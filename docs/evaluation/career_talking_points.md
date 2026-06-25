# Career Talking Points

## One-Liner

TrustLayer AI is a multi-agent Python code review system that I evaluated using a 40-case golden dataset, LangSmith-ready observability, baseline measurement, failure analysis, targeted improvements, and re-evaluation.

## Best 30-Second Pitch

I evaluated TrustLayer AI, a multi-agent code review system with Security, Reliability, and Test Coverage agents. I created a 40-case golden dataset, added LangSmith-ready tracing, ran a baseline, found missed advanced security cases, improved the Security Agent, and re-ran the same benchmark. The project shows the full production AI loop: measure, observe, debug, improve, and verify.

## Best Technical Pitch

The system uses LangGraph to orchestrate three specialist agents and produces structured findings, risk scores, and human-review decisions. I evaluated it on Critical Finding Recall, Finding Precision, Agent Routing Accuracy, Actionability, Latency, Cost, Human Review Accuracy, and Agent Completion Rate. The first baseline found 7 failures, mostly missed security cases. After targeted improvements and regression tests, the same 40-case dataset had 0 failed cases in the deterministic evaluation runner.

## Best Metrics To Mention

- Golden dataset: 40 cases
- Distribution: 20 happy path, 12 edge, 6 known failure, 2 adversarial
- Before: 26 pass, 7 conditional pass, 7 fail
- After: 33 pass, 7 conditional pass, 0 fail
- Critical Finding Recall: 100.0% after improvements
- Human Review Accuracy: 100.0% after improvements
- Agent Completion Rate: 100.0%
- Tests: 10 passed

## What To Emphasize

- I evaluated an existing AI system rather than building another demo.
- I used a fixed golden dataset so results were repeatable.
- I added observability around the workflow and agents.
- I found real failure modes.
- I prioritized fixes by production risk.
- I re-ran the same benchmark after improvements.

## Recruiter-Friendly Version

This project shows that I can evaluate AI systems, not just build them. I created a benchmark, measured performance, found reliability gaps, improved the system, and documented results clearly.

## Hiring-Manager Version

This project demonstrates practical production AI engineering. I defined success metrics, created a golden dataset, instrumented the agent workflow, measured baseline performance, identified high-risk failures, implemented targeted improvements, added regression tests, and re-evaluated using the same benchmark.

## Founding-Engineer Version

I treated the agent system like a product surface with measurable failure modes. I focused on the highest-risk failures first, especially Critical security recall and human-review accuracy, then used the same benchmark to verify improvement. That kind of evaluation loop is what makes agentic systems trustworthy enough to ship.

## Questions To Be Ready For

1. Why did you choose those metrics?
2. How did you build the golden dataset?
3. What did the baseline reveal?
4. How did you decide what to fix first?
5. How did LangSmith help?
6. How would you monitor this in production?
7. What are the limitations of the evaluation?
8. What would you improve next?

## Best Limitation To Mention

The current reported before/after results come from the deterministic local evaluation runner. The next step is to capture LangSmith screenshots from traced runs and add LLM-as-judge scoring for qualitative dimensions like explanation quality and actionability.

## Best Closing Line

This project shows the full AI engineering loop: define quality, measure behavior, observe the system, analyze failures, improve the agents, and verify the change with the same benchmark.
