# Phase 4: Evaluation Execution

## Objective

Phase 4 turns the evaluation design and golden dataset into a repeatable baseline run. The goal is to run TrustLayer AI against the 40-case dataset, capture outputs and LangSmith traces, score each case, and calculate pass/fail metrics.

This phase creates the evidence needed for failure analysis and improvement planning.

## Evaluation Artifacts

| Artifact | Purpose |
|---|---|
| `docs/evaluation/golden_dataset.csv` | Official 40-case baseline dataset. |
| `docs/evaluation/evaluation_results_template.csv` | Case-level scoring spreadsheet. |
| `docs/evaluation/baseline_metrics_template.csv` | Summary metrics table for final baseline results. |
| `docs/evaluation/phase4_evaluation_execution.md` | Execution workflow, pass/fail rules, and judge rubric. |

## Evaluation Workflow

### Step 1: Prepare Environment

Confirm the app works locally:

```bash
python3 -m pytest -q
```

Configure tracing:

```bash
cp .env.example .env
```

Set these values in `.env`:

```text
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=trustlayer-ai-evaluation

TRUSTLAYER_TRACE_SOURCE_CODE=false
LANGCHAIN_CALLBACKS_BACKGROUND=false
```

Load environment variables:

```bash
set -a
source .env
set +a
```

### Step 2: Run Each Golden Dataset Case

For each case in `golden_dataset.csv`:

1. Create or use a Python snippet that matches the scenario.
2. Run the snippet through TrustLayer AI.
3. Capture the final `ReviewState`.
4. Save the LangSmith trace URL.
5. Record actual findings, risk score, latency, tokens, and cost.

### Step 3: Fill Evaluation Spreadsheet

Use:

```text
docs/evaluation/evaluation_results_template.csv
```

For every case, fill:

- Actual Agents Completed
- Actual Finding Count
- Actual Severity Highest
- Actual Risk Score
- Human Review Required
- Expected Finding Detected
- False Positive Count
- Agent Routing Correct
- Severity Correct
- Correctness Score 1-10
- Completeness Score 1-10
- Actionability Score 1-10
- Explanation Quality Score 1-10
- End-to-End Latency Seconds
- Total Tokens
- Estimated Cost USD
- LangSmith Trace URL
- PASS/FAIL
- Failure Mode
- Evaluator Notes

### Step 4: Score With LLM-as-Judge

Use the rubric below to score each case on:

- Correctness
- Completeness
- Actionability
- Explanation Quality

The judge should evaluate the submitted code, expected findings, and TrustLayer AI output. It should not reward long answers unless they are accurate and useful.

### Step 5: Calculate Baseline Metrics

Use:

```text
docs/evaluation/baseline_metrics_template.csv
```

Calculate:

- Critical Finding Recall
- Finding Precision
- Agent Routing Accuracy
- Actionability Score
- p95 Latency
- Average Cost per Review
- Human Review Accuracy
- Agent Completion Rate
- False Positive Rate

### Step 6: Assign Overall Result

Use the pass/fail framework below:

| Result | Condition |
|---|---|
| PASS | All primary metrics meet thresholds. |
| CONDITIONAL PASS | One non-critical metric misses the threshold by a small margin, and no Critical security case is missed. |
| FAIL | Any Critical security case is missed, human review is not triggered for Critical risk, or two or more primary metrics miss threshold. |

## Case-Level PASS/FAIL Rules

Each dataset row should receive a case-level result.

| Case Result | Condition |
|---|---|
| PASS | Expected finding is detected, routing is correct, severity is acceptable, and judge scores are mostly 7 or higher. |
| CONDITIONAL PASS | Main finding is detected, but there is a minor severity, explanation, or actionability issue. |
| FAIL | Expected high-impact finding is missed, finding is routed to the wrong agent, output is unsupported, or human review is wrong for Critical risk. |

## Primary Baseline Metrics

| Metric | Formula | Threshold |
|---|---|---|
| Critical Finding Recall | Expected Critical/High findings detected ÷ expected Critical/High findings | >= 90% overall, 100% on Critical security cases |
| Finding Precision | Supported findings ÷ total findings | >= 85% |
| Agent Routing Accuracy | Correctly routed findings ÷ evaluated findings | >= 90% |
| Actionability Score | Average actionability score across all cases | >= 8.0 average and no category below 7.0 |
| Latency p95 | 95th percentile end-to-end latency from LangSmith | <= 30 seconds |
| Average Cost per Review | Total estimated cost ÷ number of reviews | <= $0.15 |

## Secondary Metrics

| Metric | Formula | Target |
|---|---|---|
| Human Review Accuracy | Critical cases with `human_review_required=true` ÷ all Critical cases | 100% |
| Agent Completion Rate | Cases where all three agents completed ÷ total cases | >= 98% |
| False Positive Rate | Unsupported findings ÷ total findings | <= 15% |
| Completeness Score | Average completeness judge score | >= 8.0 |
| Explanation Quality Score | Average explanation judge score | >= 8.0 |

## LLM-as-Judge Rubric

Each case receives four judge scores from 1-10.

### Correctness

| Score | Definition |
|---:|---|
| 1-3 | Findings are mostly wrong, unsupported by the code, or dangerously misleading. |
| 4-6 | Some correct observations, but important classification or evidence errors exist. |
| 7-8 | Mostly correct findings with minor wording, severity, or evidence issues. |
| 9-10 | Findings are accurate, code-supported, correctly categorized, and severity is appropriate. |

### Completeness

| Score | Definition |
|---:|---|
| 1-3 | Misses most important expected issues. |
| 4-6 | Finds some issues but misses at least one major expected risk. |
| 7-8 | Finds most expected issues, with minor gaps. |
| 9-10 | Captures all major expected risks without adding distracting noise. |

### Actionability

| Score | Definition |
|---:|---|
| 1-3 | Recommendations are vague, generic, or not useful. |
| 4-6 | Recommendations are directionally useful but lack concrete remediation details. |
| 7-8 | Recommendations are clear and practical for a developer to implement. |
| 9-10 | Recommendations are specific, production-aware, and directly tied to the code issue. |

### Explanation Quality

| Score | Definition |
|---:|---|
| 1-3 | Explanation is confusing, shallow, or missing the production impact. |
| 4-6 | Explanation is understandable but incomplete. |
| 7-8 | Explanation clearly states the risk and why it matters. |
| 9-10 | Explanation is concise, evidence-backed, and explains both risk and remediation reasoning. |

## LLM-as-Judge Prompt Template

Use this prompt to score each TrustLayer AI result.

```text
You are an expert AI code review evaluator.

Evaluate TrustLayer AI's review output against the expected result.

Case ID:
{case_id}

Scenario:
{scenario_description}

Submitted Python Code:
{source_code}

Expected Findings:
{expected_findings}

Expected Agent:
{expected_agent}

Expected Severity:
{expected_severity}

TrustLayer AI Output:
{actual_output}

Score the output from 1-10 on:
1. Correctness
2. Completeness
3. Actionability
4. Explanation Quality

Also return:
- expected_finding_detected: yes/no
- agent_routing_correct: yes/no
- severity_correct: yes/no
- false_positive_count
- failure_mode, if any
- concise evaluator_notes

Be strict. Reward only findings that are supported by the submitted code.
Do not reward long answers unless they are accurate, useful, and specific.
```

## Recommended Failure Mode Labels

Use consistent labels in the evaluation spreadsheet:

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

## Baseline Results Table

Fill this after running all 40 cases.

| Metric | Baseline Result | Threshold | Status |
|---|---:|---:|---|
| Critical Finding Recall | TBD | >= 90%; Critical security = 100% | TBD |
| Finding Precision | TBD | >= 85% | TBD |
| Agent Routing Accuracy | TBD | >= 90% | TBD |
| Actionability Score | TBD | >= 8.0 | TBD |
| Latency p95 | TBD | <= 30 seconds | TBD |
| Average Cost per Review | TBD | <= $0.15 | TBD |
| Human Review Accuracy | TBD | 100% | TBD |
| Agent Completion Rate | TBD | >= 98% | TBD |
| False Positive Rate | TBD | <= 15% | TBD |

## Phase 4 Decision

The evaluation run should use the 40-case golden dataset, score each case in `evaluation_results_template.csv`, summarize metrics in `baseline_metrics_template.csv`, and use LangSmith traces as execution evidence.

The baseline run should be treated as the starting point for Phase 5 failure analysis, not as the final quality claim.
