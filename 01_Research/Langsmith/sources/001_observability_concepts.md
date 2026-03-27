---
source_id: 001
title: "LangSmith Observability Concepts — Traces, Runs, Projects, Tags, Metadata"
url: "https://docs.langchain.com/langsmith/observability-concepts"
type: docs
scraped_at: 2026-03-27
keywords: ["tracing", "runs", "projects", "tags and metadata"]
content_length: 1842
---

# LangSmith Observability Concepts — Traces, Runs, Projects, Tags, Metadata

## Core Definitions

**Traces**: A trace is "a collection of runs for a single operation." It captures the complete sequence from input through processing to output, with runs bound together by a unique trace ID. Each trace has a maximum capacity of 25,000 runs.

**Runs**: Described as "a span representing a single unit of work or operation," runs can represent LLM calls, chain operations, prompt formatting, or lambda invocations. The documentation draws a parallel to OpenTelemetry spans for familiarity.

**Projects**: These function as "a collection of traces" that serves as a container for traces related to a single application or service.

## Organizational Concepts

**Threads**: A thread represents "a sequence of traces representing a single conversation." Multi-turn conversations link individual traces through special metadata keys (`session_id`, `thread_id`, or `conversation_id`).

**Tags**: These are "collections of strings" attached to runs for categorizing, filtering, and grouping runs within the UI.

**Metadata**: Defined as "a collection of key-value pairs," metadata stores additional contextual information about runs, such as application version or environment details.

## Data Architecture

The documentation shows runs organized hierarchically within traces, which aggregate into projects. Feedback mechanisms score individual runs, while the system automatically retains trace data for 400 days before permanent deletion.

## Run Types

LangSmith supports the following run types: `llm`, `chain`, `tool`, `retriever`, `embedding`, `prompt`, `parser`. The run_type field categorizes each span by its functional role in the pipeline.

## Trace Hierarchy

- **Root run** (= trace): The top-level run that represents the full request. Its ID is also the `trace_id`.
- **Child runs** (= spans): Nested runs created within a parent run. Each child links back via `parent_run_id`.
- **dotted_order**: A hierarchical string combining timestamps and UUIDs that encodes both sequence and depth (e.g., `20240101T000000Z<parent-uuid>.20240101T000001Z<child-uuid>`).
