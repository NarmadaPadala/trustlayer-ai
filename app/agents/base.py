"""Shared agent execution helpers."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from typing import Optional

from pydantic import ValidationError

from app.models.state import AgentReview, ReviewFinding
from app.utils.config import get_config
from app.utils.prompts import USER_REVIEW_PROMPT

logger = logging.getLogger(__name__)


HeuristicCheck = Callable[[str], list[ReviewFinding]]


def find_line(source_code: str, pattern: str) -> Optional[str]:
    """Return a human-readable line number for a regex match."""

    for index, line in enumerate(source_code.splitlines(), start=1):
        if re.search(pattern, line, flags=re.IGNORECASE):
            return f"Line {index}"
    return None


def run_review_agent(
    *,
    agent_name: str,
    system_prompt: str,
    file_name: str,
    source_code: str,
    heuristic_checks: HeuristicCheck,
) -> list[ReviewFinding]:
    """Run deterministic checks plus an optional LLM review."""

    config = get_config()
    findings = heuristic_checks(source_code)

    if not config.openai_api_key:
        logger.info("%s using deterministic review because OPENAI_API_KEY is absent.", agent_name)
        return findings

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", USER_REVIEW_PROMPT),
        ]
    )
    model = ChatOpenAI(
        model=config.model_name,
        temperature=0,
        max_retries=config.agent_retry_attempts,
    )
    structured_model = model.with_structured_output(AgentReview)
    chain = prompt | structured_model

    try:
        llm_review = chain.invoke(
            {
                "file_name": file_name,
                "source_code": source_code,
            }
        )
    except (ValidationError, Exception) as exc:
        logger.exception("%s failed during LLM review.", agent_name)
        findings.append(
            ReviewFinding(
                agent=agent_name,
                severity="Medium",
                finding=f"{agent_name} could not complete the LLM review.",
                recommendation=(
                    "Review model configuration, API availability, and logs. "
                    f"Failure detail: {type(exc).__name__}."
                ),
            )
        )
        return findings

    llm_findings = [
        finding.model_copy(update={"agent": agent_name})
        for finding in llm_review.findings
    ]
    return merge_findings(findings, llm_findings)


def merge_findings(
    deterministic_findings: list[ReviewFinding],
    llm_findings: list[ReviewFinding],
) -> list[ReviewFinding]:
    """Merge findings while avoiding exact duplicates."""

    merged: list[ReviewFinding] = []
    seen: set[tuple[str, str, str]] = set()
    for finding in [*deterministic_findings, *llm_findings]:
        key = (finding.agent, finding.severity, finding.finding.lower().strip())
        if key in seen:
            continue
        seen.add(key)
        merged.append(finding)
    return merged
