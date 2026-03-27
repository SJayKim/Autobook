---
source_id: 009
title: "LangSmith — Trace with OpenTelemetry (OTEL Integration, Attribute Mapping)"
url: "https://docs.langchain.com/langsmith/trace-with-opentelemetry"
type: docs
scraped_at: 2026-03-27
keywords: ["tracing", "runs", "tags and metadata"]
content_length: 5310
---

# LangSmith — Trace with OpenTelemetry (OTEL Integration, Attribute Mapping)

## Overview

LangSmith enables OpenTelemetry-based tracing for both LangChain applications and custom instrumented frameworks. This allows you to send traces from any OpenTelemetry-compatible application to LangSmith.

## Setup for LangChain Applications

### Installation

```bash
pip install "langsmith[otel]"
pip install langchain
```

**Requirements:** `langsmith>=0.3.18` (recommending `langsmith>=0.4.25` for critical fixes).

### Configuration

```bash
export LANGSMITH_OTEL_ENABLED=true
export LANGSMITH_TRACING=true
export LANGSMITH_ENDPOINT=https://api.smith.langchain.com
export LANGSMITH_API_KEY=<your_langsmith_api_key>
export LANGSMITH_WORKSPACE_ID=<workspace_id>  # If needed for multi-workspace accounts
```

For EU region: use `eu.api.smith.langchain.com`.

### Example

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
model = ChatOpenAI()
chain = prompt | model

result = chain.invoke({"topic": "programming"})
```

## Setup for Non-LangChain Applications

### Installation

```bash
pip install openai opentelemetry-sdk opentelemetry-exporter-otlp
```

### OTEL Endpoint Configuration

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=https://api.smith.langchain.com/otel
export OTEL_EXPORTER_OTLP_HEADERS="x-api-key=<your_langsmith_api_key>"
# Optional: specify project name
export OTEL_EXPORTER_OTLP_HEADERS="x-api-key=<key>,Langsmith-Project=<project_name>"
```

### Implementation Example

```python
from openai import OpenAI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

otlp_exporter = OTLPSpanExporter(timeout=10)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

tracer = trace.get_tracer(__name__)

def call_openai():
    with tracer.start_as_current_span("call_open_ai") as span:
        # LangSmith-specific attributes
        span.set_attribute("langsmith.span.kind", "LLM")
        span.set_attribute("langsmith.metadata.user_id", "user_123")

        # GenAI standard attributes
        span.set_attribute("gen_ai.system", "OpenAI")
        span.set_attribute("gen_ai.request.model", "gpt-4.1-mini")
        span.set_attribute("llm.request.type", "chat")

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a haiku about recursion."}
        ]

        for i, message in enumerate(messages):
            span.set_attribute(f"gen_ai.prompt.{i}.content", str(message["content"]))
            span.set_attribute(f"gen_ai.prompt.{i}.role", str(message["role"]))

        completion = client.chat.completions.create(
            model="gpt-4.1-mini", messages=messages
        )

        span.set_attribute("gen_ai.response.model", completion.model)
        span.set_attribute("gen_ai.completion.0.content", str(completion.choices[0].message.content))
        span.set_attribute("gen_ai.usage.prompt_tokens", completion.usage.prompt_tokens)
        span.set_attribute("gen_ai.usage.completion_tokens", completion.usage.completion_tokens)

        return completion.choices[0].message
```

## OpenTelemetry Attribute Mapping

### Core LangSmith Attributes

| OpenTelemetry Attribute | LangSmith Field | Notes |
|---|---|---|
| `langsmith.trace.name` | Run name | Overrides span name |
| `langsmith.span.kind` | Run type | `llm`, `chain`, `tool`, `retriever`, `embedding`, `prompt`, `parser` |
| `langsmith.trace.session_id` | Session ID | Groups related traces into threads |
| `langsmith.span.tags` | Tags | Comma-separated string |
| `langsmith.metadata.{key}` | `metadata.{key}` | Custom metadata key-value pairs |

### GenAI Standard Attributes

| OpenTelemetry Attribute | LangSmith Field |
|---|---|
| `gen_ai.system` | `metadata.ls_provider` |
| `gen_ai.prompt.{n}.role` | `inputs.messages[n].role` |
| `gen_ai.prompt.{n}.content` | `inputs.messages[n].content` |
| `gen_ai.completion.{n}.content` | `outputs.messages[n].content` |
| `gen_ai.request.model` | `invocation_params.model` |
| `gen_ai.usage.input_tokens` | `usage_metadata.input_tokens` |
| `gen_ai.usage.output_tokens` | `usage_metadata.output_tokens` |

## OpenTelemetry Collector Fan-Out

Use an OTEL Collector to route traces to multiple destinations simultaneously:

### Collector YAML Configuration

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318

exporters:
  otlphttp/langsmith:
    endpoint: https://api.smith.langchain.com/otel/v1/traces
    headers:
      x-api-key: ${env:LANGSMITH_API_KEY}
      Langsmith-Project: my_project
  otlphttp/other_provider:
    endpoint: https://otel.your-provider.com/v1/traces
    headers:
      api-key: ${env:OTHER_PROVIDER_API_KEY}

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlphttp/langsmith, otlphttp/other_provider]
```

## LangSmith SDK Helper for OTEL

Simplified configuration using the built-in helper:

```python
from langsmith.integrations.otel import configure

configure(project_name="my-project")
# Now all LangChain/LangGraph calls are automatically traced via OTEL
```

## Environment Variable: LANGSMITH_OTEL_ONLY

```bash
LANGSMITH_OTEL_ONLY="true"  # Send only to custom OTEL endpoint, not LangSmith
```
