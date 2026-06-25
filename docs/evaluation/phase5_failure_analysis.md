# Phase 5: Failure Analysis

## Objective

Phase 5 turns baseline evaluation results into a clear improvement plan. The goal is to identify where TrustLayer AI failed, cluster those failures, quantify their impact, and prioritize the highest-value fixes.

Failure analysis should be done after the Phase 4 baseline run is complete.

## Failure Analysis Inputs

Use these artifacts:

| Artifact | Purpose |
|---|---|
| `docs/evaluation/evaluation_results_template.csv` | Case-level results and judge scores. |
| `docs/evaluation/baseline_metrics_template.csv` | Overall metric performance. |
| LangSmith traces | Execution evidence, latency, token usage, cost, and agent behavior. |
| `docs/evaluation/failure_clusters_template.csv` | Cluster failures by type and impact. |
| `docs/evaluation/top_failure_modes_template.csv` | Document the top 3 failure modes. |

## Failure Clustering Workflow

### Step 1: Filter Failed and Conditional Cases

Start with rows where:

```text
PASS/FAIL = FAIL
```

Then review rows where:

```text
PASS/FAIL = CONDITIONAL PASS
```

Conditional passes often reveal weaker patterns that may become production issues later.

### Step 2: Assign Failure Mode Labels

Use the failure mode labels from Phase 4:

| Failure Mode | Meaning |
|---|---|
| missed_security_issue | Expected security issue was not detected. |
| missed_reliability_issue | Expected reliability issue was not detected. |
| missed_testing_gap | Expected testing gap was not detected. |
| false_positive | TrustLayer reported an unsupported issue. |
| wrong_agent | Finding was assigned to the wrong specialist agent. |
| wrong_severity | Finding severity was materially too high or too low. |
| weak_recommendation | Recommendation was too vague to be useful. |
| weak_explanation | Explanation did not clearly explain risk or impact. |
| human_review_error | Critical issue did not trigger human review, or non-critical case incorrectly did. |
| latency_or_cost_issue | Case exceeded latency or cost threshold. |
| trace_missing | LangSmith evidence was missing or incomplete. |

### Step 3: Cluster Similar Failures

Group failures by shared root cause, not only by symptom.

Example:

| Symptom | Possible Cluster |
|---|---|
| Missed `pickle.loads()` and `yaml.load()` | Unsafe deserialization detection gap |
| Missed `subprocess.run(..., shell=True)` and obfuscated `getattr` execution | Dangerous execution detection gap |
| Flagged parameterized SQL as unsafe | Security false-positive pattern |
| Gave generic fix recommendations | Weak remediation quality |
| Trace missing token usage | Observability configuration gap |

### Step 4: Quantify Impact

For each cluster, measure:

- Number of affected cases
- Percentage of the 40-case dataset affected
- Number of Critical or High expected cases affected
- Metrics impacted
- Agents impacted
- Whether human review was wrong
- Whether the issue affects production trust

Use this formula:

```text
Failure Cluster Impact % = affected cases / 40 * 100
```

For critical/high-risk misses:

```text
Critical/High Miss Impact = missed critical or high cases / total expected critical or high cases * 100
```

### Step 5: Prioritize Improvements

Prioritize using this decision table:

| Priority | Condition |
|---|---|
| P0 | Missed Critical security issue or wrong human-review decision for Critical risk. |
| P1 | Missed High severity issue, repeated false positives, or major routing failure. |
| P2 | Weak actionability, weak explanation, or moderate completeness gap. |
| P3 | Minor formatting, trace metadata, or low-severity scoring issue. |

## Top 3 Failure Modes Template

After clustering, document the top three failure modes.

Use:

```text
docs/evaluation/top_failure_modes_template.csv
```

Recommended fields:

| Field | Description |
|---|---|
| Rank | 1, 2, or 3 based on impact and priority. |
| Failure Mode | Standard failure mode label. |
| Summary | Plain-language description of the issue. |
| Impacted Cases | Case IDs affected. |
| Impact Quantification | Count and percentage impact. |
| User Impact | Why this matters to a developer or reviewer. |
| Likely Root Cause | Prompt, heuristic, routing, output, or observability issue. |
| Recommended Fix | Specific improvement to try first. |
| Owner | Suggested owner or component. |
| Priority | P0, P1, P2, or P3. |
| Status | Open, In Progress, Fixed, or Deferred. |

## Failure Cluster Template

Use:

```text
docs/evaluation/failure_clusters_template.csv
```

Recommended fields:

| Field | Description |
|---|---|
| Failure Cluster ID | Stable cluster ID, such as FC-001. |
| Failure Mode | Standard failure mode label. |
| Related Case IDs | Cases included in this cluster. |
| Affected Category | Happy Path, Edge Case, Known Failure, or Adversarial. |
| Affected Agent | Security, Reliability, Test Coverage, or Multiple Agents. |
| Count | Number of affected cases. |
| Severity Impact | Highest expected severity affected. |
| Metric Impacted | Recall, precision, routing, actionability, latency, or cost. |
| Root Cause Hypothesis | Best explanation for why the failure happened. |
| Example Evidence | Short evidence from output or LangSmith trace. |
| Priority | P0, P1, P2, or P3. |

## Example Failure Analysis

Example only:

```text
Failure Cluster ID: FC-001
Failure Mode: missed_security_issue
Related Case IDs: TL-KF-002, TL-KF-003
Affected Category: Known Failure
Affected Agent: Security Review Agent
Count: 2
Severity Impact: Critical
Metric Impacted: Critical Finding Recall
Root Cause Hypothesis: Current security heuristics detect eval/exec and SQL injection but do not detect unsafe deserialization patterns.
Example Evidence: TrustLayer did not flag pickle.loads() or yaml.load() in known failure cases.
Priority: P0
```

## Failure Analysis Questions

Use these questions during review:

1. Did TrustLayer miss any Critical or High expected issue?
2. Did TrustLayer incorrectly trigger or fail to trigger human review?
3. Did any agent repeatedly miss a class of issues?
4. Did any agent produce unsupported findings?
5. Did findings route to the wrong specialist agent?
6. Did recommendations tell the developer what to change?
7. Did explanations clearly connect code behavior to production risk?
8. Did LangSmith traces capture enough evidence for debugging?
9. Did latency or cost exceed the operating threshold?
10. Did adversarial cases affect the review output?

## Failure Analysis Output

At the end of Phase 5, produce:

1. A completed failure cluster table.
2. A top 3 failure modes table.
3. A short written summary of the most important failures.
4. A prioritized list of improvements for Phase 6.

## Written Summary Template

```text
Baseline evaluation identified {number_of_failed_cases} failed cases and {number_of_conditional_cases} conditional passes across the 40-case golden dataset.

The top failure mode was {top_failure_mode}, affecting {affected_count} cases ({impact_percent}% of the dataset). This primarily impacted {metric_impacted} and was most visible in {case_ids}.

The second failure mode was {second_failure_mode}, affecting {affected_count} cases. This reduced trust because {user_impact}.

The third failure mode was {third_failure_mode}, affecting {affected_count} cases. This should be addressed after higher-risk recall and human-review issues.

Priority improvements should focus first on {p0_or_p1_focus}, then on {p2_focus}.
```

## Phase 5 Decision

Failure analysis should prioritize production risk over cosmetic quality. Missed Critical security issues, wrong human-review decisions, and repeated false positives should be fixed before improving wording or formatting.
