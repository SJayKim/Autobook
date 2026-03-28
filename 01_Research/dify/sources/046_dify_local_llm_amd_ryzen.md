---
source_id: "046"
title: "Harnessing Dify + Local LLMs on AMD Ryzen AI PCs for Private Workflows"
url: "https://www.amd.com/en/developer/resources/technical-articles/2025/harnessing-dify-and-local-llms-on-ryzen-ai-pcs-for-private-workf.html"
type: "tutorial"
scraped_at: "2026-03-27"
keywords: ["Dify local model deployment", "Dify self-hosted", "local LLM", "private AI workflow"]
content_length: 4650
---

This AMD technical article demonstrates using Dify with locally running LLMs on AMD Ryzen AI PCs via Lemonade Server for fully private AI workflows.

What Is Dify?

Dify is an open-source platform designed to make building AI applications powered by large language models easy. It lets you design workflows visually with nodes (inputs, retrieval, agents, tools) and swap models without rewriting code.

Key features:
- Visual Workflow Builder: Drag-and-drop interface for designing AI pipelines.
- Knowledge Base Integration: Ingest and index documents to provide contextual grounding for LLMs.
- Built-in Connectors & API Access: Easily integrate external tools and services.
- Flexible Deployment: Supports both self-hosted and remote LLM endpoints.

What is Lemonade?

Lemonade is a client-side inference framework for Windows and Linux that simplifies LLM deployment using NPU and GPU acceleration. It supports models like Qwen, Llama, and DeepSeek with different hardware backends. It offers a local runtime with an API compatible with OpenAI, making integration easy.

Dify integrates with Lemonade Server to enable LLM inference, text embedding, and reranking.

Getting Started with Dify

Prerequisites: Docker Desktop and Lemonade Server installed.

Install Dify:
1. git clone https://github.com/langgenius/dify.git
2. cd dify/docker
3. cp .env.example .env
4. docker compose up -d

Launch Dify at http://localhost/plugins. Search for and install Lemonade as a model provider.

Adding Models: Go to Settings > Model Providers > Lemonade > Add a Model. Configure:
- Model Name (e.g., Qwen2.5-7B-Instruct-Hybrid)
- Model Type: LLM
- API endpoint URL: http://host.docker.internal:8000
- Model context size (e.g., 2048)
- Agent Thought and Vision support options

Example Workflow: Ask My Docs

1. Upload or sync documents as a Dify Knowledge source (supports .txt, .md, .pdf, .html, .xlsx, .docx, .csv).
2. Create Chatbot Workflow using Chatflow.
3. Add a Knowledge Retrieval node linked to the dataset.
4. Choose the locally hosted model (e.g., Qwen2.5-7B-Instruct-Hybrid running on NPU for prefill, GPU for generation).
5. Configure System Prompt: guide the model to answer only from provided context, reference specific parts, not fabricate information.
6. Map the Workflow: Input -> Retrieval -> LLM -> Output.

Because the model runs entirely on your local machine, no data leaves your environment. Dify handles visual orchestration while local models handle inference privately.

Putting It All Together:
1. Select your model endpoint via Lemonade Server
2. Create datasets from documents
3. Build flow with visual workflow editor
4. Automate updates via REST API

Everything runs privately on your AMD-powered PC, ensuring full control over performance and data security.
