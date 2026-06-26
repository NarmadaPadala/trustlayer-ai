# LangSmith Evidence Checklist

## Purpose

Use this checklist to collect visual evidence that TrustLayer AI has observability and monitoring coverage. These screenshots can be used in the final submission as evidence documentation.

## Project Setup

Recommended LangSmith project:

```text
trustlayer-ai-evaluation
```

Local configuration variables:

```text
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=trustlayer-ai-evaluation
OPENAI_MODEL=gpt-4o-mini
```

Do not upload `.env` files or API keys. Store provider credentials locally or in the deployment secret manager.

## Screenshot Checklist

| Evidence Item | Screenshot Captured | Notes |
|---|---|---|
| LangSmith project page showing `trustlayer-ai-evaluation` | No | Shows project-level organization. |
| Root trace named `TrustLayer Review Workflow` | No | Shows end-to-end workflow trace. |
| Expanded workflow trace with child spans | No | Should show orchestrator and review steps. |
| `TrustLayer Orchestrator` span | No | Shows workflow initialization. |
| `TrustLayer Specialist Agent` span for Security Agent | No | Shows Security Agent execution. |
| `TrustLayer Specialist Agent` span for Reliability Agent | No | Shows Reliability Agent execution. |
| `TrustLayer Specialist Agent` span for Test Coverage Agent | No | Shows Test Coverage Agent execution. |
| Trace metadata showing file name and source hash | No | Shows privacy-safe input tracking. |
| Trace output showing finding count and severity counts | No | Shows structured output observability. |
| Trace output showing overall risk score | No | Shows risk aggregation evidence. |
| Trace output showing human-review decision | No | Shows human-in-the-loop monitoring. |
| LLM run with token usage | No | Required only if OpenAI-backed review is enabled. |
| LLM run with estimated cost | No | Required only if LangSmith recognizes provider/model pricing. |
| Latency view for one complete run | No | Shows operational monitoring. |
| Difficult case trace, such as `TL-ADV-002` | No | Shows adversarial/failure-case observability. |

## Recommended Demo Case

Use this case for a strong evidence screenshot:

```text
TL-ADV-002
```

Why:

- It was a failed adversarial case in the first baseline.
- It passed after targeted security improvements.
- It demonstrates agent reliability and regression improvement.

## Evidence Notes Template

Use this text in the final report:

```text
LangSmith traces were configured for the TrustLayer AI workflow. The root trace captures the full review, while child spans capture the orchestrator, specialist agents, aggregation, report generation, and human-review decision. The traces include privacy-safe input metadata, finding counts, severity counts, risk score, and human-review status. OpenAI-backed runs can additionally capture token usage and estimated cost.
```

## Submission Reminder

Before final submission, update this checklist from `No` to `Yes` for the screenshots you capture. The Markdown file can then be submitted as evidence documentation.
