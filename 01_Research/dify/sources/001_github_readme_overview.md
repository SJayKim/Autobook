---
source_id: "001"
title: "Dify GitHub Repository README - Production-ready LLM Application Platform"
url: "https://github.com/langgenius/dify"
type: "official"
scraped_at: "2026-03-27"
keywords: ["Dify platform overview", "Dify architecture", "Dify application types"]
content_length: 3842
---

# Dify: Production-Ready LLM Application Platform

## What is Dify?

Dify is an open-source LLM app development platform. It combines AI workflows, retrieval-augmented generation (RAG), agent capabilities, and observability features to enable rapid prototyping and production deployment.

The name Dify comes from "Do It For You."

## Core Features

The platform provides seven main capabilities:

1. **Workflow**: Visual canvas for building and testing AI workflows using a drag-and-drop interface, leveraging all platform features.
2. **Comprehensive Model Support**: Integration with hundreds of proprietary and open-source LLMs from dozens of inference providers and self-hosted solutions, covering GPT, Mistral, Llama3, and any OpenAI API-compatible models.
3. **Prompt IDE**: Interface for crafting prompts, comparing model performance, and adding additional features such as text-to-speech to a text-based app.
4. **RAG Pipeline**: Extensive RAG capabilities that cover everything from document ingestion to retrieval, with out-of-box support for text extraction from PDFs, PPTs, and other common document formats.
5. **Agent Capabilities**: LLM Function Calling or ReAct-based agents with 50+ built-in tools (Google Search, DALL-E, Stable Diffusion, WolframAlpha, etc.).
6. **LLMOps**: Monitor and analyze application logs and performance over time. Continuously improve prompts, datasets, and models based on production data and annotations.
7. **Backend-as-a-Service**: All of Dify's offerings come with corresponding APIs, so you could effortlessly integrate Dify into your own business logic.

## Key Statistics

- 135,000+ GitHub stars
- 21,000+ forks
- 9,691 commits on main branch
- 385 open issues and 416 pull requests
- Active community across Discord, Reddit, and GitHub discussions

## Deployment Options

Users can deploy Dify through:
- **Dify Cloud**: Hosted service with free GPT-4 calls in the sandbox plan
- **Self-hosting**: Docker Compose for quick local deployment
- **Enterprise**: Custom solutions with additional features
- **Cloud platforms**: Kubernetes, Terraform (Azure, Google Cloud, AWS), AWS CDK, Alibaba Cloud

## System Requirements

Minimum specifications:
- CPU: 2+ cores
- RAM: 4+ GB

## Technology Stack & Architecture

The repository contains multiple components:
- `/api`: Backend services (Python, Flask)
- `/web`: Frontend application (Next.js)
- `/sdks`: Software development kits
- `/docker`: Containerization files
- `/docs`: Documentation across 12+ languages

## License

Dify Open Source License, based on Apache 2.0 with additional conditions.

The platform emphasizes accessibility through multi-language support (12+ languages documented) and extensive integration capabilities across major AI service providers.
