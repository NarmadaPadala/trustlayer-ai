# Phase 3: LangSmith Instrumentation

## Objective

Phase 3 makes TrustLayer AI observable. The goal is to prove that every evaluation run can be inspected from input to final report:

- User input metadata
- Orchestrator execution
- Security Agent execution
- Reliability Agent execution
- Test Coverage Agent execution
- Agent completion
- Findings produced
- Risk score
- Human-review decision
- Latency
- Token usage
- Estimated cost

## LangSmith Project

Recommended project name:

```text
trustlayer-ai-evaluation
```

Use this project for all Week 4 evaluation runs so the traces, metrics, and screenshots stay grouped together.

## Environment Variables

Create a `.env` file from the included template:

```bash
cp .env.example .env
```

Then fill in:

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=trustlayer-ai-evaluation

TRUSTLAYER_TRACE_SOURCE_CODE=false
LANGCHAIN_CALLBACKS_BACKGROUND=false
```

Optional variables:

```text
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_WORKSPACE_ID=your_workspace_id
```

Use `LANGSMITH_WORKSPACE_ID` if your LangSmith account has more than one workspace. Use `LANGSMITH_ENDPOINT` if your account is in a non-default region.

## What Was Instrumented

### 1. Top-Level Workflow Trace

File:

```text
app/graph/workflow.py
```

Function:

```python
run_review_workflow()
```

Trace name:

```text
TrustLayer Review Workflow
```

This trace captures the full review run and creates a parent span for the evaluation case.

Tracked fields:

- `file_name`
- `source_chars`
- `source_lines`
- `source_sha256`
- `source_preview`
- `completed_agents`
- `finding_count`
- `severity_counts`
- `agent_counts`
- `overall_risk_score`
- `human_review_required`
- `execution_status`
- `error_count`

By default, the trace does not log the full source code. It logs a source hash, size, line count, and short preview. To log full code during local evaluation, set:

```text
TRUSTLAYER_TRACE_SOURCE_CODE=true
```

### 2. Orchestrator Trace

File:

```text
app/graph/workflow.py
```

Function:

```python
orchestrator_node()
```

Trace name:

```text
TrustLayer Orchestrator
```

This shows when the LangGraph workflow begins and when the orchestrator sets execution status to `running`.

### 3. Specialist Agent Node Trace

File:

```text
app/graph/workflow.py
```

Function:

```python
_run_agent_node()
```

Trace name:

```text
TrustLayer Specialist Agent
```

This captures each specialist agent node as it runs through LangGraph.

Tracked fields:

- Agent name
- File name
- Source hash and size
- Findings after the node runs
- Completed agents
- Error count

Expected child runs:

- Security Review Agent
- Reliability Review Agent
- Test Coverage Review Agent

### 4. Direct Agent Review Trace

File:

```text
app/agents/base.py
```

Function:

```python
run_review_agent()
```

Trace name:

```text
TrustLayer Agent Review
```

This captures deterministic findings and optional LLM-backed findings for each agent.

### 5. LLM Call Trace

File:

```text
app/agents/base.py
```

LangChain call:

```python
chain.invoke(...)
```

The LLM call includes:

- `run_name`: the agent name
- tags:
  - `trustlayer-ai`
  - `code-review`
  - agent name
- metadata:
  - `agent`
  - `file_name`
  - `source_chars`
  - `model`
- model metadata:
  - `ls_provider=openai`
  - `ls_model_name=<configured model>`

This supports token and cost tracking in LangSmith when OpenAI-backed review is enabled.

## Tracing Helper

File:

```text
app/utils/tracing.py
```

Purpose:

- Summarizes source code safely.
- Adds source length, line count, hash, and preview.
- Summarizes findings by severity and agent.
- Prevents accidental full-code logging unless explicitly enabled.
- Formats trace inputs and outputs for LangSmith.

## How To Run With Tracing

From the project root:

```bash
source .venv/bin/activate
cp .env.example .env
```

Fill in `.env`, then export the variables:

```bash
set -a
source .env
set +a
```

Run the app:

```bash
python3 -m streamlit run app/ui/streamlit_app.py
```

Then review one of the sample files:

```text
sample_files/vulnerable_app.py
```

In LangSmith, open the `trustlayer-ai-evaluation` project and confirm a new trace appears.

## What To Verify In LangSmith

For each traced run, verify:

| Evidence Item | What To Check |
|---|---|
| Project | Trace appears under `trustlayer-ai-evaluation`. |
| Parent Trace | Root trace is named `TrustLayer Review Workflow`. |
| Orchestrator | Child span named `TrustLayer Orchestrator` exists. |
| Security Agent | Specialist agent span includes Security Review Agent. |
| Reliability Agent | Specialist agent span includes Reliability Review Agent. |
| Test Coverage Agent | Specialist agent span includes Test Coverage Review Agent. |
| Inputs | File name, source length, source hash, and preview are visible. |
| Outputs | Finding count, severity counts, risk score, and human-review status are visible. |
| Token Usage | Token usage appears on LLM runs when OpenAI-backed review is enabled. |
| Cost | Estimated cost appears when LangSmith recognizes provider/model pricing. |
| Latency | End-to-end and per-span latency are visible. |

## Evidence Screenshots For Final Submission

Capture these screenshots during the final evaluation run:

1. LangSmith project page showing `trustlayer-ai-evaluation`.
2. Root trace named `TrustLayer Review Workflow`.
3. Expanded trace showing orchestrator and three specialist agents.
4. One Security Agent run with findings.
5. One Reliability Agent run with findings.
6. One Test Coverage Agent run with findings.
7. Token usage and cost section from an LLM-backed run.
8. Latency view showing total runtime and per-step runtime.
9. Metadata showing file name, risk score, and human-review decision.
10. Failed or difficult case trace, if any, for failure analysis.

## Production Monitoring Notes

For production monitoring, track these over time:

- Critical Finding Recall on regression dataset
- False positive rate
- Human review trigger accuracy
- Average and p95 latency
- Average tokens per review
- Average cost per review
- Agent failure rate
- Retry frequency
- Most common issue categories

These metrics help determine whether TrustLayer AI is improving, drifting, or becoming too expensive/noisy for practical developer use.

## Phase 3 Decision

TrustLayer AI now has observability hooks for the full review workflow, orchestrator, specialist agents, findings, risk score, human-review decision, and LLM calls. This makes the project ready for Phase 4 baseline evaluation execution.
