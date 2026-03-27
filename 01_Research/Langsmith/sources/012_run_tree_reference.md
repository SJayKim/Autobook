---
source_id: 012
title: "LangSmith — RunTree API Reference (Python & JS, parent-child hierarchy)"
url: "https://docs.smith.langchain.com/reference/python/run_trees/langsmith.run_trees.RunTree"
type: docs
scraped_at: 2026-03-27
keywords: ["runs", "tracing"]
content_length: 2650
---

# LangSmith — RunTree API Reference

## Overview

`RunTree` is the low-level Python class for manually constructing trace hierarchies. It provides explicit control over run creation, parent-child linking, and submission to LangSmith.

**Key distinction**: `RunTree` does NOT require `LANGSMITH_TRACING=true` — it only needs `LANGSMITH_API_KEY`.

## Constructor Parameters

| Parameter | Type | Description |
|---|---|---|
| `name` | str | Display name in LangSmith UI |
| `run_type` | str | `"llm"`, `"chain"`, `"tool"`, `"retriever"`, `"embedding"`, `"prompt"`, `"parser"` |
| `inputs` | dict | Input data for the run |
| `outputs` | dict | Output data (set later via `.end()`) |
| `project_name` | str | Target project (default: `"default"`) |
| `parent_run_id` | UUID | Links this run as a child of another run |
| `trace_id` | UUID | Root run ID for the trace (auto-set for children) |
| `dotted_order` | str | Hierarchical ordering string |
| `tags` | list[str] | Tags to attach |
| `metadata` | dict | Key-value metadata |
| `client` | Client | Custom LangSmith client instance |

## Key Methods

### post() / postRun()
Submits the run to LangSmith to create it:
```python
pipeline = RunTree(name="Chat Pipeline", run_type="chain", inputs={"question": q})
pipeline.post()
```

### patch() / patchRun()
Updates an existing run (typically with outputs and end_time):
```python
pipeline.end(outputs={"answer": "Paris"})
pipeline.patch()
```

### end()
Sets outputs and end_time on the run (does not submit — call patch() after):
```python
pipeline.end(outputs={"answer": "Paris"}, error=None)
```

### create_child() / createChild()
Creates and returns a child RunTree linked to this run:
```python
child_llm_run = pipeline.create_child(
    name="OpenAI Call",
    run_type="llm",
    inputs={"messages": messages},
)
child_llm_run.post()
```

### to_headers()
Returns HTTP headers for distributed tracing context propagation:
```python
headers = run_tree.to_headers()
# {"langsmith-trace": "...", "baggage": "..."}
```

### fromHeaders() (class method, JS/TS)
Reconstructs a RunTree from incoming HTTP headers:
```typescript
const runTree = RunTree.fromHeaders(req.headers);
```

## Properties

| Property | Description |
|---|---|
| `id` | UUID v7 of this run |
| `trace_id` | UUID of the root run in this trace |
| `parent_run_id` | UUID of the parent run (None for root) |
| `dotted_order` | Hierarchical position string |
| `child_runs` | List of child RunTree objects |
| `tags` | List of tag strings |
| `metadata` | Dict of metadata key-value pairs |

## Parent-Child Hierarchy Example

```python
from langsmith.run_trees import RunTree

# Root run (trace)
root = RunTree(name="Pipeline", run_type="chain", inputs={"query": "..."})
root.post()

# Child run (span)
llm_span = root.create_child(name="LLM Call", run_type="llm", inputs={"messages": [...]})
llm_span.post()

# Another child (sibling to llm_span)
tool_span = root.create_child(name="Tool Call", run_type="tool", inputs={"tool": "search"})
tool_span.post()

# End spans and submit
llm_span.end(outputs={"content": "response text"})
llm_span.patch()

tool_span.end(outputs={"result": "search results"})
tool_span.patch()

root.end(outputs={"final_answer": "..."})
root.patch()
```

## Trace Structure Visualization

```
Root Run (chain)  ← trace_id = root.id
├── LLM Call (llm)     ← parent_run_id = root.id
│   └── ...
└── Tool Call (tool)   ← parent_run_id = root.id
    └── ...
```

## get_current_run_tree()

Helper function to retrieve the active RunTree within a `@traceable` decorated function:

```python
from langsmith.run_helpers import get_current_run_tree
import langsmith as ls

@ls.traceable
def my_func():
    rt = get_current_run_tree()
    rt.metadata["dynamic-key"] = "value"  # Mutate current run
    rt.tags.extend(["runtime-tag"])
```
