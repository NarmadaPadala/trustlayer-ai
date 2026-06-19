"""Reliability Review Agent."""

from __future__ import annotations

import re

from app.agents.base import find_line, run_review_agent
from app.models.state import ReviewFinding
from app.utils.prompts import RELIABILITY_SYSTEM_PROMPT


AGENT_NAME = "Reliability Review Agent"


def reliability_heuristics(source_code: str) -> list[ReviewFinding]:
    """Catch reliability risks without requiring an LLM."""

    findings: list[ReviewFinding] = []

    if "requests." in source_code and "timeout=" not in source_code:
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="High",
                finding="External HTTP request appears to be missing a timeout.",
                recommendation="Set explicit timeouts and handle timeout exceptions.",
                line_reference=find_line(source_code, r"requests\."),
            )
        )

    if "requests." in source_code and not re.search(r"retry|backoff|tenacity", source_code, re.I):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Medium",
                finding="External dependency call does not appear to include retries.",
                recommendation="Add bounded retries with exponential backoff for transient failures.",
                line_reference=find_line(source_code, r"requests\."),
            )
        )

    if re.search(r"except\s*:\s*(pass)?", source_code):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="High",
                finding="Broad exception handling may hide production failures.",
                recommendation="Catch specific exceptions, log context, and return safe fallback behavior.",
                line_reference=find_line(source_code, r"except\s*:"),
            )
        )

    if re.search(r"def\s+\w+\([^)]*(input|data|file|payload)[^)]*\):", source_code, re.I):
        if not re.search(r"if\s+not\s+(input|data|file|payload)|raise\s+ValueError", source_code, re.I):
            findings.append(
                ReviewFinding(
                    agent=AGENT_NAME,
                    severity="Medium",
                    finding="Input-bearing function may be missing empty input validation.",
                    recommendation="Validate required inputs early and return clear user-facing errors.",
                )
            )

    if re.search(r"open\(|Path\(.+\)|file_uploader|UploadedFile", source_code, re.I):
        if not re.search(r"exists\(\)|is_file\(\)|suffix|extension|mime|size|stat\(\)", source_code, re.I):
            findings.append(
                ReviewFinding(
                    agent=AGENT_NAME,
                    severity="Medium",
                    finding="File handling code may be missing validation.",
                    recommendation="Validate file existence, type, size, and path safety before processing.",
                    line_reference=find_line(source_code, r"open\(|file_uploader|UploadedFile|Path\("),
                )
            )

    if re.search(r"sqlite3|psycopg|sqlalchemy|mysql|postgres|database|db\.", source_code, re.I):
        if not re.search(r"transaction|rollback|commit|IntegrityError|OperationalError|except", source_code, re.I):
            findings.append(
                ReviewFinding(
                    agent=AGENT_NAME,
                    severity="Medium",
                    finding="Database interaction may be missing validation or failure handling.",
                    recommendation="Validate database inputs and handle connection, transaction, and constraint failures.",
                    line_reference=find_line(source_code, r"sqlite3|psycopg|sqlalchemy|database|db\."),
                )
            )

    if re.search(r"\.json\(\)", source_code) and "try:" not in source_code:
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Medium",
                finding="JSON parsing appears to lack error handling.",
                recommendation="Handle malformed JSON and unexpected response schemas.",
                line_reference=find_line(source_code, r"\.json\(\)"),
            )
        )

    if re.search(r"\.get\(|\[[\"'][^\"']+[\"']\]", source_code) and not re.search(r"is None|if .+ is not None|if .+:", source_code):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Low",
                finding="Dictionary or object access may need explicit null handling.",
                recommendation="Handle missing keys and None values with predictable defaults or clear errors.",
            )
        )

    if re.search(r"random\.|datetime\.now\(|time\.time\(", source_code):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Low",
                finding="Code may include non-deterministic behavior that affects predictability.",
                recommendation="Inject clocks, random seeds, or deterministic inputs for testable production behavior.",
                line_reference=find_line(source_code, r"random\.|datetime\.now\(|time\.time\("),
            )
        )

    return findings


def review_reliability(file_name: str, source_code: str) -> list[ReviewFinding]:
    """Run the Reliability Review Agent."""

    return run_review_agent(
        agent_name=AGENT_NAME,
        system_prompt=RELIABILITY_SYSTEM_PROMPT,
        file_name=file_name,
        source_code=source_code,
        heuristic_checks=reliability_heuristics,
    )
