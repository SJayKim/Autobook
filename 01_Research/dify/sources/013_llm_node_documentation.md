---
source_id: "013"
title: "LLM Node - Dify Docs"
url: "https://docs.dify.ai/en/use-dify/nodes/llm"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify workflow nodes", "Dify workflow"]
content_length: 3680
---

# LLM Node - Dify Docs

The LLM node invokes language models to process text, images, and documents. It sends prompts to your configured models and captures their responses, supporting structured outputs, context management, and multimodal inputs.

Configure at least one model provider in System Settings > Model Providers before using LLM nodes.

## Model Selection and Parameters

Choose from any model provider you've configured. Different models excel at different tasks - GPT-4 and Claude 3.5 handle complex reasoning well but cost more, while GPT-3.5 Turbo balances capability with affordability. For local deployment, use Ollama, LocalAI, or Xinference.

Model parameters control response generation. Temperature ranges from 0 (deterministic) to 1 (creative). Top P limits word choices by probability. Frequency Penalty reduces repetition. Presence Penalty encourages new topics. You can also use presets: Precise, Balanced, or Creative.

## Prompt Configuration

Your interface adapts based on model type. Chat models use message roles (System for behavior, User for input, Assistant for examples), while completion models use simple text continuation. Reference workflow variables in prompts using double curly braces: {{variable_name}}. Variables are replaced with actual values before reaching the model.

```
System: You are a technical documentation expert.
User: {{user_input}}
```

## Context Variables

Context variables inject external knowledge while preserving source attribution. This enables RAG applications where LLMs answer questions using your specific documents.

Connect a Knowledge Retrieval node's output to your LLM node's context input, then reference it:

```
Answer using only this context:
{{knowledge_retrieval.result}}

Question: {{user_question}}
```

When using context variables from knowledge retrieval, Dify automatically tracks citations so users see information sources.

## Structured Outputs

Force models to return specific data formats like JSON for programmatic use. Configure through three methods:

- Visual Editor: User-friendly interface for simple structures. Add fields with names and types, mark required fields, set descriptions.
- JSON Schema: Write schemas directly for complex structures with nested objects, arrays, and validation rules.
- AI Generation: Describe needs in plain language and let AI generate the schema.

Models with native JSON support handle structured outputs reliably. For others, Dify includes the schema in prompts, but results may vary.

## Memory and File Processing

Enable Memory to maintain context across multiple LLM calls within a chatflow conversation. When enabled, previous interactions will be included in subsequent prompts as formatted user-assistant outputs. You can customize what goes into the user prompts by editing the USER template. Memory is node-specific and doesn't persist between different conversations.

For File Processing, add file variables to prompts for multimodal models. GPT-4V handles images, Claude processes PDFs directly, while other models might need preprocessing.

### Vision Configuration

When processing images, you can control the detail level:
- High detail - Better accuracy for complex images but uses more tokens
- Low detail - Faster processing with fewer tokens for simple images

## Jinja2 Template Support

LLM prompts support Jinja2 templating for advanced variable handling. When you use Jinja2 mode, you can use loops, conditionals, and complex data transformations within prompts:

```
{% for item in search_results %}
{{ loop.index }}. {{ item.title }}: {{ item.content }}
{% endfor %}
```

## Streaming Output

LLM nodes support streaming output by default. Each text chunk is yielded as a RunStreamChunkEvent, enabling real-time response display. File outputs (images, documents) are processed and saved automatically during streaming.

## Error Handling

Configure retry behavior for failed LLM calls. Set maximum retry attempts, intervals between retries, and backoff multipliers. Define fallback strategies like default values, error routing, or alternative models when retries aren't sufficient.
