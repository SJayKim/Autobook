---
source_id: 005
title: "LangSmith — Adding Metadata and Tags to Traces"
url: "https://docs.langchain.com/langsmith/add-metadata-tags"
type: docs
scraped_at: 2026-03-27
keywords: ["tags and metadata", "tracing", "runs"]
content_length: 3480
---

# LangSmith — Adding Metadata and Tags to Traces

## Overview

LangSmith enables developers to attach arbitrary metadata and tags to traces for enhanced organization and context. "Tags are strings that can be used to categorize or label a trace. Metadata is a dictionary of key-value pairs that can be used to store additional information about a trace."

These additions help associate supplementary details with traces, including execution environment, initiating user, or correlation identifiers.

## Method 1: Static Declaration via @traceable Decorator

```python
import langsmith as ls

@ls.traceable(
    run_type="llm",
    name="OpenAI Call Decorator",
    tags=["my-tag"],
    metadata={"my-key": "my-value"}
)
def call_openai(messages: list[dict], model: str = "gpt-4.1-mini") -> str:
    return client.chat.completions.create(
        model=model,
        messages=messages,
    ).choices[0].message.content
```

## Method 2: Dynamic Updates During Execution

Within decorated functions, modify metadata and tags at runtime using `get_current_run_tree()`:

```python
import langsmith as ls

@ls.traceable
def my_function():
    rt = ls.get_current_run_tree()
    rt.metadata["some-conditional-key"] = "some-val"
    rt.tags.extend(["another-tag"])
    # ... rest of function
```

## Method 3: Invocation-Time Parameters (langsmith_extra)

Pass additional metadata and tags when calling functions:

```python
call_openai(
    messages,
    langsmith_extra={"tags": ["my-other-tag"], "metadata": {"my-other-key": "my-value"}}
)
```

## Method 4: Context-Based Defaults (tracing_context)

Use `tracing_context` to establish default metadata for ALL child spans without creating a span itself:

```python
import langsmith as ls

with ls.tracing_context(metadata={"default-key": "default-value"}):
    call_openai(messages)
```

## Method 5: trace Context Manager

Create explicit spans with metadata and tags:

```python
import langsmith as ls
from langsmith.wrappers import wrap_openai
import openai

client = wrap_openai(openai.Client())

with ls.trace(
    name="OpenAI Call Trace",
    run_type="llm",
    inputs={"messages": messages},
    tags=["my-tag"],
    metadata={"my-key": "my-value"},
) as rt:
    chat_completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
    )
    rt.end(outputs={"output": chat_completion})
```

## Method 6: Wrapped Client Integration (wrap_openai)

Apply metadata and tags through OpenAI client wrappers:

```python
from langsmith.wrappers import wrap_openai

patched_client = wrap_openai(
    client, tracing_extra={"metadata": {"my-key": "my-value"}, "tags": ["a-tag"]}
)
```

## TypeScript Equivalents

Similar patterns apply in TypeScript using `traceable` and `wrapOpenAI`:

```typescript
import { traceable } from "langsmith/traceable";
import { wrapOpenAI } from "langsmith/wrappers";
import { getCurrentRunTree } from "langsmith/traceable";
import OpenAI from "openai";

// Static tags and metadata
const myFunc = traceable(
    async (input: string) => {
        // Dynamic updates
        const rt = getCurrentRunTree();
        rt.metadata["dynamic-key"] = "dynamic-val";
        rt.tags.push("runtime-tag");
        return input;
    },
    {
        name: "My Function",
        tags: ["static-tag"],
        metadata: { "static-key": "static-value" }
    }
);

// Wrapped client
const wrappedClient = wrapOpenAI(new OpenAI(), {
    tracingExtra: { metadata: { "my-key": "my-value" }, tags: ["a-tag"] }
});
```

## Filtering Behavior

- **Tags**: Filterable in the LangSmith UI to categorize, search, and group runs.
- **Metadata**: Filterable as key-value pairs in the LangSmith UI.
- LangSmith indexes up to **100 unique keys per run**, with each key having a **250 character limit** per value. Text exceeding these limits will not be indexed.
- Common use cases for metadata: `{"user_id": "...", "session_id": "...", "version": "1.2.3", "environment": "production"}`
