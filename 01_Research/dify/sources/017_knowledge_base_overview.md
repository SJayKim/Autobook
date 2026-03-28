---
source_id: "017"
title: "Knowledge - Dify Docs"
url: "https://docs.dify.ai/en/use-dify/knowledge/readme"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify RAG pipeline", "Dify retrieval strategy"]
content_length: 3280
---

# Knowledge - Dify Docs

## Introduction

Knowledge in Dify is a collection of your own data that can be integrated into your AI apps. It allows you to provide LLMs with domain-specific information as context, ensuring their responses are more accurate, relevant, and less prone to hallucinations. This is made possible through Retrieval-Augmented Generation (RAG). It means that instead of relying solely on its pre-trained public data, the LLM uses your custom knowledge as an additional source of truth:

1. (Retrieval) When a user asks a question, the system first retrieves the most relevant information from the incorporated knowledge.
2. (Augmented) This retrieved information is then combined with the user's original query and sent to the LLM as augmented context.
3. (Generation) The LLM uses this context to generate a more precise answer.

Knowledge is stored and managed in knowledge bases. You can create multiple knowledge bases, each tailored to different domains, use cases, or data sources, and selectively integrate them into your application as needed.

## Build with Knowledge

With Dify knowledge, you can build AI apps that are grounded in your own data and domain-specific expertise. Here are some common use cases:

- Customer support chatbots: Build smarter support bots that provide accurate answers from your up-to-date product documentation, FAQs, and troubleshooting guides.
- Internal knowledge portals: Build AI-powered search and Q&A systems for employees to quickly access company policies and procedures.
- Content generation tools: Build intelligent writing tools that generate reports, articles, or emails based on specific background materials.
- Research & analysis applications: Build applications that assist in research by retrieving and summarizing information from specific knowledge repositories like academic papers, market reports, or legal documents.

## Create Knowledge

- Quick create: Import data, define processing rules, and let Dify handle the rest. Fast and beginner-friendly.
- Create from a knowledge pipeline: Orchestrate more complex, flexible data processing workflows with custom steps and various plugins.
- Connect to an external knowledge base: Sync directly from external knowledge bases via APIs to leverage existing data without migration.

## Manage & Optimize Knowledge

- Manage content: View, add, modify, or delete documents and chunks to keep your knowledge current, accurate, and retrieval-ready.
- Test and validate retrieval: Simulate user queries to test how well your knowledge base retrieves relevant information.
- Enhance retrieval with metadata: Add metadata to documents to enable filter-based searches and further improve retrieval precision.
- Adjust knowledge base settings: Modify the index method, embedding model, and retrieval strategy at any time.

## Use Knowledge

Integrate into applications: Ground your AI app in your own knowledge.

Related resources:
- Dify v1.1.0: Filtering Knowledge Retrieval with Customized Metadata
- Dify v0.15.0: Introducing Parent-child Retrieval for Enhanced Knowledge
- Introducing Hybrid Search and Rerank to Improve the Retrieval Accuracy of the RAG System
- Text Embedding: Basic Concepts and Implementation Principles
- Enhance Dify RAG with InfraNodus: Expand Your LLM's Context
