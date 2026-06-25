# Phase 1: TrustLayer AI Evaluation Design

## Evaluation Goal

TrustLayer AI is not being evaluated as a new application. It is being evaluated as a production-minded AI review system that helps developers identify security, reliability, and test coverage risks before Python code reaches production.

The evaluation should answer one practical question:

> Can TrustLayer AI consistently produce accurate, complete, actionable, and observable code review results at an acceptable latency and cost?

## User Outcome

The target user is a developer, AI engineer, or technical reviewer preparing Python code for deployment.

The desired user outcome is:

> A user submits Python source code and receives a clear, prioritized review that correctly identifies meaningful security, reliability, and test coverage risks, routes findings through the correct specialist agents, explains why each issue matters, recommends practical fixes, and flags when human review is required.

## Evaluation One-Liner

TrustLayer AI passes evaluation if it reliably detects high-impact Python code risks, assigns findings to the correct specialist agents, explains issues clearly, recommends useful remediation steps, triggers human review for critical risk, and stays within practical latency and cost limits.

## Evaluation Scope

The evaluation covers the existing TrustLayer AI architecture:

- Orchestrator Agent / LangGraph workflow
- Security Review Agent
- Reliability Review Agent
- Test Coverage Review Agent
- Risk scoring
- Human-review decision
- Final markdown report
- Structured `ReviewState` and `ReviewFinding` outputs
- LangSmith traces for observability

The evaluation does not require building a new product interface. The evaluation is focused on measuring the quality, behavior, and operational performance of the existing multi-agent review system.

## Primary Evaluation Metrics

| Metric | Type | What It Measures | Judge Method | Pass / Fail Threshold |
|---|---|---|---|---|
| Critical Finding Recall | Quality | Whether TrustLayer AI detects the expected high-risk issue in each golden test case. | Compare system findings against expected findings in the golden dataset. Use deterministic matching for known keywords and LLM-as-judge for semantic matches. | Pass if overall recall is at least 90% and recall on Critical security cases is 100%. |
| Finding Precision | Quality | Whether reported findings are real, relevant, and supported by the submitted code. | LLM-as-judge reviews each finding against the source code and marks it as supported, partially supported, or unsupported. | Pass if at least 85% of findings are supported by the code. |
| Agent Routing Accuracy | Behavior | Whether each finding is assigned to the correct specialist agent: Security, Reliability, or Test Coverage. | Compare each finding's `agent` field against the expected category in the golden dataset. Validate with LangSmith trace spans when available. | Pass if at least 90% of findings are routed to the correct agent. |
| Actionability Score | Quality / UX | Whether recommendations are specific, practical, and useful to a developer. | LLM-as-judge scores recommendations from 1-10 using the actionability rubric. | Pass if average score is at least 8.0 and no category average is below 7.0. |
| Latency and Cost Efficiency | Operational | Whether reviews complete within a practical time and token/cost budget. | Use LangSmith traces to measure end-to-end latency, per-agent latency, token usage, and estimated cost. | Pass if p95 latency is 30 seconds or lower and average estimated cost is $0.15 or lower per review. |

## Secondary Metrics

These metrics are useful for the final report but should not block the first evaluation run.

| Metric | What It Measures | Suggested Target |
|---|---|---|
| Completeness Score | Whether TrustLayer finds all major expected issue types in a case. | Average score >= 8.0 |
| Explanation Quality | Whether findings clearly explain the risk and its production impact. | Average score >= 8.0 |
| Human Review Accuracy | Whether `human_review_required` is true when Critical findings exist. | 100% |
| False Positive Rate | Percentage of findings that are unsupported or too speculative. | <= 15% |
| Agent Completion Rate | Whether all three specialist agents complete successfully. | >= 98% |

## Judge Methods

### 1. Golden Dataset Comparison

Each test case will include expected findings. The evaluator compares TrustLayer AI's output against the expected finding list.

This method is best for:

- Critical Finding Recall
- Agent Routing Accuracy
- Human Review Accuracy
- Known failure tracking

### 2. LLM-as-Judge

An evaluator model reviews the submitted code, expected findings, and TrustLayer AI output. It scores quality using a structured rubric.

This method is best for:

- Finding Precision
- Completeness
- Actionability
- Explanation Quality

The judge should not simply reward longer answers. It should reward findings that are specific, evidence-backed, and useful for remediation.

### 3. LangSmith Trace Review

LangSmith traces should be used to inspect workflow execution and operational performance.

This method is best for:

- Orchestrator execution
- Per-agent execution
- Token usage
- Latency
- Cost
- Agent errors
- Retry behavior

### 4. Rule-Based Checks

Some evaluation checks can be automated using structured fields from `ReviewState`.

This method is best for:

- `completed_agents` contains all three specialist agents
- `overall_risk_score` matches severity rules
- `human_review_required` is true when any Critical finding exists
- `execution_status` is completed
- Required fields are present in each finding

## LLM-as-Judge Rubric Preview

Each evaluated review should be scored from 1-10 on four dimensions.

| Dimension | 1-3 | 4-6 | 7-8 | 9-10 |
|---|---|---|---|---|
| Correctness | Mostly wrong or unsupported. | Some correct findings but important mistakes. | Mostly correct with minor issues. | Fully supported by the code and accurately classified. |
| Completeness | Misses most important issues. | Finds some issues but misses important risks. | Finds most important issues. | Captures all major expected risks without unnecessary noise. |
| Actionability | Vague or not useful. | Some useful advice but too generic. | Clear and practical remediation. | Specific, developer-ready fixes tied to the code. |
| Explanation Quality | Confusing or shallow. | Understandable but incomplete. | Clear explanation of risk and impact. | Concise, production-aware explanation with strong reasoning. |

## Pass / Fail Framework

An evaluation run should be marked `PASS` only if all primary thresholds are met.

| Result | Condition |
|---|---|
| PASS | All primary metrics meet thresholds. |
| CONDITIONAL PASS | One non-critical metric misses the threshold by a small margin, and no Critical security case is missed. |
| FAIL | Any Critical security case is missed, human review is not triggered for Critical risk, or two or more primary metrics miss threshold. |

## Recommended Baseline Run

The first evaluation run should be treated as a baseline, not as the final result.

Recommended baseline process:

1. Run TrustLayer AI on the 40-case golden dataset.
2. Capture the output for each case.
3. Record latency, token usage, and cost in LangSmith.
4. Score outputs using the LLM-as-judge rubric.
5. Calculate baseline metrics.
6. Cluster failures.
7. Choose targeted improvements.
8. Re-run the same dataset after improvements.

## Initial Threshold Rationale

The thresholds are intentionally production-oriented but realistic for a Week 4 evaluation project.

- Critical security misses are treated as unacceptable because the product is positioned as a pre-deployment safety layer.
- Precision is set at 85% because noisy findings reduce developer trust.
- Routing accuracy is set at 90% because specialist-agent behavior is part of the product promise.
- Actionability is set at 8/10 because a review system should help developers fix problems, not only detect them.
- Latency and cost thresholds keep the system practical for repeated code review use.

## Phase 1 Decision

TrustLayer AI's evaluation should use five primary metrics:

1. Critical Finding Recall
2. Finding Precision
3. Agent Routing Accuracy
4. Actionability Score
5. Latency and Cost Efficiency

These metrics will guide the golden dataset, LangSmith tracing, evaluation spreadsheet, failure analysis, improvement plan, and final submission report.
