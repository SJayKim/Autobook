---
source_id: "005"
title: "Platform Architecture and Core Components - DeepWiki Analysis of Dify"
url: "https://deepwiki.com/langgenius/dify-docs/1.1-system-architecture"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify architecture", "Dify platform overview", "Dify application types"]
content_length: 12450
---

# Platform Architecture and Core Components

Source: DeepWiki analysis of langgenius/dify-docs repository (indexed March 16, 2026)

## Purpose and Scope

This document provides a comprehensive overview of the Dify platform's high-level architecture, detailing its four main platform domains, core technical components, and organizational model. It explains how the platform's major systems -- Workflow Engine, Node System, Knowledge Base, Plugin System, and Model Providers -- interconnect to enable AI application development and deployment.

## Four Platform Domains

Dify's architecture is organized into four primary domains, each serving distinct user needs:

### Use Dify Domain (Application Development)
The primary application development environment through the Studio interface:
- **Getting Started**: Platform introduction and quick start guides
- **Nodes**: Library of 40+ workflow building blocks
- **Build**: Orchestration tools, shortcuts, error handling
- **Debug**: Step-by-step execution, variable inspection, logs
- **Publish**: Deployment options (Web App, MCP, API, Embed)
- **Monitor**: Analytics, logs, external observability integrations
- **Knowledge**: RAG pipeline, knowledge base management
- **Workspace**: Model providers, plugins, team management

### Self Host Domain (Infrastructure Management)
Manages infrastructure deployment and configuration:
- **Quick Start**: Container orchestration setup via docker-compose.yaml
- **Configuration**: Environment variables and feature flags via .env file
- **Vector Databases**: Integration with Weaviate, Qdrant, Milvus, etc.
- **Storage**: S3, Azure Blob, local filesystem options

### API Reference Domain (Programmatic Access)
Exposes programmatic interfaces via OpenAPI specifications:
- **Chat and Agent API**: Legacy chat application APIs (openapi_chat.json)
- **Chatflow API**: Multi-turn conversation workflows (openapi_chatflow.json)
- **Workflow API**: Single-turn task execution (openapi_workflow.json)
- **Knowledge API**: Dataset and document management (openapi_knowledge.json)
- **Text Completion API**: Direct LLM completion APIs (openapi_completion.json)

### Develop Plugin Domain (Platform Extension)
Enables platform extensibility through six plugin types:
- **Model Plugin**: Custom LLM provider integration
- **Tool Plugin**: External API and service connections
- **Data Source Plugin**: Custom data import pipelines
- **Trigger Plugin**: Event-based workflow initiation
- **Agent Strategy Plugin**: Custom reasoning logic
- **Endpoint Plugin**: HTTP service exposure

## Core Components Architecture

Five interconnected component systems power AI application development:

### Workflow Engine
- **Variables**: Immutable state management across workflow steps
- **Error Handling**: Configurable retry and failure logic
- **Version Control**: Application state persistence and rollback
- **Orchestration**: Node connection and execution flow management

### Node System
40+ modular building blocks organized into six functional categories:

**Trigger Nodes**: user-input (Web/API Entry Point), schedule-trigger (Cron Jobs), plugin-trigger (External Events), webhook-trigger (HTTP Callbacks)

**Processing Nodes**: llm (Model Inference), code (Python/JS Execution), template (Jinja2 Templating), http-request (External API Calls), doc-extractor (File Parsing), parameter-extractor (Structured Output)

**Logic & Control Nodes**: question-classifier (Intent Routing), ifelse (Conditional Branching), iteration (Loop Processing), loop (Fixed Iterations)

**Data Nodes**: knowledge-retrieval (RAG Integration), variable-aggregator (Merge Branches), variable-assigner (State Management), list-operator (Array Operations)

**Advanced Nodes**: agent (Autonomous Reasoning), tools (Function Calling)

**Output Nodes**: answer (Chatflow Response), output (Workflow Result)

### Knowledge Base System (RAG Pipeline)
- **Data Sources**: File Upload (PDF, DOCX, XLSX - max 50 files, 15MB each), Notion Integration, Web Crawler (Jina Reader, Firecrawl), Cloud Storage (Google Drive, Dropbox)
- **Document Extractors**: Dify, Unstructured
- **Chunking Strategies**: General, Parent-child, Q&A
- **Indexing Methods**: High Quality (Embedding) vs Economy (Keywords)
- **Vector Database**: 14 provider options
- **Retrieval Settings**: KB-level initial retrieval pool, Node-level rerank, TopK, Score Threshold

### Plugin System
Executes in an isolated daemon service (Port 5003) with six plugin types. Features persistent key-value storage, plugin logging/observability, and bundle system for dependency management. Supports reverse invocation (calling Dify APIs from plugins).

### Model Provider System
Manages LLM integrations with:
- **Provider Configuration**: API key management and model selection
- **Load Balancing**: Multi-credential distribution for rate limiting
- **Model Schema**: Input/output interface definitions

## Component Integration and Data Flow

### Service Architecture
- **Web Application**: Next.js Frontend (Port 3000)
- **REST API**: Flask Backend (Port 5001)
- **MCP Server**: AI Assistant Integration
- **Embed SDK**: JavaScript/iframe

### Data Layer
- **PostgreSQL**: Application Data (Port 5432)
- **Redis**: Cache & Task Queue (Port 6379)
- **Vector Database**: Embeddings Storage
- **File Storage**: S3/Azure/Local

### Background Processing
- **Celery Worker**: Async Task Processing
- **Celery Beat**: Task Scheduler
- **Task Queues**: dataset, pipeline, mail, workflow, schedule_*

### Three Primary Data Flow Patterns

1. **Synchronous Request-Response**: Client -> API Service -> Workflow Engine -> (Knowledge Service -> Vector DB) -> (LLM Service) -> Response

2. **Asynchronous Background Processing**: API Service -> Redis (enqueue) -> Celery Worker -> Knowledge Pipeline -> Vector DB -> Task Complete

3. **Plugin Execution**: Workflow Engine -> Plugin Daemon (Port 5003) -> Plugin Code (Isolated) -> External API -> Result

## Deployment Architecture

Container Orchestration via docker-compose.yaml:
- nginx (Ports 80, 443): Reverse proxy and SSL termination
- web (Port 3000): Next.js frontend application
- api (Port 5001): Flask API service
- worker: Celery worker for async tasks
- beat: Celery beat scheduler
- db (Port 5432): PostgreSQL database
- redis (Port 6379): Redis cache and message broker
- weaviate (Port 8080): Default vector database (configurable)
- sandbox (Port 8194): Secure code execution environment
- ssrf_proxy (Port 3128): Squid proxy for HTTP request filtering

This architecture enables horizontal scaling of stateless services (api, worker) while maintaining centralized data stores (db, redis, vector database) and ensures isolated execution environments for potentially unsafe operations (sandbox, ssrf_proxy, plugin_daemon).

## Workspace and Organizational Model

Dify's workspace structure provides multi-tenant organization with role-based access control:
- **Model Providers**: Workspace-level LLM configuration
- **Plugins**: Installed plugin management
- **App Management**: Application organization and versioning
- **Team Members**: User roles (Admin, Editor, Viewer) and permissions
- **Personal Account**: Individual user settings
- **Subscription**: Plan limits and billing
