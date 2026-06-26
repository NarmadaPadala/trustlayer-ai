# Baseline Evaluation Execution Notes

## Purpose

This note documents the first executable baseline run before generating final submission materials.

The run used:

```text
scripts/evaluate_golden_dataset.py
```

The runner executes the existing TrustLayer AI workflow against all 40 golden dataset scenarios and writes:

```text
docs/evaluation/baseline_evaluation_results.csv
docs/evaluation/baseline_metrics.csv
```

## Baseline Run Type

This was a deterministic local baseline run.

Important limitations:

- OpenAI-backed LLM review was not required.
- LangSmith trace URLs were not filled in this local baseline output.
- Token usage and cost are recorded as zero because the deterministic fallback path was used.
- Case-level judge scores are automated estimates, not final LLM-as-judge scores.

This baseline is still useful because it identifies concrete failure modes in the current deterministic TrustLayer behavior.

## Baseline Summary

| Result Type | Count |
|---|---:|
| PASS | 26 |
| CONDITIONAL PASS | 7 |
| FAIL | 7 |
| Total | 40 |

## Baseline Metrics

| Metric | Baseline Result | Status |
|---|---:|---|
| Critical Finding Recall | 57.1% overall; 50.0% Critical security | FAIL |
| Finding Precision | 100.0% | PASS |
| Agent Routing Accuracy | 85.0% | FAIL |
| Actionability Score | 7.5 | FAIL |
| Latency p95 | 0.004 seconds | PASS |
| Average Cost per Review | $0.0000 | PASS |
| Human Review Accuracy | 57.1% | FAIL |
| Agent Completion Rate | 100.0% | PASS |
| False Positive Rate | 0.0% | PASS |

## Failed Cases

| Case ID | Failure Mode | Notes |
|---|---|---|
| TL-KF-001 | missed_security_issue | Path traversal was not detected as the expected security issue. |
| TL-KF-002 | missed_security_issue | Unsafe `pickle.loads()` deserialization was not detected. |
| TL-KF-003 | missed_security_issue | Unsafe `yaml.load()` behavior was not detected. |
| TL-KF-004 | missed_security_issue | `subprocess.run(..., shell=True)` command injection was not detected. |
| TL-KF-005 | missed_security_issue | Weak randomness for reset tokens was not detected. |
| TL-KF-006 | missed_security_issue | Predictable temporary file creation was not detected. |
| TL-ADV-002 | missed_security_issue | Obfuscated dynamic execution through `getattr(__builtins__, "eval")` was not detected. |

## Conditional Pass Cases

The conditional pass cases were mostly safe or nuanced edge cases where the main expected behavior was acceptable but severity or extra findings need review.

| Case ID | Issue |
|---|---|
| TL-EDGE-002 | Parameterized SQL did not trigger SQL injection, but output severity was higher than expected. |
| TL-EDGE-003 | bcrypt password verification avoided the main false positive, but output severity was higher than expected. |
| TL-EDGE-005 | Specific `ValueError` handling avoided broad exception failure, but output severity was higher than expected. |
| TL-EDGE-008 | Environment-based API key avoided hardcoded secret failure, but output severity was higher than expected. |
| TL-EDGE-009 | Database transaction handling avoided the main failure, but output severity was higher than expected. |
| TL-EDGE-011 | Clean utility code produced higher-than-expected severity. |
| TL-EDGE-012 | TODO comment did not become a security finding, but output severity was higher than expected. |

## Interpretation

The baseline confirms that TrustLayer AI has a working multi-agent evaluation path:

- All three agents completed on every case.
- The workflow produced structured findings for every case.
- Local deterministic latency was very low.
- Cost was zero in deterministic mode.

The main quality gap is security recall for known failure classes that are not currently covered by deterministic heuristics:

- Path traversal
- Unsafe deserialization
- Unsafe YAML loading
- Command injection
- Weak randomness
- Insecure temporary files
- Obfuscated dynamic execution

This aligns with the Phase 6 improvement plan, especially:

- `IMP-001`: Expand Security Agent prompt coverage.
- `IMP-006`: Add source-code prompt-injection guardrail.
- `IMP-010`: Add deterministic regression checks for known failure cases.

## Recommended Next Step

Before final submission, decide whether to:

1. Present this as the baseline evaluation and improvement roadmap, or
2. Implement the P0 improvements, re-run the same 40-case dataset, and report before/after results.

Option 2 creates a stronger GitHub project story because it demonstrates a full evaluation loop:

```text
baseline -> failure analysis -> targeted improvements -> re-evaluation
```
