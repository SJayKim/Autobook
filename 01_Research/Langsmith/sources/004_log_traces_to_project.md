---
source_id: 004
title: "LangSmith — Log Traces to Specific Project (Static & Dynamic Assignment)"
url: "https://docs.langchain.com/langsmith/log-traces-to-project"
type: docs
scraped_at: 2026-03-27
keywords: ["projects", "tracing"]
content_length: 4120
---

# LangSmith — Log Traces to Specific Project (Static & Dynamic Assignment)

## Overview

LangSmith organizes traces into projects. You can configure the target project statically via environment variables or dynamically at runtime.

## Static Configuration via Environment Variable

```bash
export LANGSMITH_PROJECT=my-custom-project
```

**Note:** The `LANGSMITH_PROJECT` flag is only supported in JS SDK versions >= 0.2.16. Use `LANGCHAIN_PROJECT` instead for older versions.

If the specified project does not exist, LangSmith automatically creates it when the first trace arrives.

## Dynamic Project Assignment at Runtime

Dynamic assignment takes precedence over environment variables and is useful when routing traces to different projects within a single application.

### Python: @traceable Decorator

```python
@traceable(
    run_type="llm",
    name="OpenAI Call Decorator",
    project_name="My Project"
)
def call_openai(messages: list[dict], model: str = "gpt-4.1-mini") -> str:
    return client.chat.completions.create(
        model=model,
        messages=messages,
    ).choices[0].message.content

# Override project at call time
call_openai(
    messages,
    langsmith_extra={"project_name": "My Overridden Project"},
)
```

### Python: RunTree

```python
from langsmith.run_trees import RunTree

rt = RunTree(
    run_type="llm",
    name="OpenAI Call RunTree",
    inputs={"messages": messages},
    project_name="My Project"
)
rt.end(outputs=chat_completion)
rt.post()
```

### Python: Wrapped OpenAI Client

```python
from langsmith import wrappers
wrapped_client = wrappers.wrap_openai(client)
wrapped_client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=messages,
    langsmith_extra={"project_name": "My Project"},
)
```

### TypeScript: traceable

```typescript
import { traceable } from "langsmith/traceable";

const traceableCallOpenAI = traceable(
    async (messages, model) => {
        const completion = await client.chat.completions.create({
            model: model,
            messages: messages,
        });
        return completion.choices[0].message.content;
    },
    {
        run_type: "llm",
        name: "OpenAI Call Traceable",
        project_name: "My Project"
    }
);

await traceableCallOpenAI(messages, "gpt-4.1-mini");
```

### TypeScript: RunTree

```typescript
import { RunTree } from "langsmith";

const rt = new RunTree({
    run_type: "llm",
    name: "OpenAI Call RunTree",
    inputs: { messages },
    project_name: "My Project"
});
```

## Multi-Destination Tracing with Replicas

Send traces simultaneously to multiple projects or workspaces using replicas.

### Environment Variable Configuration (Array format)

```bash
export LANGSMITH_RUNS_ENDPOINTS='[
  {"api_url": "https://api.smith.langchain.com", "api_key": "ls__key1", "project_name": "project-prod"},
  {"api_url": "https://api.smith.langchain.com", "api_key": "ls__key2", "project_name": "project-staging"}
]'
```

### Python: Runtime Replica Configuration

```python
from langsmith import traceable, tracing_context
from langsmith.run_trees import WriteReplica, ApiKeyAuth

@traceable
def my_pipeline(query: str) -> str:
    return f"Answer to: {query}"

replicas = [
    WriteReplica(
        api_url="https://api.smith.langchain.com",
        auth=ApiKeyAuth(api_key="ls__key_workspace_a"),
        project_name="project-prod",
    ),
    WriteReplica(
        api_url="https://api.smith.langchain.com",
        auth=ApiKeyAuth(api_key="ls__key_workspace_b"),
        project_name="project-staging",
        updates={"metadata": {"environment": "staging"}},
    ),
]

with tracing_context(replicas=replicas):
    my_pipeline("What is LangSmith?")
```

### Same-Server Project Replicas (No Auth Needed)

```python
with tracing_context(
    replicas=[
        WriteReplica(project_name="project-prod"),
        WriteReplica(
            project_name="project-staging",
            updates={"metadata": {"env": "staging"}}
        ),
    ]
):
    my_pipeline("What is LangSmith?")
```

## Key Considerations

- `LANGSMITH_RUNS_ENDPOINTS` cannot be combined with `LANGSMITH_ENDPOINT` in the same configuration.
- Replica errors do NOT affect primary traces; failed endpoints log errors without interrupting execution.
- Authentication credentials do NOT propagate across distributed traces; each service must configure its own replica credentials.
- The `updates` field allows per-replica customization of metadata and tags without modifying the primary trace.
