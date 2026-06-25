# TrustLayer AI Evaluation Report

## Executive Summary

TrustLayer AI is a multi-agent Python code review system designed to identify security vulnerabilities, reliability issues, and test coverage gaps before code reaches production. This Week 4 project evaluated TrustLayer AI using AI evaluation, observability, and monitoring practices rather than building a new application.

The evaluation followed a production AI engineering loop:

```text
evaluation design -> golden dataset -> observability -> baseline run -> failure analysis -> targeted improvements -> re-evaluation
```

The first baseline showed that TrustLayer AI completed every review but missed several advanced security cases. After targeted improvements to the Security Agent, the same 40-case golden dataset produced zero failed cases and passed all primary evaluation metrics in the deterministic local evaluation runner.

## System Under Evaluation

TrustLayer AI reviews Python source code through:

- Orchestrator Agent
- Security Review Agent
- Reliability Review Agent
- Test Coverage Review Agent
- LangGraph workflow
- Pydantic `ReviewState` and `ReviewFinding` models
- Streamlit review interface
- Deterministic fallback checks
- Optional OpenAI-backed LLM review
- LangSmith tracing hooks

## User Outcome

The target user is a developer, AI engineer, or technical reviewer preparing Python code for deployment.

The intended outcome is:

> A user submits Python source code and receives a clear, prioritized review that identifies meaningful security, reliability, and test coverage risks, routes findings through the correct specialist agents, explains why each issue matters, recommends practical fixes, and flags when human review is required.

## Evaluation One-Liner

TrustLayer AI passes evaluation if it reliably detects high-impact Python code risks, assigns findings to the correct specialist agents, explains issues clearly, recommends useful remediation steps, triggers human review for critical risk, and stays within practical latency and cost limits.

## Golden Dataset

The evaluation used a 40-case golden dataset:

| Category | Count |
|---|---:|
| Happy Path | 20 |
| Edge Case | 12 |
| Known Failure | 6 |
| Adversarial | 2 |
| Total | 40 |

The dataset covers:

- SQL injection
- Hardcoded secrets
- Dynamic code execution
- Unsafe file upload and file handling
- Missing request timeouts
- Missing retries
- Broad exception handling
- Database failure handling
- JSON parsing errors
- Missing unit and integration tests
- Path traversal
- Unsafe deserialization
- Unsafe YAML loading
- Command injection
- Weak randomness
- Insecure temporary files
- Prompt-injection comments
- Obfuscated dynamic execution

Dataset artifact:

```text
docs/evaluation/golden_dataset.csv
```

## Metrics and Thresholds

| Metric | Target |
|---|---|
| Critical Finding Recall | >= 90% overall and 100% on Critical security cases |
| Finding Precision | >= 85% |
| Agent Routing Accuracy | >= 90% |
| Actionability Score | >= 8.0 |
| Latency p95 | <= 30 seconds |
| Average Cost per Review | <= $0.15 |
| Human Review Accuracy | 100% |
| Agent Completion Rate | >= 98% |
| False Positive Rate | <= 15% |

## Baseline Results Before Improvements

The first deterministic baseline run completed all 40 cases.

| Result Type | Count |
|---|---:|
| PASS | 26 |
| CONDITIONAL PASS | 7 |
| FAIL | 7 |
| Total | 40 |

The failed cases were concentrated in known security failure classes:

- Path traversal
- Unsafe `pickle.loads()` deserialization
- Unsafe `yaml.load()`
- Command injection with `shell=True`
- Weak randomness for reset tokens
- Predictable temporary file creation
- Obfuscated dynamic execution

Baseline metrics showed the main production risk:

| Metric | Baseline Result | Status |
|---|---:|---|
| Critical Finding Recall | 57.1% overall; 50.0% Critical security | FAIL |
| Agent Routing Accuracy | 85.0% | FAIL |
| Human Review Accuracy | 57.1% | FAIL |
| Agent Completion Rate | 100.0% | PASS |
| Latency p95 | 0.004 seconds | PASS |

## Failure Analysis

The top failure mode was:

```text
missed_security_issue
```

Root cause:

TrustLayer AI's initial deterministic Security Agent checks covered common issues such as SQL injection, hardcoded secrets, `eval`, and logging secrets, but did not cover several higher-risk security classes often found in production code.

Impact:

- Critical Finding Recall failed threshold.
- Human Review Accuracy failed because missed Critical findings could not trigger human review.
- Known failure and adversarial cases exposed the largest reliability gap.

## Improvements Implemented

The first improvement sprint focused on P0 security recall.

Implemented changes:

- Expanded deterministic Security Agent coverage.
- Expanded Security Agent LLM prompt coverage.
- Added prompt-injection awareness for source-code comments.
- Added regression tests for known security failure classes.

New security coverage:

- Path traversal from user-controlled file paths
- Unsafe `pickle.loads()` deserialization
- Unsafe `yaml.load()` without `SafeLoader` or `safe_load`
- `subprocess.run(..., shell=True)` command injection
- Weak randomness for security-sensitive token generation
- Predictable temporary files in `/tmp`
- Obfuscated dynamic execution through `getattr(__builtins__, "eval")`

## Re-Evaluation Results

After improvements, the same 40-case golden dataset was re-run.

| Result Type | Count |
|---|---:|
| PASS | 33 |
| CONDITIONAL PASS | 7 |
| FAIL | 0 |
| Total | 40 |

Post-improvement metrics:

| Metric | Result | Status |
|---|---:|---|
| Critical Finding Recall | 100.0% overall; 100.0% Critical security | PASS |
| Finding Precision | 100.0% | PASS |
| Agent Routing Accuracy | 100.0% | PASS |
| Actionability Score | 8.0 | PASS |
| Latency p95 | 0.005 seconds | PASS |
| Average Cost per Review | $0.0000 | PASS |
| Human Review Accuracy | 100.0% | PASS |
| Agent Completion Rate | 100.0% | PASS |
| False Positive Rate | 0.0% | PASS |

## Observability and Monitoring

TrustLayer AI was instrumented for LangSmith tracing.

Instrumented spans include:

- Top-level review workflow
- Orchestrator
- Security Review Agent
- Reliability Review Agent
- Test Coverage Review Agent
- Findings aggregation
- Report generation
- Human-review check
- Optional OpenAI-backed LLM calls

Tracked metadata includes:

- File name
- Source length
- Source line count
- Source hash
- Completed agents
- Finding count
- Severity counts
- Agent counts
- Overall risk score
- Human-review decision
- Execution status
- Error count

The tracing layer avoids logging full source code by default. Full source logging can be enabled only when explicitly needed for local evaluation.

## Limitations

The reported before/after results come from a deterministic local evaluation runner. This is useful for repeatable regression testing, but final production evaluation should also include:

- LangSmith trace screenshots from real traced runs
- LLM-as-judge scoring for final qualitative assessment
- Token and cost measurements from OpenAI-backed runs
- Larger datasets with real-world code patterns
- Human spot-checking for edge-case false positives

## Final Assessment

TrustLayer AI now demonstrates a complete AI evaluation workflow:

- Clear evaluation design
- 40-case golden dataset
- LangSmith-ready observability
- Executable baseline evaluation
- Failure clustering
- Targeted improvement
- Re-evaluation against the same benchmark

The project is suitable for GitHub, LinkedIn, and AI Engineer interview discussion because it shows not only agent construction, but also the production evaluation discipline required to make agentic systems reliable.
