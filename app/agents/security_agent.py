"""Security Review Agent."""

from __future__ import annotations

import re

from app.agents.base import find_line, run_review_agent
from app.models.state import ReviewFinding
from app.utils.prompts import SECURITY_SYSTEM_PROMPT


AGENT_NAME = "Security Review Agent"


def security_heuristics(source_code: str) -> list[ReviewFinding]:
    """Catch common security risks without requiring an LLM."""

    findings: list[ReviewFinding] = []
    secret_patterns = [
        r"api[_-]?key\s*=\s*['\"][^'\"]{8,}",
        r"secret\s*=\s*['\"][^'\"]{8,}",
        r"password\s*=\s*['\"][^'\"]{6,}",
        r"token\s*=\s*['\"][^'\"]{8,}",
        r"bearer\s+[a-z0-9._\-]{12,}",
        r"sk-[a-z0-9]{12,}",
    ]
    if any(re.search(pattern, source_code, flags=re.IGNORECASE) for pattern in secret_patterns):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Critical",
                finding="Possible hardcoded secret or credential detected.",
                recommendation=(
                    "Move secrets to environment variables or a managed secret store, "
                    "rotate exposed credentials, and add secret scanning to CI."
                ),
                line_reference=find_line(source_code, "|".join(secret_patterns)),
            )
        )

    dynamic_sql_patterns = [
        r"\.execute\(.+f['\"]",
        r"\.execute\(.+\+",
        r"\bquery\s*=\s*f['\"].*(select|insert|update|delete)",
        r"\bquery\s*=.+\+.+(select|insert|update|delete)",
    ]
    if any(re.search(pattern, source_code, flags=re.IGNORECASE | re.DOTALL) for pattern in dynamic_sql_patterns):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="High",
                finding="Potential SQL injection risk from dynamic query construction.",
                recommendation="Use parameterized queries and validate all user-controlled inputs.",
                line_reference=find_line(source_code, r"\.execute|\bquery\s*="),
            )
        )

    if re.search(r"\beval\(|\bexec\(", source_code):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Critical",
                finding="Dynamic code execution is present.",
                recommendation="Remove eval/exec or replace with a constrained parser or allowlist.",
                line_reference=find_line(source_code, r"\beval\(|\bexec\("),
            )
        )

    obfuscated_eval_patterns = [
        r"getattr\(__builtins__,\s*['\"]eval['\"]",
        r"getattr\(__builtins__,\s*\w+\)\(",
        r"['\"]ev['\"]\s*\+\s*['\"]al['\"]",
    ]
    if any(re.search(pattern, source_code, flags=re.IGNORECASE) for pattern in obfuscated_eval_patterns):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Critical",
                finding="Obfuscated dynamic code execution may be present.",
                recommendation=(
                    "Remove obfuscated access to eval/exec-style behavior and replace it with explicit, "
                    "allowlisted operations."
                ),
                line_reference=find_line(source_code, r"getattr\(__builtins__|['\"]ev['\"]\s*\+"),
            )
        )

    if re.search(r"pickle\.loads?\(", source_code, flags=re.IGNORECASE):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Critical",
                finding="Unsafe deserialization with pickle is present.",
                recommendation=(
                    "Do not deserialize untrusted data with pickle. Use a safe format such as JSON "
                    "with schema validation, or strictly authenticate and isolate trusted serialized data."
                ),
                line_reference=find_line(source_code, r"pickle\.loads?\("),
            )
        )

    if re.search(r"yaml\.load\(", source_code, flags=re.IGNORECASE) and not re.search(
        r"SafeLoader|safe_load", source_code, flags=re.IGNORECASE
    ):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="High",
                finding="Unsafe YAML loading may allow deserialization attacks.",
                recommendation="Use yaml.safe_load or yaml.load with SafeLoader for untrusted YAML input.",
                line_reference=find_line(source_code, r"yaml\.load\("),
            )
        )

    if re.search(r"subprocess\.(run|call|Popen)\(.+shell\s*=\s*True", source_code, flags=re.IGNORECASE | re.DOTALL):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Critical",
                finding="Shell command execution with shell=True may allow command injection.",
                recommendation=(
                    "Use shell=False with an argument list, avoid string-concatenated commands, "
                    "and validate user-controlled command arguments with an allowlist."
                ),
                line_reference=find_line(source_code, r"subprocess\.(run|call|Popen)\("),
            )
        )

    if re.search(r"random\.(random|randint|choice|choices|randrange)\(", source_code) and re.search(
        r"token|password|reset|secret|auth", source_code, flags=re.IGNORECASE
    ):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="High",
                finding="Weak random source used for security-sensitive token generation.",
                recommendation="Use the secrets module, such as secrets.token_urlsafe, for security-sensitive tokens.",
                line_reference=find_line(source_code, r"random\.(random|randint|choice|choices|randrange)\("),
            )
        )

    if re.search(r"['\"]/tmp/[^'\"]*[{]|['\"]/tmp/[^'\"]*['\"]\s*\+", source_code):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Medium",
                finding="Predictable temporary file path may allow insecure file access or collisions.",
                recommendation=(
                    "Use tempfile.NamedTemporaryFile or tempfile.TemporaryDirectory with safe permissions "
                    "instead of predictable paths in /tmp."
                ),
                line_reference=find_line(source_code, r"/tmp/"),
            )
        )

    if re.search(r"send_file\(.+\+|open\(.+\+|Path\(.+\)|os\.path\.join\(", source_code, flags=re.IGNORECASE | re.DOTALL) and re.search(
        r"request\.args|get\(|filename|file|path", source_code, flags=re.IGNORECASE
    ) and not re.search(r"resolve\(\)|safe_join|basename|is_relative_to|allowlist", source_code, flags=re.IGNORECASE):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="High",
                finding="Potential path traversal risk from user-controlled file path construction.",
                recommendation=(
                    "Resolve paths against an allowlisted base directory, reject traversal segments, "
                    "and use safe path utilities before reading or sending files."
                ),
                line_reference=find_line(source_code, r"send_file|open\(|Path\(|os\.path\.join"),
            )
        )

    if re.search(r"open\(.+upload|UploadedFile|file_uploader", source_code, flags=re.IGNORECASE):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Medium",
                finding="File upload or file handling code may need stricter validation.",
                recommendation=(
                    "Validate file extension, MIME type, size, path handling, and storage location."
                ),
                line_reference=find_line(source_code, r"upload|file_uploader|UploadedFile"),
            )
        )

    if re.search(r"auth|login|password|session|jwt", source_code, flags=re.IGNORECASE):
        if not re.search(r"hash|bcrypt|argon2|verify|expires|httponly|secure", source_code, flags=re.IGNORECASE):
            findings.append(
                ReviewFinding(
                    agent=AGENT_NAME,
                    severity="Medium",
                    finding="Authentication-related code may be missing explicit security controls.",
                    recommendation=(
                        "Verify password hashing, session expiration, secure cookies, and authorization checks."
                    ),
                    line_reference=find_line(source_code, r"auth|login|password|session|jwt"),
                )
            )

    if re.search(r"print\(.+(password|secret|token|api[_-]?key)|logging\..+(password|secret|token|api[_-]?key)", source_code, flags=re.IGNORECASE):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="High",
                finding="Sensitive data may be exposed through logs or console output.",
                recommendation="Avoid logging secrets, tokens, passwords, or personally sensitive data.",
                line_reference=find_line(source_code, r"print|logging\."),
            )
        )

    return findings


def review_security(file_name: str, source_code: str) -> list[ReviewFinding]:
    """Run the Security Review Agent."""

    return run_review_agent(
        agent_name=AGENT_NAME,
        system_prompt=SECURITY_SYSTEM_PROMPT,
        file_name=file_name,
        source_code=source_code,
        heuristic_checks=security_heuristics,
    )
