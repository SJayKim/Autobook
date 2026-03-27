---
source_id: 006
title: "LangSmith — Trace Using the REST API (POST /runs, PATCH /runs, Batch Ingestion)"
url: "https://docs.langchain.com/langsmith/trace-with-api"
type: docs
scraped_at: 2026-03-27
keywords: ["tracing", "runs"]
content_length: 5640
---

# LangSmith — Trace Using the REST API (POST /runs, PATCH /runs, Batch Ingestion)

## Overview

LangSmith provides two REST API approaches for tracing:
1. **Basic tracing** via `POST /runs` and `PATCH /runs/{run_id}` endpoints
2. **Batch ingestion** via `POST /runs/multipart` for higher throughput

> "We strongly recommend using the Python or TypeScript SDK to send traces to LangSmith instead of the REST API directly."

## Basic Tracing Approach

### Key Requirements

- Include your API key in request headers as `"x-api-key"`
- If linked to multiple workspaces, specify via `"x-tenant-id"` header
- Use **UUID v7** for run IDs (embeds timestamps for proper ordering)
- No need to manually set `dotted_order` or `trace_id` for basic tracing — system generates these automatically

### POST /runs — Create a Run

```python
import requests
from datetime import datetime, timezone
from langsmith import uuid7

headers = {
    "x-api-key": os.environ["LANGSMITH_API_KEY"],
    "x-tenant-id": os.environ["LANGSMITH_WORKSPACE_ID"]
}

def post_run(run_id, name, run_type, inputs, parent_id=None):
    data = {
        "id": run_id.hex,
        "name": name,
        "run_type": run_type,
        "inputs": inputs,
        "start_time": datetime.utcnow().isoformat(),
    }
    if parent_id:
        data["parent_run_id"] = parent_id.hex

    requests.post(
        "https://api.smith.langchain.com/runs",
        json=data,
        headers=headers
    )
```

### PATCH /runs/{run_id} — Update a Run with Outputs

```python
def patch_run(run_id, outputs):
    requests.patch(
        f"https://api.smith.langchain.com/runs/{run_id}",
        json={
            "outputs": outputs,
            "end_time": datetime.now(timezone.utc).isoformat(),
        },
        headers=headers,
    )
```

### Complete Parent-Child Example

```python
# Create parent run (root of trace)
parent_run_id = uuid7()
post_run(parent_run_id, "Chat Pipeline", "chain", {"question": question})

# Create child run (linked to parent)
child_run_id = uuid7()
post_run(child_run_id, "OpenAI Call", "llm", {"messages": messages}, parent_run_id)

# Execute and patch
chat_completion = client.chat.completions.create(...)
patch_run(child_run_id, chat_completion.dict())
patch_run(parent_run_id, {"answer": chat_completion.choices[0].message.content})
```

## Run Data Fields

| Field | Type | Description |
|---|---|---|
| `id` | UUID v7 | Unique identifier for the run |
| `name` | str | Descriptive name displayed in UI |
| `run_type` | str | `"chain"`, `"llm"`, `"tool"`, etc. |
| `inputs` | dict | Input data provided to the run |
| `outputs` | dict | Results produced by the run |
| `start_time` | ISO datetime | When the run began |
| `end_time` | ISO datetime | When the run completed |
| `parent_run_id` | UUID | Links child runs to their parent |
| `trace_id` | UUID | Root run ID for the entire trace |
| `dotted_order` | str | Hierarchical ordering (required for batch) |

## Batch Ingestion Approach (POST /runs/multipart)

For superior performance and rate limits. Requires `requests-toolbelt` and `uuid-utils`.

### dotted_order Format

A hierarchical string combining timestamps and UUIDs:
```
20240101T000000Z<parent-uuid>.20240101T000001Z<child-uuid>
```
- Parent and child entries separated by dots
- `trace_id` = UUID from the root (first) dotted_order segment

### Helper: construct_run

```python
from datetime import datetime, timezone
from uuid_utils.compat import uuid7
import uuid

def create_dotted_order(start_time=None, run_id=None):
    st = start_time or datetime.now(timezone.utc)
    id_ = run_id or uuid7()
    return f"{st.strftime('%Y%m%dT%H%M%S%fZ')}{id_}"

def construct_run(name, run_type, inputs, parent_dotted_order=None):
    start_time = datetime.now(timezone.utc)
    run_id = uuid7()
    run = {
        "id": str(run_id),
        "trace_id": str(run_id),
        "name": name,
        "start_time": start_time.isoformat(),
        "inputs": inputs,
        "run_type": run_type,
    }
    current_dotted_order = create_dotted_order(start_time, uuid.UUID(run["id"]))

    if parent_dotted_order:
        current_dotted_order = f"{parent_dotted_order}.{current_dotted_order}"
        run["trace_id"] = parent_dotted_order.split(".")[0].split("Z")[1]
        run["parent_run_id"] = parent_dotted_order.split(".")[-1].split("Z")[1]

    run["dotted_order"] = current_dotted_order
    return run
```

### Batch Ingestion Example

```python
# Create runs
parent_run = construct_run("Parent Run", "chain", {"question": "Tell me about France"})
child_run = construct_run("Child Run", "llm",
    {"question": "What is the capital of France?"},
    parent_dotted_order=parent_run["dotted_order"])

# POST to create
batch_ingest_runs(api_url, api_key, posts=[parent_run, child_run])

# PATCH to update with outputs
child_update = {**child_run, "end_time": ..., "outputs": {"answer": "Paris"}}
parent_update = {**parent_run, "end_time": ..., "outputs": {"summary": "..."}}
batch_ingest_runs(api_url, api_key, patches=[child_update, parent_update])
```

## Performance Notes

> "Though simpler, [basic tracing] is slower and subject to lower rate limits than batch ingestion."

Batch ingestion via `/runs/multipart` is recommended for production environments requiring higher throughput.
