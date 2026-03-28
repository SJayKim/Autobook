---
source_id: "062"
title: "Observability and tracing for Dify - Langfuse"
url: "https://langfuse.com/integrations/no-code/dify"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify LangSmith integration", "Dify Langfuse integration", "Dify observability"]
content_length: 2680
---

# Dify - Observability & Metrics for Your LLM Apps (Langfuse Integration)

Dify (GitHub: langgenius/dify) is an open-source LLM app development platform which is natively integrated with Langfuse. With the native integration, you can use Dify to quickly create complex LLM applications and then use Langfuse to monitor and improve them.

## Setup

1. Create project in Langfuse and get API credentials in project settings.
2. In Dify: Navigate to Monitoring settings of your Dify app.
3. Add Langfuse via Third-party LLMOps provider menu.
4. Invoke Dify application via UI or API to start capturing traces and metrics in Langfuse.

## Mapping of Dify to Langfuse

The integration automatically maps the following fields from Dify to Langfuse:

| Dify | Langfuse |
| --- | --- |
| user | userId |
| message_id | trace_id |
| conversation_id | sessionId |
| (app name) | trace.name |
| type of application, type of model | tags |

## Langfuse Prompt Management

The Langfuse Prompt Management Plugin (community maintained) lets you use prompts that are managed and versioned in Langfuse in your Dify applications, enhancing your LLM application development workflow. Key features include:

- **Get Prompt:** Fetch specific prompts managed in Langfuse.
- **Search Prompts:** Search for prompts in Langfuse using various filters.
- **Update Prompt:** Create new versions of prompts in Langfuse and set tags/labels.

This integration streamlines the process of managing and versioning your prompts, contributing to more efficient development and iteration cycles.

## About Dify

Dify is an open-source LLM app development platform. Its intuitive interface combines AI workflow, RAG pipeline, agent capabilities, model management, observability features and more, letting you quickly go from prototype to production. Core features:

1. **Workflow**: Build and test powerful AI workflows on a visual canvas.
2. **Comprehensive model support**: Seamless integration with hundreds of proprietary / open-source LLMs from dozens of inference providers and self-hosted solutions.
3. **Prompt IDE**: Intuitive interface for crafting prompts, comparing model performance.
4. **RAG Pipeline**: Extensive RAG capabilities from document ingestion to retrieval.
5. **Agent capabilities**: Define agents based on LLM Function Calling or ReAct, with 50+ built-in tools.
6. **LLMOps**: Monitor and analyze application logs and performance over time. Continuously improve prompts, datasets, and models based on production data and annotations.
7. **Backend-as-a-Service**: All offerings come with corresponding APIs for integration.
