---
source_id: 011
title: "LangSmith — Run Types Reference and LLM Call Logging (run_type, inputs, outputs, usage_metadata)"
url: "https://docs.langchain.com/langsmith/log-llm-trace"
type: docs
scraped_at: 2026-03-27
keywords: ["runs", "tracing"]
content_length: 3120
---

# LangSmith — Run Types Reference and LLM Call Logging

## Run Type Values

LangSmith defines the following `run_type` values:

| run_type | Description |
|---|---|
| `"llm"` | Language model invocations (enables token counting, cost calc, Playground) |
| `"chain"` | Orchestration / pipeline / workflow logic |
| `"tool"` | Tool or function calls executed by an agent |
| `"retriever"` | Document retrieval operations (vector search, etc.) |
| `"embedding"` | Text embedding operations |
| `"prompt"` | Prompt formatting / template rendering |
| `"parser"` | Output parsing operations |

The run_type is specified via `@traceable(run_type="llm")`, `RunTree(run_type="chain")`, or the REST API `run_type` field.

## LLM Run Logging Requirements

To create a fully functional LLM trace with token counting and cost calculation, four things are needed:

1. **Set `run_type="llm"`** — Enables proper LLM-specific rendering, token/cost display, and Playground support
2. **Format inputs/outputs correctly** — Use OpenAI, Anthropic, or LangChain message formats
3. **Provide `ls_provider` and `ls_model_name`** in metadata — Enables cost tracking and model selection in Playground
4. **Include `usage_metadata`** — Enables token counting and cost calculation

## Message Format Structure

Messages follow this pattern:

```python
inputs = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "I'd like to book a table for two."},
]

output = {
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": "Sure, what time would you like?"
            }
        }
    ]
}
```

**Supported roles:** `system`, `reasoning`, `user`, `assistant`, `tool`

## Python Example: Custom LLM Tracing

```python
from langsmith import traceable

@traceable(
    run_type="llm",
    metadata={"ls_provider": "my_provider", "ls_model_name": "my_model"}
)
def chat_model(messages: list):
    # Your LLM call here
    return output

chat_model(inputs)
```

## Usage Metadata Fields

| Field | Type | Purpose |
|---|---|---|
| `input_tokens` | int | Prompt/input token count |
| `output_tokens` | int | Completion/output token count |
| `total_tokens` | int | Combined total (optional) |
| `input_token_details` | object | Breakdown by type (cache, audio, text, image) |
| `output_token_details` | object | Breakdown (reasoning, audio, text, image) |
| `input_cost` | float | For non-linear pricing models |
| `output_cost` | float | For non-linear pricing models |
| `total_cost` | float | Total cost |

## Streaming Models

Use `reduce_fn` to aggregate streaming chunks into a standard format:

```python
def _reduce_chunks(chunks: list):
    all_text = "".join([chunk["choices"][0]["message"]["content"] for chunk in chunks])
    return {"choices": [{"message": {"content": all_text, "role": "assistant"}}]}

@traceable(
    run_type="llm",
    reduce_fn=_reduce_chunks,
    metadata={"ls_provider": "my_provider", "ls_model_name": "my_model"}
)
def my_streaming_chat_model(messages: list):
    for chunk in ["Hello, " + messages[1]["content"]]:
        yield {"choices": [{"message": {"content": chunk, "role": "assistant"}}]}
```

## process_inputs / process_outputs

Use these parameters on `@traceable` to convert custom formats to LangSmith-compatible structures before logging:

```python
def process_inputs(inputs):
    # Transform inputs to LangSmith format
    return {"messages": inputs["raw_messages"]}

def process_outputs(outputs):
    # Transform outputs to LangSmith format
    return {"choices": [{"message": {"content": outputs["text"]}}]}

@traceable(
    run_type="llm",
    process_inputs=process_inputs,
    process_outputs=process_outputs
)
def my_llm(inputs):
    ...
```

## Time-to-First-Token

LangSmith automatically calculates this metric for streaming runs using `traceable` or SDK wrappers. When using the RunTree API directly, add a `new_token` event to populate this measurement.
