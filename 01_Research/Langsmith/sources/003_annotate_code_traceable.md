---
source_id: 003
title: "LangSmith Custom Instrumentation — @traceable, wrap_openai, RunTree, trace context manager"
url: "https://docs.langchain.com/langsmith/annotate-code"
type: docs
scraped_at: 2026-03-27
keywords: ["tracing", "runs"]
content_length: 5890
---

# LangSmith Custom Instrumentation — @traceable, wrap_openai, RunTree, trace context manager

## Overview

LangSmith enables precise control over function tracing without requiring code restructuring. The platform offers several approaches to instrument your applications and capture execution details.

## Prerequisites

Enable tracing by setting environment variables:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="<your-api-key>"
```

By default, traces log to a `"default"` project. The `LANGSMITH_TRACING` variable does NOT affect `RunTree` objects or direct API calls — those operate independently.

## Method 1: @traceable Decorator / Wrapper (Recommended)

The `@traceable` decorator (Python) or `traceable` wrapper (TypeScript) instruments individual functions with minimal code changes. LangSmith automatically manages context propagation across nested function calls.

### Python Example

```python
from langsmith import traceable
from openai import Client

openai = Client()

@traceable
def format_prompt(subject):
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"What's a good name for a store that sells {subject}?"}
    ]

@traceable(run_type="llm")
def invoke_llm(messages):
    return openai.chat.completions.create(
        messages=messages, model="gpt-4.1-mini", temperature=0
    )

@traceable
def parse_output(response):
    return response.choices[0].message.content

@traceable
def run_pipeline():
    messages = format_prompt("colorful socks")
    response = invoke_llm(messages)
    return parse_output(response)

run_pipeline()
```

### TypeScript Example

```typescript
import { traceable } from "langsmith/traceable";
import OpenAI from "openai";

const openai = new OpenAI();

const formatPrompt = traceable((subject: string) => {
    return [
        { role: "system" as const, content: "You are a helpful assistant." },
        { role: "user" as const, content: `What's a good name for a store that sells ${subject}?` },
    ];
}, { name: "formatPrompt" });

const invokeLLM = traceable(
    async ({ messages }: { messages: { role: string; content: string }[] }) => {
        return openai.chat.completions.create({
            model: "gpt-4.1-mini", messages, temperature: 0,
        });
    },
    { run_type: "llm", name: "invokeLLM" }
);

const runPipeline = traceable(
    async () => {
        const messages = await formatPrompt("colorful socks");
        const response = await invokeLLM({ messages });
        return response.choices[0].message.content;
    },
    { name: "runPipeline" }
);

await runPipeline();
```

**Key Point:** When wrapping synchronous functions with `traceable` in TypeScript, use `await` when calling them to ensure proper trace logging.

## Method 2: trace Context Manager (Python)

The `trace` context manager provides fine-grained control over specific code blocks without decorator syntax.

```python
import openai
import langsmith as ls
from langsmith.wrappers import wrap_openai

client = wrap_openai(openai.Client())

@ls.traceable(run_type="tool", name="Retrieve Context")
def my_tool(question: str) -> str:
    return "During this morning's meeting, we solved all world conflict."

app_inputs = {"input": "Can you summarize this morning's meetings?"}

with ls.trace("Chat Pipeline", "chain", project_name="my_test", inputs=app_inputs) as rt:
    output = chat_pipeline("Can you summarize this morning's meetings?")
    rt.end(outputs={"output": output})
```

## Method 3: RunTree API (Low-Level, Explicit Control)

For explicit control, use the `RunTree` API to manually construct trace hierarchies. This method requires `LANGSMITH_API_KEY` but NOT `LANGSMITH_TRACING`.

### Python Example

```python
import openai
from langsmith.run_trees import RunTree

question = "Can you summarize this morning's meetings?"

# Create root run
pipeline = RunTree(
    name="Chat Pipeline",
    run_type="chain",
    inputs={"question": question}
)
pipeline.post()

# Create child run
messages = [{"role": "user", "content": question}]
child_llm_run = pipeline.create_child(
    name="OpenAI Call",
    run_type="llm",
    inputs={"messages": messages},
)
child_llm_run.post()

client = openai.Client()
chat_completion = client.chat.completions.create(
    model="gpt-4.1-mini", messages=messages
)

child_llm_run.end(outputs=chat_completion)
child_llm_run.patch()
pipeline.end(outputs={"answer": chat_completion.choices[0].message.content})
pipeline.patch()
```

### TypeScript Example

```typescript
import OpenAI from "openai";
import { RunTree } from "langsmith";

const question = "Can you summarize this morning's meetings?";

const pipeline = new RunTree({
    name: "Chat Pipeline",
    run_type: "chain",
    inputs: { question }
});
await pipeline.postRun();

const childRun = await pipeline.createChild({
    name: "OpenAI Call",
    run_type: "llm",
    inputs: { messages },
});
await childRun.postRun();

const client = new OpenAI();
const chatCompletion = await client.chat.completions.create({
    model: "gpt-4.1-mini", messages,
});

childRun.end(chatCompletion);
await childRun.patchRun();
pipeline.end({ outputs: { answer: chatCompletion.choices[0].message.content } });
await pipeline.patchRun();
```

## Ensuring Trace Submission Before Exit

LangSmith uses background threads for trace delivery. Call `flush()` before application exit:

```python
from langsmith import Client

client = Client()

@traceable(client=client)
async def my_traced_func():
    pass

try:
    await my_traced_func()
finally:
    await client.flush()
```

## @traceable Parameters Summary

| Parameter | Type | Description |
|---|---|---|
| `run_type` | str | Run type: `"llm"`, `"chain"`, `"tool"`, `"retriever"`, etc. |
| `name` | str | Display name in LangSmith UI |
| `tags` | list[str] | Tags to attach to this run |
| `metadata` | dict | Key-value metadata for this run |
| `project_name` | str | Target project (overrides env var) |
| `process_inputs` | callable | Transform inputs before logging |
| `process_outputs` | callable | Transform outputs before logging |
| `client` | Client | Custom LangSmith client instance |
