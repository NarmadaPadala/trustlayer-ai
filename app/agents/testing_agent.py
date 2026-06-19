"""Test Coverage Review Agent."""

from __future__ import annotations

import re

from app.agents.base import run_review_agent
from app.models.state import ReviewFinding
from app.utils.prompts import TESTING_SYSTEM_PROMPT


AGENT_NAME = "Test Coverage Review Agent"


def testing_heuristics(source_code: str) -> list[ReviewFinding]:
    """Recommend test coverage improvements without requiring an LLM."""

    findings: list[ReviewFinding] = []
    function_count = len(re.findall(r"^def\s+\w+\(", source_code, flags=re.MULTILINE))
    has_tests = bool(re.search(r"def\s+test_|pytest|unittest", source_code))

    if function_count and not has_tests:
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Medium",
                finding="Application logic is present but no tests are included in the submitted file.",
                recommendation="Add unit tests for core functions and keep tests in a separate tests/ folder.",
            )
        )

        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Low",
                finding="User acceptance testing scenarios are not visible.",
                recommendation="Document UAT scenarios for the main user workflow, expected results, and approval criteria.",
            )
        )

    if re.search(r"requests\.|sqlite3|psycopg|sqlalchemy|openai|boto3", source_code, re.I):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Medium",
                finding="Code interacts with external systems but lacks visible integration tests.",
                recommendation="Add integration tests with mocked services and one controlled end-to-end path.",
            )
        )

    if re.search(r"if\s+not|raise\s+ValueError|except", source_code) and not has_tests:
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Low",
                finding="Edge and negative scenarios are not covered by visible tests.",
                recommendation="Add tests for empty inputs, malformed values, and expected failure paths.",
            )
        )

    if re.search(r"login|auth|upload|payment|delete|admin", source_code, re.I) and not has_tests:
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Medium",
                finding="High-risk workflow code lacks negative test coverage.",
                recommendation="Add negative tests for unauthorized access, invalid uploads, bad inputs, and failure paths.",
            )
        )

    if re.search(r"streamlit|st\.", source_code, re.I):
        findings.append(
            ReviewFinding(
                agent=AGENT_NAME,
                severity="Low",
                finding="UI code may need accessibility, browser compatibility, and user acceptance testing.",
                recommendation=(
                    "Validate keyboard navigation, screen-reader labels, responsive layout, and browser behavior."
                ),
            )
        )

    return findings


def review_testing(file_name: str, source_code: str) -> list[ReviewFinding]:
    """Run the Test Coverage Review Agent."""

    return run_review_agent(
        agent_name=AGENT_NAME,
        system_prompt=TESTING_SYSTEM_PROMPT,
        file_name=file_name,
        source_code=source_code,
        heuristic_checks=testing_heuristics,
    )
