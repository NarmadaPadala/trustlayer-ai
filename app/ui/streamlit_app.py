"""Streamlit interface for TrustLayer AI."""

from __future__ import annotations

import sys
from typing import Optional
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.graph.workflow import stream_review_workflow
from app.models.state import ReviewState
from app.utils.logging_config import configure_logging
from app.utils.validation import validate_review_input


configure_logging()

RISK_COLORS = {
    "Low": "#15803d",
    "Medium": "#b45309",
    "High": "#b91c1c",
    "Critical": "#7f1d1d",
}

SEVERITY_ORDER = {
    "Critical": 0,
    "High": 1,
    "Medium": 2,
    "Low": 3,
}


def apply_page_styles() -> None:
    """Keep the Streamlit UI clean and review-tool focused."""

    st.markdown(
        """
        <style>
        .main .block-container {
            max-width: 1100px;
            padding-top: 2rem;
        }
        .risk-badge {
            display: inline-flex;
            align-items: center;
            border-radius: 6px;
            color: white;
            font-weight: 700;
            padding: 0.35rem 0.65rem;
        }
        .status-row {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 0.75rem 0.9rem;
            margin-bottom: 0.5rem;
            background: #ffffff;
        }
        .human-review {
            border-left: 5px solid #b91c1c;
            background: #fef2f2;
            padding: 1rem;
            border-radius: 6px;
        }
        .summary-metric {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 0.85rem 1rem;
            background: #ffffff;
            min-height: 86px;
        }
        .summary-label {
            color: #6b7280;
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .summary-value {
            color: #111827;
            font-size: 1.35rem;
            font-weight: 750;
            margin-top: 0.25rem;
        }
        .deployment-banner {
            border-left: 5px solid #2563eb;
            background: #eff6ff;
            padding: 1rem;
            border-radius: 6px;
            margin-top: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def read_uploaded_file(uploaded_file) -> tuple[str, str, int]:
    """Decode uploaded Python file content."""

    raw_bytes = uploaded_file.getvalue()
    return uploaded_file.name, raw_bytes.decode("utf-8", errors="replace"), len(raw_bytes)


def risk_badge(risk_score: str) -> None:
    """Render a compact risk badge."""

    color = RISK_COLORS.get(risk_score, "#374151")
    st.markdown(
        f'<span class="risk-badge" style="background:{color};">{risk_score}</span>',
        unsafe_allow_html=True,
    )


def render_progress(completed_agents: list[str], active_node: Optional[str] = None) -> None:
    """Render agent execution status."""

    agent_labels = [
        ("Security Review Agent", "Security Review"),
        ("Reliability Review Agent", "Reliability Review"),
        ("Test Coverage Review Agent", "Test Coverage Review"),
    ]
    active_map = {
        "security_review": "Security Review Agent",
        "reliability_review": "Reliability Review Agent",
        "test_coverage_review": "Test Coverage Review Agent",
    }
    active_agent = active_map.get(active_node or "")

    for agent_key, label in agent_labels:
        if agent_key in completed_agents:
            status = "Completed"
        elif active_agent == agent_key:
            status = "Running"
        else:
            status = "Pending"
        st.markdown(
            f'<div class="status-row"><strong>{label}</strong><br>Status: {status}</div>',
            unsafe_allow_html=True,
        )


def findings_dataframe(review_state: ReviewState) -> pd.DataFrame:
    """Convert findings to the required report table columns."""

    sorted_findings = sorted(
        review_state.findings,
        key=lambda finding: SEVERITY_ORDER.get(finding.severity, 99),
    )
    return pd.DataFrame(
        [
            {
                "Agent": finding.agent,
                "Severity": finding.severity,
                "Finding": finding.finding,
                "Recommendation": finding.recommendation,
            }
            for finding in sorted_findings
        ]
    )


def render_review_summary(review_state: ReviewState) -> None:
    """Render a concise professional review summary."""

    completed_count = len(review_state.completed_agents)
    human_review = "Required" if review_state.human_review_required else "Not Required"
    columns = st.columns(4)
    metrics = [
        ("Risk Score", review_state.overall_risk_score),
        ("Human Review", human_review),
        ("Findings", str(len(review_state.findings))),
        ("Agents Completed", f"{completed_count}/3"),
    ]

    for column, (label, value) in zip(columns, metrics):
        with column:
            st.markdown(
                f"""
                <div class="summary-metric">
                    <div class="summary-label">{label}</div>
                    <div class="summary-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def deployment_recommendation(review_state: ReviewState) -> str:
    """Return a clear deployment recommendation."""

    if review_state.overall_risk_score == "Critical":
        return "Do not deploy until Critical findings are resolved and reviewed by a human approver."
    if review_state.overall_risk_score == "High":
        return "Delay deployment until High findings are fixed or explicitly accepted by the team."
    if review_state.overall_risk_score == "Medium":
        return "Proceed only after reviewing Medium findings and creating remediation follow-ups."
    return "Proceed with normal review and monitoring practices."


def deployment_status(review_state: ReviewState) -> str:
    """Return a concise deployment status for the review header."""

    if review_state.overall_risk_score == "Critical":
        return "Blocked"
    if review_state.overall_risk_score == "High":
        return "Needs Fixes"
    if review_state.overall_risk_score == "Medium":
        return "Review Needed"
    return "Ready for Review"


def render_report(review_state: ReviewState) -> None:
    """Render final review report."""

    st.header("Deployment Review Report")

    render_review_summary(review_state)

    st.markdown(
        f"""
        <div class="deployment-banner">
            <strong>Deployment Status: {deployment_status(review_state)}</strong><br>
            {deployment_recommendation(review_state)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if review_state.human_review_required:
        st.markdown(
            """
            <div class="human-review">
            <strong>Human Review Required</strong><br>
            Critical findings were detected. A human approver should review remediation
            before this code moves toward deployment.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("1. Executive Summary")
    st.markdown(review_state.report_markdown.split("## Overall Risk Score")[0].replace("## Executive Summary", "").strip())

    st.subheader("2. Overall Risk Score")
    risk_badge(review_state.overall_risk_score)

    st.subheader("3. Findings Table")
    if review_state.findings:
        st.dataframe(findings_dataframe(review_state), use_container_width=True, hide_index=True)
    else:
        st.success("No actionable findings were generated for this review scope.")

    st.subheader("4. Human Review Status")
    st.write("Human Review Required: Yes" if review_state.human_review_required else "Human Review Required: No")
    if not review_state.human_review_required:
        st.info("No Critical findings were detected by the configured review agents.")

    st.subheader("5. Recommended Next Steps")
    for step in review_state.report_markdown.split("## Recommended Next Steps")[-1].strip().splitlines():
        if step.strip():
            st.markdown(step)

    if review_state.errors:
        st.warning("One or more agents needed fallback handling. Review the workflow state for details.")

    with st.expander("Audit Trace"):
        trace = review_state.model_dump(exclude={"source_code", "report_markdown"})
        st.json(trace)


def main() -> None:
    """Run the Streamlit application."""

    st.set_page_config(page_title="TrustLayer AI", page_icon="TL", layout="wide")
    apply_page_styles()

    st.title("TrustLayer AI")
    st.caption("Pre-deployment risk review for AI-generated and human-written Python code.")

    st.header("Submit Code for Review")
    uploaded_file = st.file_uploader("Upload a Python (.py) file")

    st.caption("OR")
    pasted_code = st.text_area("Paste source code", height=260, placeholder="Paste Python code here...")

    analyze_clicked = st.button("Run Review", type="primary", use_container_width=False)

    if not analyze_clicked:
        return

    file_name = "pasted_code.py"
    source_code = pasted_code
    file_size = None

    if uploaded_file is not None:
        file_name, source_code, file_size = read_uploaded_file(uploaded_file)
    elif pasted_code.strip():
        file_name = "pasted_code.py"

    validation = validate_review_input(source_code, file_name, file_size)
    if not validation.is_valid:
        st.error("Please fix the input before running TrustLayer AI.")
        for error in validation.errors:
            st.write(f"- {error}")
        return

    review_state = ReviewState(
        file_name=validation.file_name,
        source_code=validation.source_code,
    )

    st.header("Agent Execution Summary")
    completion_message_placeholder = st.empty()
    progress_placeholder = st.empty()
    final_state = review_state

    with st.spinner("TrustLayer AI is reviewing the code..."):
        try:
            for node_name, updated_state in stream_review_workflow(review_state):
                final_state = updated_state
                with progress_placeholder.container():
                    render_progress(final_state.completed_agents, node_name)
        except Exception as exc:
            st.error("TrustLayer AI could not complete the review. Please check the input and try again.")
            st.caption(f"Failure detail: {type(exc).__name__}")
            return

    with completion_message_placeholder.container():
        if final_state.human_review_required:
            st.warning("Review completed. Critical findings require human approval before deployment.")
        else:
            st.success("Review completed. No Critical findings detected.")
    render_report(final_state)


if __name__ == "__main__":
    main()
