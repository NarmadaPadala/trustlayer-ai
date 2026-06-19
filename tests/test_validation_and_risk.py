from app.models.state import ReviewFinding
from app.utils.risk import calculate_overall_risk, requires_human_review
from app.utils.validation import validate_review_input


def test_validation_rejects_empty_code():
    result = validate_review_input("", "example.py")

    assert not result.is_valid
    assert "Source code cannot be empty." in result.errors


def test_validation_rejects_non_python_file():
    result = validate_review_input("print('hello')", "example.txt")

    assert not result.is_valid
    assert "Only Python .py files are supported." in result.errors


def test_validation_rejects_oversized_file():
    result = validate_review_input("print('hello')", "example.py", file_size_bytes=999_999)

    assert not result.is_valid
    assert "File is too large. Limit is 200 KB." in result.errors


def test_validation_accepts_uppercase_python_extension():
    result = validate_review_input("print('hello')", "EXAMPLE.PY")

    assert result.is_valid


def test_validation_rejects_binary_like_content():
    result = validate_review_input("print('hello')\x00", "example.py")

    assert not result.is_valid
    assert "Source code appears to contain binary data and cannot be reviewed." in result.errors


def test_critical_finding_sets_critical_risk_and_human_review():
    findings = [
        ReviewFinding(
            agent="Security Review Agent",
            severity="Critical",
            finding="Hardcoded secret detected.",
            recommendation="Rotate the secret and move it to a secret manager.",
        )
    ]

    assert calculate_overall_risk(findings) == "Critical"
    assert requires_human_review(findings)


def test_multiple_medium_findings_raise_high_risk():
    findings = [
        ReviewFinding(
            agent="Reliability Review Agent",
            severity="Medium",
            finding=f"Reliability issue {index}.",
            recommendation="Add validation.",
        )
        for index in range(3)
    ]

    assert calculate_overall_risk(findings) == "High"
