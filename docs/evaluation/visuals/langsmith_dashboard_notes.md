# LangSmith Dashboard Visual Notes

## Recommended Portfolio Visual

Use this upgraded dashboard visual for portfolio storytelling:

```text
docs/evaluation/visuals/langsmith_evaluation_dashboard_enterprise.svg
```

It is stronger than the original representative trace because it shows:

- Evaluation KPIs
- Dataset and experiment metadata
- Portfolio summary ID and live trace capture status
- Nested agent trace tree
- Security Agent internal checks
- Verification node
- Human escalation gate
- Deterministic evaluator scores
- LLM-as-judge rubric readiness
- Token/cost/latency fields
- Failure cluster before/after signal

## Important Honesty Note

This is still a portfolio dashboard artifact, not a direct exported LangSmith UI screenshot. It intentionally labels the run as deterministic local evaluation and marks LLM-as-judge scores as pending live evaluation.

For final submission or interviews, say:

```text
This visual summarizes the LangSmith-style observability and evaluation evidence for TrustLayer AI. The actual implementation is instrumented for LangSmith tracing; live account screenshots should be captured separately after running with LANGSMITH_TRACING=true.
```

## Replace With Real LangSmith Evidence When Available

After running the app with LangSmith tracing enabled, capture:

- Project page
- Root trace
- Expanded child spans
- Agent metadata
- Token/cost section from an OpenAI-backed run
- Dataset or experiment comparison if run through LangSmith Evaluation

Then use the real screenshot in the final submission and keep this SVG as a polished architecture/evaluation summary.
