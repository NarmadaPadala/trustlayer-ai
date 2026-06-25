# Evaluation Results Table

## TrustLayer AI Evaluation Results

| Evaluation Stage | PASS | CONDITIONAL PASS | FAIL | Notes |
|---|---:|---:|---:|---|
| Baseline Run | 26 | 7 | 7 | Initial run exposed missed advanced security cases. |
| Post-Improvement Run | 33 | 7 | 0 | Targeted Security Agent fixes eliminated failed cases. |

## Metric Summary

| Metric | Baseline Result | Post-Improvement Result | Threshold | Final Status |
|---|---:|---:|---|---|
| Critical Finding Recall | 57.1% overall; 50.0% Critical security | 100.0% overall; 100.0% Critical security | >= 90% overall and 100% Critical security | PASS |
| Finding Precision | 100.0% | 100.0% | >= 85% | PASS |
| Agent Routing Accuracy | 85.0% | 100.0% | >= 90% | PASS |
| Actionability Score | 7.5 | 8.0 | >= 8.0 | PASS |
| Latency p95 | 0.004 seconds | 0.005 seconds | <= 30 seconds | PASS |
| Average Cost per Review | $0.0000 | $0.0000 | <= $0.15 | PASS |
| Human Review Accuracy | 57.1% | 100.0% | 100% | PASS |
| Agent Completion Rate | 100.0% | 100.0% | >= 98% | PASS |
| False Positive Rate | 0.0% | 0.0% | <= 15% | PASS |

## Improvement Impact

| Improvement Area | Before | After | Impact |
|---|---|---|---|
| Known failure security coverage | Missed path traversal, unsafe deserialization, command injection, weak randomness, insecure temp files, and obfuscated eval. | All known failure cases detected by deterministic evaluation runner. | Critical security recall improved to 100%. |
| Human-review escalation | Missed Critical findings could not trigger human review. | Critical findings trigger `human_review_required=true`. | Human Review Accuracy improved to 100%. |
| Regression safety | Known failure classes were not covered by tests. | Regression tests added for P0 security classes. | Future changes are less likely to reintroduce the same misses. |

## Note

These results are from the deterministic local evaluation runner. Final submission evidence should also include real LangSmith screenshots from traced runs and, if possible, LLM-as-judge scoring for qualitative review dimensions.
