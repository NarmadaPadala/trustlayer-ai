"""Risk scoring and human-review rules."""

from __future__ import annotations

from app.models.state import ReviewFinding, RiskScore


def calculate_overall_risk(findings: list[ReviewFinding]) -> RiskScore:
    """Compute an explainable overall risk from individual findings."""

    if not findings:
        return "Low"

    severities = [finding.severity for finding in findings]
    if "Critical" in severities:
        return "Critical"
    if "High" in severities:
        return "High"
    if severities.count("Medium") >= 3:
        return "High"
    if "Medium" in severities:
        return "Medium"
    return "Low"


def requires_human_review(findings: list[ReviewFinding]) -> bool:
    """Human approval is required when any finding is Critical."""

    return any(finding.severity == "Critical" for finding in findings)
