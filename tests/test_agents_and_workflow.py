from pathlib import Path

from app.agents.security_agent import security_heuristics
from app.graph.workflow import run_review_workflow
from app.models.state import ReviewState


def test_security_detects_dynamic_query_variable():
    code = """
def find_user(email, conn):
    query = f"SELECT * FROM users WHERE email = '{email}'"
    return conn.execute(query).fetchall()
"""

    findings = security_heuristics(code)

    assert any("SQL injection" in finding.finding for finding in findings)


def test_workflow_flags_human_review_for_vulnerable_sample(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    source_code = Path("sample_files/vulnerable_app.py").read_text()

    state = run_review_workflow(
        ReviewState(file_name="vulnerable_app.py", source_code=source_code)
    )

    assert state.execution_status == "completed"
    assert state.overall_risk_score == "Critical"
    assert state.human_review_required
    assert len(state.completed_agents) == 3

