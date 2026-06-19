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
