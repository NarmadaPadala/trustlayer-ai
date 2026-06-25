# Phase 2: Golden Dataset Documentation

## Purpose

The golden dataset defines the expected behavior for TrustLayer AI before evaluation execution begins. It gives the system a fixed set of Python code review scenarios that can be used for baseline evaluation, failure analysis, improvement planning, and final regression testing.

The dataset is intentionally designed around TrustLayer AI's current product scope:

- Security review
- Reliability review
- Test coverage review
- Agent routing
- Risk scoring
- Human-review escalation
- Production-oriented code review quality

## Dataset File

Spreadsheet-ready dataset:

```text
docs/evaluation/golden_dataset.csv
```

This CSV can be opened in Google Sheets, Excel, Numbers, or any spreadsheet tool.

## Dataset Distribution

| Category | Count | Purpose |
|---|---:|---|
| Happy Path | 20 | Clear scenarios where TrustLayer AI should detect expected security, reliability, or testing issues. |
| Edge Case | 12 | Ambiguous or partially safe scenarios that test false positives, routing judgment, and nuance. |
| Known Failure | 6 | Higher-risk scenarios that are likely to expose current system limitations. |
| Adversarial | 2 | Inputs designed to test prompt-injection resistance and obfuscated unsafe behavior. |
| Total | 40 | Full baseline evaluation set. |

## Spreadsheet Columns

| Column | Description |
|---|---|
| Case ID | Stable identifier for each evaluation case. |
| Scenario Description | Plain-language explanation of the submitted Python code scenario. |
| Code Vulnerability or Issue | The main risk or behavior being tested. |
| Expected Findings | What TrustLayer AI should report or avoid reporting. |
| Difficulty Level | Easy, Medium, or Hard. |
| Category | Happy Path, Edge Case, Known Failure, or Adversarial. |
| Expected Agent | Agent expected to own the primary finding. |
| Expected Severity | Expected severity for the primary issue. |

## Design Principles

### 1. Cover Core Product Promise

TrustLayer AI promises review across security, reliability, and test coverage. The dataset includes cases for all three specialist agents and multi-agent scenarios where more than one agent should contribute.

### 2. Test Both Detection and Restraint

A good code review system should not only find issues. It should also avoid unsupported findings. Edge cases include safe parameterized SQL, secure password hashing, environment-based secrets, and test-only files.

### 3. Include Production Risk

Known failure cases focus on real production concerns that code review systems often miss:

- Path traversal
- Unsafe deserialization
- Unsafe YAML loading
- Command injection
- Weak randomness
- Insecure temporary files

### 4. Include Adversarial Behavior

The adversarial cases test whether TrustLayer AI can ignore malicious instructions embedded inside code comments and still identify unsafe behavior.

### 5. Make Results Measurable

Each row contains expected findings, expected agent ownership, expected severity, and difficulty level. These fields support recall, precision, routing accuracy, severity accuracy, and failure clustering.

## How This Dataset Supports Phase 1 Metrics

| Phase 1 Metric | Dataset Support |
|---|---|
| Critical Finding Recall | Critical and High cases include explicit expected findings. |
| Finding Precision | Edge cases include safe or partially safe code that should not receive noisy findings. |
| Agent Routing Accuracy | Each case includes an expected agent or multiple-agent expectation. |
| Actionability Score | Expected findings describe the recommendation quality the system should provide. |
| Latency and Cost Efficiency | The fixed 40-case set creates a repeatable workload for LangSmith trace measurement. |

## Recommended Baseline Procedure

1. Convert each dataset row into a small Python snippet or file.
2. Run TrustLayer AI against all 40 cases.
3. Capture structured outputs from `ReviewState`.
4. Record LangSmith trace links for each run.
5. Score each result against the expected finding, expected agent, expected severity, and LLM-as-judge rubric.
6. Calculate baseline metrics.
7. Cluster failures by issue type and agent.
8. Prioritize improvements.
9. Re-run the same dataset after improvements.

## Expected Evaluation Value

This dataset will help demonstrate that the project uses production AI evaluation practices rather than relying only on manual demos. It gives TrustLayer AI a measurable benchmark and creates evidence for:

- AI Evaluation
- Observability
- Monitoring
- Agent reliability
- Human-in-the-loop escalation
- Production AI engineering judgment

## Phase 2 Decision

The 40-case golden dataset is the official baseline evaluation set for TrustLayer AI. Future improvements should be measured against this same dataset so metric changes are comparable across runs.
