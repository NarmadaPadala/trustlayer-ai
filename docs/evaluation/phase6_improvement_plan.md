# Phase 6: Improvement Plan

## Objective

Phase 6 defines how TrustLayer AI should improve after the baseline evaluation. The plan focuses on production AI engineering improvements that directly map to the Phase 1 metrics and Phase 5 failure-analysis process.

The goal is not to add more agents or make the app more complex. The goal is to improve reliability, observability, evaluation performance, and developer trust.

## Improvement Matrix

Spreadsheet-ready roadmap:

```text
docs/evaluation/improvement_plan_matrix.csv
```

This matrix includes:

- Improvement type
- Recommendation
- Expected impact
- Metric affected
- Risk
- Effort level
- Priority

## Priority Strategy

Prioritize improvements in this order:

1. Fix missed Critical security issues.
2. Protect human-review escalation.
3. Reduce false positives in edge cases.
4. Improve actionability and explanation quality.
5. Improve latency and cost.
6. Improve report polish and portfolio presentation.

## Prompt Improvements

### 1. Expand Security Coverage

Recommendation:

Update the Security Review Agent prompt to explicitly cover:

- Path traversal
- Unsafe deserialization with `pickle.loads`
- Unsafe YAML loading with `yaml.load`
- Shell command injection with `shell=True`
- Weak randomness for tokens
- Insecure temporary files
- Prompt-injection comments inside source code

Expected impact:

- Better performance on known failure and adversarial cases.
- Higher Critical Finding Recall.

Metric affected:

- Critical Finding Recall
- Completeness Score

Risk:

- Medium. A broader prompt may increase false positives if the agent is not required to cite code evidence.

Effort:

- Low.

Priority:

- P0.

### 2. Add Evidence-Only Finding Rule

Recommendation:

Add an instruction that every finding must be supported by actual source-code behavior. The agent should not create findings based only on comments, TODOs, variable names, or general suspicion.

Expected impact:

- Reduces unsupported findings in edge cases.
- Improves developer trust.

Metric affected:

- Finding Precision
- False Positive Rate

Risk:

- Low. The system may become slightly less speculative, but this is appropriate for evaluation.

Effort:

- Low.

Priority:

- P1.

### 3. Improve Recommendation Specificity

Recommendation:

Require each recommendation to include a concrete remediation pattern.

Examples:

- Use parameterized SQL queries.
- Replace `yaml.load` with `yaml.safe_load`.
- Replace `pickle.loads` on user input with JSON plus schema validation.
- Replace `shell=True` with `shell=False` and an argument list.
- Replace `random.random()` tokens with `secrets.token_urlsafe`.
- Replace predictable `/tmp` paths with `tempfile.NamedTemporaryFile`.

Expected impact:

- Makes review output easier for developers to act on.

Metric affected:

- Actionability Score
- Explanation Quality

Risk:

- Low.

Effort:

- Low.

Priority:

- P1.

## Control-Flow Improvements

### 1. Add Post-Agent Verification Node

Recommendation:

Add a LangGraph node after all specialist agents and before report generation. This node should verify:

- Required fields are present.
- Duplicate findings are removed.
- Severity is consistent with issue type.
- Critical findings trigger human review.
- Findings are assigned to the correct agent.
- Empty results are intentional, not agent failures.

Expected impact:

- Improves consistency before the user sees the final report.

Metric affected:

- Agent Routing Accuracy
- Human Review Accuracy
- Finding Precision

Risk:

- Medium. It adds another workflow step and may increase latency.

Effort:

- Medium.

Priority:

- P1.

### 2. Parallelize Specialist Agent Execution

Recommendation:

Run Security, Reliability, and Test Coverage agents in parallel when the workflow is ready for parallel state merging.

Expected impact:

- Reduces end-to-end runtime.

Metric affected:

- Latency p95

Risk:

- Medium. Requires careful state merge logic and error isolation.

Effort:

- Medium.

Priority:

- P2.

## Guardrails

### 1. Source-Code Prompt Injection Guardrail

Recommendation:

Treat source-code comments and strings as untrusted content. Comments inside submitted code must never override TrustLayer AI's system instructions.

Expected impact:

- Improves adversarial robustness.

Metric affected:

- Critical Finding Recall
- Finding Precision

Risk:

- Low.

Effort:

- Low.

Priority:

- P0.

### 2. Human-Review Escalation Guardrail

Recommendation:

Enforce this rule as a final invariant:

```text
If any finding severity is Critical:
  overall_risk_score = Critical
  human_review_required = true
```

Expected impact:

- Protects the most important safety behavior in the product.

Metric affected:

- Human Review Accuracy

Risk:

- Low.

Effort:

- Low.

Priority:

- P0.

### 3. Privacy Guardrail For Tracing

Recommendation:

Keep full source-code logging disabled by default. Log source length, hash, line count, and preview unless `TRUSTLAYER_TRACE_SOURCE_CODE=true`.

Expected impact:

- Makes LangSmith evidence safer for portfolio and interview use.

Metric affected:

- Trace Safety
- Production Readiness

Risk:

- Low.

Effort:

- Low.

Priority:

- P2.

## Structured Output Improvements

### 1. Extend ReviewFinding Schema

Recommendation:

Add fields to `ReviewFinding`:

```text
category
confidence
evidence
cwe_or_issue_type
remediation_type
```

Expected impact:

- Easier scoring.
- Better failure clustering.
- Clearer reports.
- Stronger portfolio story around structured AI outputs.

Metric affected:

- Agent Routing Accuracy
- Explanation Quality
- Failure Analysis Quality

Risk:

- Medium. Requires updating UI, tests, report rendering, and model output validation.

Effort:

- Medium.

Priority:

- P1.

### 2. Explicit Safe-Pattern Recognition

Recommendation:

Let agents internally record when safe patterns are present, such as:

- Parameterized SQL
- bcrypt password verification
- environment variable secret loading
- specific exception handling
- transaction rollback handling

These safe-pattern notes do not need to appear in the final user report unless needed for evaluation.

Expected impact:

- Reduces false positives and improves edge-case scoring.

Metric affected:

- Finding Precision
- False Positive Rate

Risk:

- Medium. Could add verbosity if exposed directly in reports.

Effort:

- Medium.

Priority:

- P2.

## Verification Loops

### 1. Golden Dataset Regression Runner

Recommendation:

Create a script that runs all 40 golden cases and writes outputs to:

```text
docs/evaluation/evaluation_results_template.csv
```

Expected impact:

- Makes evaluation repeatable.
- Makes improvements measurable.
- Supports before/after comparison.

Metric affected:

- Evaluation Reproducibility
- Agent Completion Rate
- Regression Stability

Risk:

- Medium. Requires creating executable code snippets for each dataset row.

Effort:

- High.

Priority:

- P1.

### 2. Known Failure Regression Tests

Recommendation:

Add deterministic tests for known failure classes:

- Path traversal
- `pickle.loads`
- `yaml.load`
- `subprocess.run(..., shell=True)`
- `random.random()` for token generation
- predictable temp files

Expected impact:

- Prevents repeated misses on high-risk security cases.

Metric affected:

- Critical Finding Recall
- Regression Stability

Risk:

- Low.

Effort:

- Medium.

Priority:

- P0.

### 3. LangSmith Metadata Verification

Recommendation:

During evaluation execution, attach metadata to each trace:

- `evaluation_case_id`
- `category`
- `difficulty`
- `expected_agent`
- `expected_severity`

Expected impact:

- Makes traces searchable and easier to connect to spreadsheet rows.

Metric affected:

- Trace Completeness
- Failure Analysis Quality

Risk:

- Low.

Effort:

- Medium.

Priority:

- P1.

## Recommended First Improvement Sprint

The first improvement sprint should focus on P0/P1 changes:

| Priority | Improvement |
|---|---|
| P0 | Expand Security Agent prompt for known failure and adversarial classes. |
| P0 | Add source-code prompt-injection guardrail. |
| P0 | Add human-review escalation guardrail. |
| P0 | Add deterministic known-failure regression tests. |
| P1 | Add evidence-only prompt rule. |
| P1 | Improve recommendation specificity. |
| P1 | Add LangSmith evaluation metadata. |

## Expected Before / After Story

This improvement plan supports a strong final project narrative:

```text
I first evaluated TrustLayer AI against a 40-case golden dataset and used LangSmith traces to inspect agent behavior. The baseline identified gaps in known security failure classes, edge-case false positives, and recommendation specificity. I prioritized improvements by production risk, starting with Critical security recall and human-review escalation. After improving prompts, guardrails, structured outputs, and regression tests, I re-ran the same dataset to measure whether recall, precision, routing, actionability, latency, and cost improved.
```

## Phase 6 Decision

The improvement plan should prioritize production risk first, especially missed Critical security findings and human-review errors. After that, TrustLayer AI should improve precision, recommendation quality, structured outputs, and repeatable evaluation automation.
