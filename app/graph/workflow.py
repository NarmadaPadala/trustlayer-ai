"""LangGraph workflow for TrustLayer AI."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from app.agents.reliability_agent import review_reliability
from app.agents.security_agent import review_security
from app.agents.testing_agent import review_testing
from app.models.state import ReviewFinding, ReviewState
from app.utils.config import get_config
from app.utils.risk import calculate_overall_risk, requires_human_review

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """LangGraph-compatible state container."""

    review_state: ReviewState


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def orchestrator_node(state: GraphState) -> GraphState:
    """Initialize workflow execution."""

    review_state = state["review_state"]
    review_state.execution_status = "running"
    review_state.timestamps["orchestrator_started"] = _now()
    return {"review_state": review_state}


def _run_agent_node(
    state: GraphState,
    *,
    agent_key: str,
    agent_runner: Any,
) -> GraphState:
    """Run one specialist agent and keep the workflow alive on failure."""

    review_state = state["review_state"]
    review_state.timestamps[f"{agent_key}_started"] = _now()
    attempts = max(1, get_config().agent_retry_attempts)

    for attempt in range(1, attempts + 1):
        try:
            findings: list[ReviewFinding] = agent_runner(
                review_state.file_name,
                review_state.source_code,
            )
            review_state.findings.extend(findings)
            review_state.completed_agents.append(agent_key)
            review_state.timestamps[f"{agent_key}_completed"] = _now()
            return {"review_state": review_state}
        except Exception as exc:
            logger.exception(
                "%s failed unexpectedly on attempt %s of %s.",
                agent_key,
                attempt,
                attempts,
            )
            if attempt == attempts:
                review_state.errors.append(f"{agent_key} failed after {attempts} attempt(s): {type(exc).__name__}")
                review_state.findings.append(
                    ReviewFinding(
                        agent=agent_key,
                        severity="Medium",
                        finding=f"{agent_key} did not complete successfully.",
                        recommendation=(
                            "Use deterministic findings from the other agents, check application logs, "
                            "and re-run the review after resolving the agent failure."
                        ),
                    )
                )
                review_state.timestamps[f"{agent_key}_failed"] = _now()

    return {"review_state": review_state}


def security_node(state: GraphState) -> GraphState:
    """Run the Security Review Agent."""

    return _run_agent_node(
        state,
        agent_key="Security Review Agent",
        agent_runner=review_security,
    )


def reliability_node(state: GraphState) -> GraphState:
    """Run the Reliability Review Agent."""

    return _run_agent_node(
        state,
        agent_key="Reliability Review Agent",
        agent_runner=review_reliability,
    )


def testing_node(state: GraphState) -> GraphState:
    """Run the Test Coverage Review Agent."""

    return _run_agent_node(
        state,
        agent_key="Test Coverage Review Agent",
        agent_runner=review_testing,
    )


def aggregate_node(state: GraphState) -> GraphState:
    """Aggregate findings and compute overall risk."""

    review_state = state["review_state"]
    review_state.overall_risk_score = calculate_overall_risk(review_state.findings)
    review_state.human_review_required = requires_human_review(review_state.findings)
    review_state.timestamps["findings_aggregated"] = _now()
    return {"review_state": review_state}


def report_node(state: GraphState) -> GraphState:
    """Generate the final markdown report."""

    review_state = state["review_state"]
    finding_count = len(review_state.findings)
    critical_count = sum(1 for finding in review_state.findings if finding.severity == "Critical")
    high_count = sum(1 for finding in review_state.findings if finding.severity == "High")

    if finding_count:
        summary = (
            f"TrustLayer AI reviewed `{review_state.file_name}` and found "
            f"{finding_count} issue(s), including {critical_count} critical "
            f"and {high_count} high-severity finding(s)."
        )
    else:
        summary = (
            f"TrustLayer AI reviewed `{review_state.file_name}` and found no "
            "actionable issues in the configured review scope."
        )

    next_steps = build_next_steps(review_state)
    human_review_text = "Yes" if review_state.human_review_required else "No"
    human_review_reason = (
        "A Critical finding was detected, so human approval is recommended before deployment."
        if review_state.human_review_required
        else "No Critical findings were detected by the configured review agents."
    )
    review_state.report_markdown = "\n\n".join(
        [
            "## Executive Summary",
            summary,
            "## Overall Risk Score",
            review_state.overall_risk_score,
            "## Findings Table",
            "See the structured findings table in the UI.",
            "## Human Review Status",
            f"Human Review Required: {human_review_text}",
            human_review_reason,
            "## Recommended Next Steps",
            "\n".join(f"- {step}" for step in next_steps),
        ]
    )
    review_state.timestamps["report_generated"] = _now()
    return {"review_state": review_state}


def human_review_node(state: GraphState) -> GraphState:
    """Finalize human-in-the-loop status."""

    review_state = state["review_state"]
    review_state.execution_status = "completed"
    review_state.timestamps["workflow_completed"] = _now()
    return {"review_state": review_state}


def build_next_steps(review_state: ReviewState) -> list[str]:
    """Generate practical next steps from risk posture."""

    steps = [
        "Address Critical and High findings before deployment.",
        "Add or update tests for the recommended edge and failure paths.",
        "Re-run TrustLayer AI after changes to confirm the risk score improves.",
    ]
    if review_state.human_review_required:
        steps.insert(
            0,
            "Route this review to a human approver because at least one Critical issue was found.",
        )
    if review_state.errors:
        steps.append("Review agent execution errors in the application logs.")
    return steps


def build_review_graph():
    """Compile the LangGraph review workflow."""

    workflow = StateGraph(GraphState)
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("security_review", security_node)
    workflow.add_node("reliability_review", reliability_node)
    workflow.add_node("test_coverage_review", testing_node)
    workflow.add_node("aggregate_findings", aggregate_node)
    workflow.add_node("generate_report", report_node)
    workflow.add_node("human_review_check", human_review_node)

    workflow.set_entry_point("orchestrator")
    workflow.add_edge("orchestrator", "security_review")
    workflow.add_edge("security_review", "reliability_review")
    workflow.add_edge("reliability_review", "test_coverage_review")
    workflow.add_edge("test_coverage_review", "aggregate_findings")
    workflow.add_edge("aggregate_findings", "generate_report")
    workflow.add_edge("generate_report", "human_review_check")
    workflow.add_edge("human_review_check", END)
    return workflow.compile()


def run_review_workflow(review_state: ReviewState) -> ReviewState:
    """Run the full review workflow and return final state."""

    graph = build_review_graph()
    result = graph.invoke({"review_state": review_state})
    return result["review_state"]


def stream_review_workflow(review_state: ReviewState):
    """Yield workflow updates for progress-aware UIs."""

    graph = build_review_graph()
    latest_state = review_state
    for update in graph.stream({"review_state": review_state}):
        node_name, payload = next(iter(update.items()))
        latest_state = payload["review_state"]
        yield node_name, latest_state
