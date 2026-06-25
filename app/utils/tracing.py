"""LangSmith tracing helpers for TrustLayer AI."""

from __future__ import annotations

import hashlib
import os
from typing import Any

from app.models.state import ReviewFinding, ReviewState


def _should_log_source_code() -> bool:
    """Return whether full source code should be included in trace inputs."""

    return os.getenv("TRUSTLAYER_TRACE_SOURCE_CODE", "false").lower() == "true"


def summarize_source(source_code: str) -> dict[str, Any]:
    """Create an observability-safe source-code summary for traces."""

    summary: dict[str, Any] = {
        "source_chars": len(source_code),
        "source_lines": len(source_code.splitlines()),
        "source_sha256": hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
    }
    if _should_log_source_code():
        summary["source_code"] = source_code
    else:
        summary["source_preview"] = source_code[:500]
    return summary


def summarize_review_state(review_state: ReviewState) -> dict[str, Any]:
    """Summarize ReviewState for trace inputs or outputs."""

    severity_counts: dict[str, int] = {}
    agent_counts: dict[str, int] = {}
    for finding in review_state.findings:
        severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
        agent_counts[finding.agent] = agent_counts.get(finding.agent, 0) + 1

    return {
        "file_name": review_state.file_name,
        **summarize_source(review_state.source_code),
        "completed_agents": review_state.completed_agents,
        "finding_count": len(review_state.findings),
        "severity_counts": severity_counts,
        "agent_counts": agent_counts,
        "overall_risk_score": review_state.overall_risk_score,
        "human_review_required": review_state.human_review_required,
        "execution_status": review_state.execution_status,
        "error_count": len(review_state.errors),
    }


def summarize_findings(findings: list[ReviewFinding]) -> dict[str, Any]:
    """Summarize review findings for trace outputs."""

    severity_counts: dict[str, int] = {}
    for finding in findings:
        severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1

    return {
        "finding_count": len(findings),
        "severity_counts": severity_counts,
        "findings": [finding.model_dump() for finding in findings],
    }


def workflow_trace_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    """Process workflow function inputs before logging to LangSmith."""

    review_state = inputs.get("review_state")
    if review_state is None and isinstance(inputs.get("state"), dict):
        review_state = inputs["state"].get("review_state")
    if isinstance(review_state, ReviewState):
        return summarize_review_state(review_state)
    return inputs


def workflow_trace_outputs(output: Any) -> dict[str, Any]:
    """Process workflow function outputs before logging to LangSmith."""

    if isinstance(output, ReviewState):
        return summarize_review_state(output)
    if isinstance(output, dict) and isinstance(output.get("review_state"), ReviewState):
        return summarize_review_state(output["review_state"])
    return {"output": str(output)}


def agent_trace_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    """Process agent-node inputs before logging to LangSmith."""

    state = inputs.get("state", {})
    review_state = state.get("review_state") if isinstance(state, dict) else None
    agent_key = inputs.get("agent_key", "unknown")
    if isinstance(review_state, ReviewState):
        return {
            "agent": agent_key,
            "file_name": review_state.file_name,
            **summarize_source(review_state.source_code),
        }
    return {"agent": agent_key}


def agent_trace_outputs(output: Any) -> dict[str, Any]:
    """Process agent-node outputs before logging to LangSmith."""

    if isinstance(output, dict) and isinstance(output.get("review_state"), ReviewState):
        return summarize_review_state(output["review_state"])
    return {"output": str(output)}


def findings_trace_outputs(output: Any) -> dict[str, Any]:
    """Process direct agent outputs before logging to LangSmith."""

    if isinstance(output, list) and all(isinstance(item, ReviewFinding) for item in output):
        return summarize_findings(output)
    return {"output": str(output)}


def review_agent_trace_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    """Process direct agent inputs before logging to LangSmith."""

    source_code = inputs.get("source_code", "")
    trace_inputs = {
        "agent": inputs.get("agent_name", "unknown"),
        "file_name": inputs.get("file_name", "unknown"),
    }
    if isinstance(source_code, str):
        trace_inputs.update(summarize_source(source_code))
    return trace_inputs
