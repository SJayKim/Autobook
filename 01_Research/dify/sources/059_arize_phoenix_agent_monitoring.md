---
source_id: "059"
title: "Dify x Arize: How to Evaluate, Monitor, and Improve Agents"
url: "https://dify.ai/blog/dify-arize-how-to-evaluate-monitor-and-improve-agents"
type: "blog"
scraped_at: "2026-03-27"
keywords: ["Dify Arize Phoenix integration", "Dify observability", "Dify annotation and feedback"]
content_length: 5680
---

# Dify x Arize: How to Evaluate, Monitor, and Improve Agents

At Dify, we're committed to helping teams build reliable AI applications fast. To make it easier to evaluate, monitor, and improve agents, we've partnered with Arize to bring their observability tools -- Phoenix and AX -- into the Dify ecosystem.

## Introduction

Dify is an open source, model agnostic platform for agentic AI. It unifies visual workflows, a full RAG Knowledge Pipeline, and LLMOps so teams ship production ready agents fast, in self hosted or cloud environments.

But speed alone isn't enough -- you need to know your applications are sound. As your AI applications and agents get more complex, keeping them accurate and efficient becomes a real challenge.

By leveraging observability features, you can begin to answer questions like:
- Are your agents taking the most efficient paths?
- Is your chosen model the right one in terms of token usage, latency, and cost?
- How well are your retrieval steps contributing to output quality?

Observability isn't just a production concern; it's also essential during development, helping you catch silent errors, monitor costs, and understand LLM and agent behavior before issues reach your users. And once your application is live, that same visibility ensures it stays reliable as you scale.

This is where products like Arize Phoenix and Arize AX come in, giving you one-click observability, performance insights, experimentation tools, and evaluation pipelines that let you bring Dify applications into production with confidence.

## Arize Phoenix & Dify

When you're building with Dify, you get the flexibility to spin up LLM-powered workflows in no time. But as your agents get more complex, keeping them accurate and efficient becomes a real challenge.

Arize-Phoenix is your open-source observability layer for LLM apps, plugging right into your Dify workflows so you can actually see what your agents are doing. Every model call, tool invocation, and chain step your agents execute gets traced automatically, so you're not left guessing why a prompt tweak worked -- or made things worse. Inputs, outputs, latencies, and metadata all show up, making it easy to debug and optimize without hunting through logs.

Phoenix goes beyond just tracing. It lets you annotate your collected traces, build structured test datasets, create tailored evaluations, and run tests to measure exactly how your agents are performing before you ship changes.

### Phoenix + Dify: Sample Use Case for Improving Your Agents

1. **Configure your Dify application with Phoenix** -- In Dify's monitoring tab, drop in your Phoenix credentials, and tracing is good to go.
2. **Collect traces** -- Run your Dify agent as usual, and Phoenix will automatically capture structured traces for every conversation and task.
3. **Build a dataset for evaluation** -- Hop into Phoenix, grab traces that capture key user flows, tricky edge cases, and examples where your agent struggles. Save these examples as a dataset so you can use it as a reference point to evaluate performance changes over time.
4. **Iterate and Experiment** -- Use Phoenix's LLM span replay and prompt playground to test prompt tweaks and model changes against your dataset. Compare outputs side by side to see how your changes affect results on real examples.
5. **Define and Run Evaluators** -- Set up and run evaluators such as correctness, helpfulness, or relevance checks on your experiment results.
6. **Deploy with confidence** -- Update your Dify application with tested changes. Keep tracing, evaluating, and refining with Phoenix as your agents grow.

## Arize AX & Dify

While Arize Phoenix is a fantastic tool for iterating quickly -- tracing your agents, testing prompt and model changes, and running structured offline evaluations -- there comes a point when you need continuous visibility as your LLM workflows scale in production.

Arize AX is the answer to scalability. It builds on Phoenix's observability with live evaluations on production data, dashboards to watch your metrics over time, and monitors that flag unexpected changes as they happen.

### Arize + Dify: Sample Use Case for Monitoring and Iterating on Agents

1. **Connect your Dify app to Arize** -- In Dify's monitoring tab, enter your Arize credentials, traces start flowing automatically.
2. **Stream production data into Arize** -- As users interact with your Dify workflows, Arize captures structured traces in real time.
3. **Set up online evaluations** -- Spin up online evaluators like accuracy, safety, or user frustration checks to automatically score your agent's outputs on live traffic.
4. **Monitor key metrics on dashboards** -- Track evaluation scores, token usage, latency, and cost trends in one place.
5. **Configure alerts and monitors** -- Set up monitors and alerts to catch drifts, regressions, or sudden spikes before they reach end users.
6. **Iterate with confidence** -- Use insights from dashboards and alerts to guide prompt or model tweaks in Dify.

## Getting Started

- **Arize Phoenix**: For fast development and iteration mode.
- **Arize AX**: For production applications needing continuous monitoring on live traffic.
