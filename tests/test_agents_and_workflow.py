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


def test_security_detects_known_failure_classes():
    cases = [
        (
            """
from flask import request, send_file

def download_report():
    filename = request.args.get("file")
    return send_file("reports/" + filename)
""",
            "path traversal",
        ),
        (
            """
import pickle

def load_uploaded_state(uploaded_file):
    return pickle.loads(uploaded_file.read())
""",
            "pickle",
        ),
        (
            """
import yaml

def load_config(raw_config):
    return yaml.load(raw_config)
""",
            "YAML",
        ),
        (
            """
import subprocess

def ping_host(host):
    return subprocess.run("ping -c 1 " + host, shell=True)
""",
            "command injection",
        ),
        (
            """
import random

def password_reset_token(user_id):
    return str(user_id) + "-" + str(random.random())
""",
            "Weak random",
        ),
        (
            """
def write_temp_report(user_id, contents):
    path = f"/tmp/report-{user_id}.txt"
    with open(path, "w") as report:
        report.write(contents)
""",
            "temporary file",
        ),
        (
            """
def hidden_runner(payload):
    fn = "ev" + "al"
    return getattr(__builtins__, fn)(payload)
""",
            "Obfuscated dynamic code execution",
        ),
    ]

    for code, expected_text in cases:
        findings = security_heuristics(code)

        assert any(expected_text.lower() in finding.finding.lower() for finding in findings)


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
