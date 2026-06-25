# Loom Walkthrough Script

## Target Length

5 minutes

## Audience

- AI Engineer interviewers
- Hiring managers
- Technical recruiters
- GenAcademy project reviewers
- GitHub or LinkedIn portfolio viewers

## Script

### 0:00-0:30 - Project Introduction

Hi, I am walking through my Week 4 evaluation project for TrustLayer AI.

TrustLayer AI is a multi-agent Python code review system. It uses an Orchestrator Agent, Security Review Agent, Reliability Review Agent, and Test Coverage Review Agent to identify risks before code reaches production.

For this project, I did not build a new app. I evaluated the existing agentic system using AI evaluation, observability, and monitoring practices.

### 0:30-1:10 - System Overview

The app accepts Python source code and runs it through a LangGraph workflow.

The Security Agent checks for vulnerabilities like hardcoded secrets, SQL injection, unsafe deserialization, command injection, and dynamic execution.

The Reliability Agent checks for production reliability issues like missing timeouts, missing retries, broad exception handling, and missing validation.

The Test Coverage Agent checks whether the submitted code has meaningful unit, integration, edge-case, and negative test coverage.

The workflow returns structured findings, an overall risk score, and a human-review decision.

### 1:10-1:50 - Evaluation Design

I started by defining the user outcome.

The desired outcome is that a developer submits Python code and receives accurate, prioritized, actionable findings, with the correct specialist agent attached to each issue.

I used five primary metrics:

1. Critical Finding Recall
2. Finding Precision
3. Agent Routing Accuracy
4. Actionability Score
5. Latency and Cost Efficiency

I also tracked human-review accuracy, agent completion rate, and false-positive rate.

### 1:50-2:30 - Golden Dataset

Next, I created a 40-case golden dataset.

The dataset includes:

- 20 happy path cases
- 12 edge cases
- 6 known failure cases
- 2 adversarial cases

The known failure cases included path traversal, unsafe `pickle.loads`, unsafe `yaml.load`, command injection, weak randomness, and predictable temp files.

The adversarial cases included source-code comments that tried to override the reviewer instructions and obfuscated dynamic execution.

### 2:30-3:10 - Observability With LangSmith

I then added LangSmith instrumentation.

The workflow now traces the full review, orchestrator, specialist agents, aggregation, report generation, and human-review decision.

The trace metadata includes file name, source length, source hash, completed agents, finding count, severity counts, risk score, and human-review status.

This lets me debug not only the final answer, but also how each agent behaved inside the workflow.

### 3:10-4:00 - Baseline and Failure Analysis

I ran the first baseline against all 40 cases.

Initial results were:

- 26 pass
- 7 conditional pass
- 7 fail

The failures were concentrated in the Security Agent. It missed several advanced security cases like path traversal, unsafe deserialization, command injection, weak randomness, insecure temp files, and obfuscated eval.

That failure analysis was valuable because it showed the system worked end to end, but needed better security recall for production-grade code review.

### 4:00-4:40 - Improvements and Re-Evaluation

I implemented targeted P0 improvements.

I expanded the Security Agent's deterministic checks, improved the Security Agent prompt, added prompt-injection awareness for source-code comments, and added regression tests for the known failure classes.

Then I re-ran the exact same 40-case dataset.

Post-improvement results were:

- 33 pass
- 7 conditional pass
- 0 fail

Critical Finding Recall improved to 100 percent, Human Review Accuracy improved to 100 percent, and all three agents completed on every case.

### 4:40-5:00 - Closing

The most important part of this project is that it shows the full production AI engineering loop.

I did not stop at building an agent. I designed an evaluation, created a golden dataset, added observability, measured failures, improved the system, and re-ran the benchmark.

That is the kind of workflow needed to make agentic AI systems reliable enough for real production use.

## Optional Closing Line

TrustLayer AI demonstrates AI evaluation, observability, monitoring, agent reliability, and human-in-the-loop escalation in a focused code-review use case.
