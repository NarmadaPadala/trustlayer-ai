"""Structured review state for the TrustLayer AI workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


Severity = Literal["Low", "Medium", "High", "Critical"]
RiskScore = Literal["Low", "Medium", "High", "Critical"]
ExecutionStatus = Literal["pending", "running", "completed", "failed"]


class ReviewFinding(BaseModel):
    """One actionable code review finding."""

    agent: str
    severity: Severity
    finding: str
    recommendation: str
    line_reference: Optional[str] = None


class ReviewState(BaseModel):
    """Workflow state shared by the orchestrator and all review agents."""

    file_name: str
    source_code: str
    completed_agents: list[str] = Field(default_factory=list)
    findings: list[ReviewFinding] = Field(default_factory=list)
    overall_risk_score: RiskScore = "Low"
    human_review_required: bool = False
    execution_status: ExecutionStatus = "pending"
    timestamps: dict[str, str] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    report_markdown: str = ""

    def mark_timestamp(self, event_name: str) -> None:
        """Record a UTC timestamp for a workflow event."""

        self.timestamps[event_name] = datetime.now(timezone.utc).isoformat()


class AgentReview(BaseModel):
    """Structured LLM response expected from each specialist agent."""

    findings: list[ReviewFinding] = Field(default_factory=list)
