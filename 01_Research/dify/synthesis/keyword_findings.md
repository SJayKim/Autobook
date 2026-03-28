# Keyword Findings by Cluster

## 1. Platform Overview & Architecture (cluster: platform_overview)

### Dify platform overview
- Dify is an open-source LLM app development platform combining workflows, RAG, agents, and observability [001, 002]
- Name stands for "Do It For You"; positions as an agentic workflow builder [002]
- 134,700+ GitHub stars, 180,000+ developers, 2.4M community downloads [001, 081]
- Seven main capabilities: Workflow, Model Support, Prompt IDE, RAG Pipeline, Agent Capabilities, LLMOps, Backend-as-a-Service [001]
- Deployment options: Dify Cloud (free sandbox), Docker Compose self-hosting, Kubernetes enterprise, cloud platforms (AWS, Azure, GCP) [001, 054, 055]
- Minimum requirements: 2 CPU cores, 4 GiB RAM [001, 054]
- Licensed under Dify Open Source License based on Apache 2.0 with additional conditions (prohibits competing services) [001, 074]

### Dify architecture
- "Beehive architecture" — hexagonal, modular design where components are independent yet collaborative [004]
- Four platform domains: Use Dify (app development), Self Host (infrastructure), API Reference (programmatic access), Develop Plugin (extensions) [005]
- Five core component systems: Workflow Engine, Node System, Knowledge Base, Plugin System, Model Providers [005]
- Service architecture: Next.js frontend (3000), Flask API (5001), Plugin Daemon (5003), Sandbox (8194), SSRF Proxy (3128) [005]
- Data layer: PostgreSQL (metadata), Redis (cache/queue), Vector DB (embeddings), File Storage (S3/Azure/local) [005]
- Background processing: Celery Worker + Celery Beat with task queues for dataset, pipeline, mail, workflow, schedule [005]
- Three data flow patterns: synchronous request-response, asynchronous background processing, plugin execution [005]
- v0.4.0 restructured with Model Runtime to decouple model management; removed LangChain dependency [004, 074]

### Dify application types
- Two primary types: Workflow (single-turn tasks) and Chatflow (multi-turn conversations) — recommended for new apps [003, 010]
- Three legacy types: Chatbot, Agent, Text Generator — run on same workflow engine with simpler interfaces [003]
- All types share the same underlying workflow engine [003, 010]
- Workflow supports User Input and Trigger start nodes (mutually exclusive) [003]
- Chatflow adds conversation variables, LLM memory, streaming output; cannot use Trigger start [003, 010]
- All apps exportable as YAML DSL files for portability [003, 009]

**Cross-cluster connections**: Architecture connects to all other clusters as the foundation. Plugin System (cluster: plugin_system) decouples components from the core. Knowledge Base (cluster: knowledge_base) and Model Providers (cluster: model_providers) are core component systems.

---

## 2. Workflow & Orchestration (cluster: workflow_orchestration)

### Dify workflow
- Visual drag-and-drop canvas for building AI workflows [009]
- Introduced as a standalone app type and also available inside Chatbot apps as "Chatflow" [009]
- Core workflow nodes: LLM, Tools, Question Classifier, Knowledge Retrieval, Code (Python/Node.js), If/Else, Template, HTTP Request, Variable Assigner [009]
- Designed to be extensible with new node types over time [009]
- DSL support for export/import and cross-workspace portability [009]
- API-ready with built-in observability [009]
- Robust debugging and testing: end-to-end tests, individual node tests, automatic run logging [009]

### Dify chatflow
- Special workflow type triggered at every conversation turn [003, 010]
- Additional features over workflow: conversation variables, LLM node memory, streaming output [003, 010]
- Cannot use Trigger start nodes [003]
- Chatflow-specific system variables: sys.conversation_id, sys.dialogue_count [010]
- Supports multi-turn interactions with context persistence [040, 041]

### Dify workflow nodes
- 40+ modular building blocks in six categories [005]:
  - Trigger: user-input, schedule-trigger, plugin-trigger, webhook-trigger
  - Processing: llm, code, template, http-request, doc-extractor, parameter-extractor
  - Logic/Control: question-classifier, ifelse, iteration, loop
  - Data: knowledge-retrieval, variable-aggregator, variable-assigner, list-operator
  - Advanced: agent, tools
  - Output: answer (chatflow), output (workflow)
- LLM node supports structured outputs (JSON schema), context variables, memory, file processing, Jinja2 templates, streaming [013]
- Code node executes Python/Node.js in sandboxed environment [074]
- Parameter Extractor uses LLM to extract structured data from text [078]

### Dify workflow engine
- Queue-based execution engine aimed at parallel behavior and control [007, 011]
- Parallel execution introduced in v0.8.0: simple, nested, iterative, and conditional parallelism [012]
- Error handling in v0.14.0: default values, workflow redirection, retry logic for LLM/HTTP/Tool/Code nodes [015]
- Real-time debugging in v1.5.0: variable inspect panel, last-run tracking, step-by-step execution without full reruns [014]
- Three pillars: visual clarity, agentic workflow, reliability [011]
- Reliability features: security (least-privilege, sandboxing), observability (logs, traces), auditability (reproducible runs, version tracking), scalability [011]

**Cross-cluster connections**: Workflow nodes integrate directly with Knowledge Base (knowledge-retrieval node), Agent (agent node), Tools (tools node), and Model Providers (llm node). Debugging connects to Monitoring & Observability cluster.

---

## 3. RAG Pipeline & Knowledge Retrieval (cluster: rag_pipeline)

### Dify RAG pipeline
- End-to-end RAG: document ingestion -> chunking -> embedding -> indexing -> retrieval -> reranking -> generation [001, 017, 019]
- Two index methods: High Quality (embedding/vector) and Economical (keyword/inverted index) [018]
- Knowledge Pipeline (v1.0+): visual ETL pipeline with pluggable nodes for extraction, transformation, chunking, and indexing [022, 027]
- Seven built-in pipeline templates for common scenarios [022]
- Data source support: 30+ file formats, cloud storage, online docs, web crawlers [022, 027]
- RAG plugin ecosystem: connectors (Google Drive, Notion, Confluence), ingestion (LlamaParse, Unstructured), storage (Qdrant, Weaviate, Milvus) [022]

### Dify retrieval strategy
- Three retrieval modes for High Quality index: Vector Search, Full-Text Search, Hybrid Search [018]
- Hybrid Search combines vector + keyword search with configurable weight settings (semantic vs keyword priority) [018, 019]
- Multi-path retrieval with consolidation across multiple knowledge bases [029]
- Two rerank settings for multi-path: Weighted Score (internal, no external model) and Rerank Model (external scoring) [029]
- TopK (default 3) and Score Threshold (default 0.5) parameters for tuning retrieval precision [018]
- Practical guidance: start with hybrid retrieval and modest top-k (4-6), add reranker for noisy documents [007]

### Dify embedding and reranking
- Embedding converts text chunks into vector representations for semantic similarity search [018]
- Multimodal embedding models can embed both text and images in unified semantic space [021]
- Rerank models calculate relevance scores between query and retrieved documents, sorting by relevance [019]
- Popular rerank models: Cohere, Jina AI, bge-reranker [019, 045]
- Reranking is positioned at end of search pipeline for merging and sorting results [019]
- Azure AI experiments show hybrid retrieval + rerank significantly improves recall relevance [019]
- TopK and Score Threshold only effective during rerank phase [018]

### Dify agentic RAG
- Embeds retrieval inside an intelligent reasoning loop instead of treating it as fixed preprocessing [020]
- Agent iteratively: analyzes intent, selects tools/sources, constructs queries, executes retrieval, evaluates results, refines or falls back [020]
- Dify enables via Agent Node + drag-and-drop workflow builder + native tool integration + iteration support [020]
- Traditional RAG: one-shot, fixed retriever, no reasoning. Agentic RAG: multi-step, dynamic tool selection, query refinement, feedback loop [020]
- Limitations: increased latency, higher cost, operational complexity [020]
- Use cases: enterprise knowledge assistant, legal/scientific research, developer copilot, customer support [020]

### Dify multimodal retrieval
- Introduced in v1.11.0 with unified semantic space for text and images [021]
- Supports Image-to-Text, Text-to-Image, and Image-to-Image retrieval [021]
- Auto-extracts images from documents (JPG, PNG, GIF up to 2MB) [021]
- Requires multimodal embedding model (marked with VISION badge) [021]
- Multimodal reranking evaluates relevance between query, text, and images [021]
- Supported providers: AWS Bedrock, Google Vertex AI, Jina, Tongyi [021]
- Makes images "searchable, rankable, and actionable evidence" in enterprise RAG [021]

**Cross-cluster connections**: RAG pipeline connects to Knowledge Base Management (document processing, metadata), Agent Capabilities (agentic RAG), and Model Providers (embedding/rerank models). Knowledge Pipeline uses Workflow nodes (If-else, Code, LLM).

---

## 4. Knowledge Base Management (cluster: knowledge_base)

### Dify knowledge base
- Collections of custom data integrated into AI apps to provide domain-specific context [017]
- Three creation methods: Quick create, Knowledge Pipeline, External knowledge base API [017]
- Management features: view/add/modify/delete documents and chunks, test retrieval, adjust settings [017]
- Common use cases: customer support bots, internal portals, content generation, research applications [017]
- Integration: add knowledge bases to apps via Context settings, configure retrieval mode for multi-KB scenarios [029]
- Citation and attribution support when using knowledge retrieval [029]
- Supported file formats: TXT, MD, PDF, HTML, XLSX, DOCX, CSV, EML, MSG, PPTX, XML, EPUB (max 15MB each) [027]

### Dify document processing
- Chunking modes: General (single-tier) and Parent-child (two-tier) [024]
- General mode: configurable delimiter, max chunk length, chunk overlap [024]
- Parent-child mode: child chunks for precise retrieval, parent chunks for contextual response [024, 028]
  - Parent modes: Paragraph (split into multiple parents) or Full Doc (entire document as parent) [024, 028]
  - Full Doc limited to first 10,000 tokens [024]
- Text pre-processing: replace consecutive whitespace, remove URLs/emails [024]
- Summary auto-gen: automatic chunk summaries for enhanced retrievability (self-hosted only) [024]
- Image extraction from PDFs: JPG, JPEG, PNG, GIF under 2MB attached to corresponding chunks [027]
- Q&A mode: auto-generates Q&A pairs from text (Q-to-Q matching strategy, self-hosted only) [018]

### Dify knowledge pipeline
- Visual ETL pipeline introduced September 2025 [022]
- Inherits Dify Workflow canvas experience [022]
- Pipeline nodes: Data Source, Extractor, Processor (optional), Chunker, Indexer, Knowledge Base [027]
- Pluggable architecture: swap parsers, enrichment models, embedding providers, vector stores [022]
- Data source plugins: Google Drive, Notion, Confluence, SharePoint, GitLab, GitHub, web crawlers [022]
- Processor nodes can embed Workflow nodes (If-else, Code, LLM) for content enrichment and rule-based cleaning [022]
- Observable debugging with step-by-step test runs and variable inspect panel [022]
- Seven built-in templates for common scenarios [022]
- Must publish pipeline before uploading files [027]

### Dify metadata filtering
- Introduced in v1.1.0 [025]
- Metadata = "data about data" providing context about documents [025, 026]
- Three value types: String, Number, Time [025, 026]
- Built-in metadata (system-generated): document_name, uploader, upload_date, last_update_date, source [026]
- Custom metadata: user-defined fields assigned to specific documents [026]
- Filter modes in apps: Disabled (default), Automatic (LLM-driven), Manual (user-configured conditions) [029]
- Operators per type: String (is, contains, starts with, etc.), Number (=, !=, >, <, etc.), Date (is, before, after) [029]
- Logic operators: AND (match all) or OR (match any) [029]
- Use cases: access control, version management, contextual relevance filtering [025]
- Bulk editing via Metadata Editor with "Apply to All Documents" option [026]

**Cross-cluster connections**: Knowledge Base is consumed by RAG Pipeline (retrieval strategies, embedding). Knowledge Pipeline uses Plugin System (data source plugins, extractor plugins). Metadata filtering connects to Enterprise Features (access control).

---

## 5. Agent Capabilities (cluster: agent_capabilities)

### Dify agent node
- Decision center in workflows that hands steps to LLM for autonomous decisions [016, 031]
- Embeds Agent Strategy and connects with upstream/downstream workflow nodes [016]
- Three execution stages: initialization, iterative looping, final response [016]
- Output variables: Final Answer, Tool Outputs, Reasoning Trace, Iteration Count, Success Status, Agent Logs [031]
- Configuration: model selection, tool configuration (auth, description, parameters), instructions (Jinja2 supported), execution controls (max iterations, memory/TokenBufferMemory) [031]
- Tool parameter auto-generation: auto (AI-populated) or manual (fixed values) [031]
- Use cases: research/analysis, troubleshooting, multi-step data processing, dynamic API integration [031]

### Dify agent strategy
- Pluggable reasoning algorithms defining how the agent thinks and acts [016, 031]
- Two built-in strategies: Function Calling (native LLM capability) and ReAct (Thought-Action-Observation cycle) [016, 031]
- Extensible: developers can create custom strategies (CoT, ToT, GoT, semantic kernels) via plugin SDK [016]
- Declarative configuration via YAML with parameters (model-selector, tools array, max_iterations) [016]
- Strategy development kit includes configuration component library, structured logging, sandbox testing [016]
- Available for download from Marketplace > Agent Strategies [031]
- Future plans: knowledge base integration, memory support in Chatflow, error handling [016]

### Dify tool integration
- Four tool types: Built-in, Custom (OpenAPI/Swagger), Workflow Tools, MCP Tools [032]
- Built-in tools: Google Search, weather APIs, productivity tools, AI services (50+ available) [001, 032]
- Custom tools: import via OpenAPI specification, configure once, reuse across workflows [032]
- Workflow tools: publish complex workflows as reusable single-node tools [032]
- Tool advantages over HTTP requests: structured interfaces, built-in error handling, type safety, documentation [032]
- Error handling: retry up to 10 times with configurable intervals (max 5000ms), fallback paths [032]

### Dify MCP integration
- Model Context Protocol standardizes how AI agents discover and use external servers [033]
- Two-way native support in v1.6.0 [033]:
  - **MCP Client**: Call any HTTP-based MCP server as a tool (protocol version 2025-03-26) [033, 036]
  - **MCP Server**: Expose Dify apps as MCP endpoints for Claude Desktop, Cursor, Cline, Windsurf [033, 035]
- Three usage modes: (1) MCP server as tool, (2) Agent calling MCP tools intelligently, (3) MCP tools in workflow (agent node or standalone nodes) [033]
- Prior to v1.6.0: community plugin (mcp-server by hjlarry) enabled MCP via Extension plugin [034]
- Setup: Tools > MCP > Add MCP Server (URL, name, server ID) [036]
- MCP tools appear in agents, workflows, and agent nodes like regular tools [036]
- Publishing: provide service description and parameter description; Dify issues server URL [033, 035]
- Security: MCP server URLs contain auth credentials, treat like API keys [035]
- Zapier MCP integration unlocks 8,000+ authorized apps [033]

**Cross-cluster connections**: Agent capabilities are the bridge between Workflow (agent node is a workflow node), Tools (agents use tools), RAG (agentic RAG), and API/Deployment (MCP publishing). Plugin System provides Agent Strategy plugins.

---

## 6. Prompt Engineering & Management (cluster: prompt_engineering)

### Dify prompt orchestration
- Two modes: Basic Mode (encapsulated prompts, lower barrier) and Expert Mode (full control) [038]
- Expert Mode supports SYSTEM/USER/ASSISTANT message roles for Chat models [038]
- Complete model supports flexible block adjustment (Context, Conversation History, Query, Variables) [038]
- Expert mode reveals encapsulated Basic mode prompts for full modification [038]
- Log View feature for debugging from input to output [038]
- Content review feature for sensitive word filtering [038]
- Production prompt best practices: Task description + Examples + Task/context [039]
- Separate rules (system prompt) from data (user prompt) [039]
- Structured outputs (JSON) preferred for workflow-ready applications [039]

### Dify prompt variables
- Variable types: Inputs, Outputs, Environment Variables, Conversation Variables (chatflow only), System Variables [003, 010]
- System variables: sys.user_id, sys.app_id, sys.workflow_id, sys.workflow_run_id, sys.timestamp [003]
- Chatflow adds: sys.conversation_id, sys.dialogue_count [003]
- Variable referencing: dropdown selection or "/" slash command in text inputs [003]
- Environment variables store sensitive info (API keys) separate from app DSL [003]
- Conversation Variables persist across multi-turn chatflow runs within a conversation [003, 040]
- Variable Assigner node writes/updates conversation variables at any point [041]
- Conversation Variables support complex types: String, Number, Object, Array[object] [040, 041]
- Use cases: simulating OpenAI memory, storing user preferences, dialogue summarization, creative writing [040, 041]
- Limitation: too many memories degrade context quality; RAG should be used for large memory sets [040]

**Cross-cluster connections**: Prompt engineering is core to Workflow (LLM node configuration), Agent (instructions), and RAG (context variables connect knowledge retrieval to LLM prompts).

---

## 7. Model Providers & Integration (cluster: model_providers)

### Dify model providers
- System Providers (managed by Dify, billed through subscription) and Custom Providers (own API keys, direct billing) [042]
- Can use both simultaneously: system for prototyping, custom for production [042]
- Supported LLMs: OpenAI (GPT-4, GPT-3.5), Anthropic (Claude), Google (Gemini), Cohere, and many more [042]
- Embedding models: OpenAI, Cohere, Azure OpenAI, local models [042]
- Specialized: DALL-E, Stable Diffusion (image), Whisper, ElevenLabs (speech), Moderation APIs [042]
- Load balancing: round-robin credential rotation with temporary removal on rate limits (paid feature) [042]
- Team access: Owners/Admins configure providers; Editors/Members use them [042]
- Multiple credentials per provider for environment isolation, cost optimization, model testing [042]

### Dify model provider plugin
- Two configuration methods: Predefined Models (provider credentials unlock all models) and Custom Models (per-model configuration) [043]
- Both methods can coexist in a single provider [043]
- Development workflow: init project (CLI) -> YAML config -> provider class -> model-specific code -> debug -> package -> publish [043]
- Provider YAML defines: identifier, labels, description, supported_model_types, configurate_methods, credential schema [043]
- Model YAML defines: model identifier, features (agent-thought, vision, tool-call), model_properties (mode, context_size), parameter_rules, pricing [043]
- Core _invoke method: transform Dify inputs -> provider API call -> transform responses, support streaming/non-streaming [043]
- Remote debugging via plugin management debug key [043]
- Package with `dify plugin package`, publish to dify-official-plugins repository [043]

### Dify local model deployment
- Ollama: pull and run models locally via Docker, configure in Dify via server URL [045]
- Xinference: supports LLM, Text Embedding, and Rerank models with per-model model_uid [043, 045]
- Lemonade Server: client-side inference on AMD Ryzen AI PCs with NPU/GPU acceleration, OpenAI-compatible API [046]
- Other frameworks: Replicate, OpenLLM, LocalAI [044]
- Hugging Face integration: Hosted Inference API (free) or Inference Endpoint (paid, AWS-backed) [044]
- Benefits: complete data privacy, no external API costs, custom fine-tuning [042, 046]
- Supported open-source models: Gemma, LLaMA, Mistral, Baichuan, Yi, Qwen, DeepSeek [044, 045]

**Cross-cluster connections**: Model Providers are used by Workflow (LLM nodes), RAG (embedding, reranking), Agent (model selection for reasoning), and Plugin System (model provider plugins).

---

## 8. API & Deployment (cluster: api_deployment)

### Dify API
- Backend-as-a-Service: use any Dify app as an API service out-of-box [048]
- API types per app: completion-messages (text generation), chat-messages (conversational), workflow execution, knowledge management [048]
- Each app gets its own API credentials with app-specific documentation [048]
- Conversation management via conversation_id for session continuity [048]
- Service API and WebApp conversations are isolated [048]
- Security: never expose API keys in frontend code [048]
- Response modes: streaming (SSE) and blocking [048]
- Full OpenAPI specifications for all app types [005]

### Dify application publishing
- Web App: standalone page with unique URL [049]
- Chat Bubble Widget: floating button overlay with customizable CSS [049]
- Iframe: embedded directly in page content [049]
- JavaScript SDK: advanced embedding with custom styling and behavior [049]
- Configuration via difyChatbotConfig object: token, baseUrl, containerProps, inputs, systemVariables, draggable [049]
- Input passing supports text-input, paragraph, number, and options types (GZIP compressed, base64 encoded) [049]
- Changes to app configuration automatically apply to all embedded instances after republish [049]

### Dify MCP server publishing
- Expose apps as MCP (Model Context Protocol) servers for AI assistants [035, 050]
- Toggle MCP Server on in app configuration to generate unique server URL [035]
- URL contains auth credentials — treat as API key, regenerable [035]
- Integration examples: Claude Desktop (Integrations > Add), Cursor (.cursor/mcp.json) [035]
- Service description and parameter descriptions enable external LLMs to discover and invoke [033]
- Community plugin (pre-v1.6.0): mcp-server Extension plugin with endpoint configuration [034, 051]
- Native support (v1.6.0+): built-in, no plugin needed [033, 052]
- HTTP-based MCP, protocol version 2025-03-26 [033]

**Cross-cluster connections**: API & Deployment consumes Workflow (execution APIs), connects to MCP (agent_capabilities cluster), and is the output layer for all app types.

---

## 9. Self-Hosting & Installation (cluster: self_hosting)

### Dify self-hosting
- Open-source community edition freely deployable [053]
- Recommended when: data residency/governance required, cost at scale favors self-hosting, air-gapped/custom networking needed [053]
- Minimum: 2 CPU cores, 4 GiB RAM [054]
- Components: PostgreSQL, Redis, vector database (Weaviate default), object storage [053]
- Enterprise edition available for advanced features (SSO, multi-workspace, audit logging) [056]

### Dify Docker deployment
- Primary self-hosting method via Docker Compose [054]
- Steps: clone repo (latest release tag), cd docker, cp .env.example .env, docker compose up -d [054]
- 11 containers: api, worker, worker_beat, web, plugin_daemon, db_postgres, redis, weaviate, nginx, sandbox, ssrf_proxy [054]
- Access via http://localhost/install for initial admin setup [054]
- Upgrade: check .env.example changes, docker compose down, pull new images, up -d [054]
- Supports macOS 10.14+, Linux (Docker 19.03+), Windows with WSL 2 [054]

### Dify Kubernetes deployment
- Official Helm chart: helm repo add dify https://langgenius.github.io/dify-helm [056]
- Requirements: Kubernetes 1.24+, Helm 3.14+ [056]
- KubeBlocks integration for production: managed PostgreSQL, Redis, Qdrant clusters with one-click scaling [055]
- KubeBlocks operations: vertical scaling, horizontal scaling, volume expansion, restart [055]
- Community Helm chart: douban/charts for non-enterprise deployments [055]
- Enterprise Helm chart supports restricted environments (OpenShift) [056]
- Expected pods: dify-worker, dify-sandbox, dify-frontend, dify-api [055]

### Dify environment configuration
- Comprehensive .env file with 100+ variables [057]
- Key categories: Common URLs, Server Config, Database (PostgreSQL), Redis, Celery, CORS, File Storage, Vector Database, Knowledge, Multi-modal, Scheduled Tasks [057]
- Vector database options: 30+ providers (weaviate, qdrant, milvus, pgvector, elasticsearch, tidb, couchbase, etc.) [057]
- File storage: local, S3, Azure Blob, Aliyun OSS, Huawei OBS, Volcengine TOS, Tencent COS [057]
- Critical settings: SECRET_KEY (must set before first launch), MIGRATION_ENABLED, LOG_LEVEL, VECTOR_STORE [057]
- Worker configuration: SERVER_WORKER_AMOUNT (cpu cores x 2 + 1), gevent worker class [057]
- Scheduled tasks: cache cleaning, unused dataset cleanup, message cleanup, workflow log retention [057]

**Cross-cluster connections**: Self-hosting is foundational infrastructure for all other clusters. Environment configuration directly affects Model Providers, Vector DB choice (RAG), and Enterprise Features (security settings).

---

## 10. Monitoring & Observability (cluster: monitoring_observability)

### Dify observability
- Built-in monitoring: application logs, performance analytics, cost tracking [001]
- LLMOps features: select models, create prompts, monitor performance, continuous improvement, cost optimization [058]
- External integration via one-click configuration in app monitoring tab [058]
- Supported tools: LangSmith, Langfuse, Opik — all support custom endpoints for self-hosted instances [074]
- Arize Phoenix and Arize AX for advanced evaluation and production monitoring [059]

### Dify LangSmith integration
- Developed by LangChain team; provides tracing and evaluation capabilities [058]
- Features: pairwise testing, regression testing, LLM-as-judge, custom evaluators [058]
- One-click configuration on app overview page [058]
- Tracks accuracy, latency, resource utilization [058]

### Dify Langfuse integration
- Open-source, self-hostable (MIT license) [058, 062]
- Native integration auto-maps: user->userId, message_id->trace_id, conversation_id->sessionId [062]
- Features: framework-agnostic tracing, automated evaluation, custom pipelines, human annotation, datasets [058]
- Langfuse Prompt Management Plugin (community): fetch, search, update prompts from Langfuse [062]
- Low performance overhead; supports complex use cases [058]

### Dify Arize Phoenix integration
- Open-source observability layer for LLM apps [059]
- Auto-traces model calls, tool invocations, chain steps [059]
- Beyond tracing: annotate traces, build test datasets, create evaluations, run tests [059]
- Use case flow: configure -> collect traces -> build dataset -> iterate/experiment -> define evaluators -> deploy [059]
- Arize AX extends with live evaluations, dashboards, monitors, alerts for production [059]

### Dify annotation and feedback
- Annotation system: curated Q&A library for consistent responses [060]
- When enabled: user question -> search annotations -> if match above threshold, return curated response; else proceed with AI [060]
- Creates "fast path" for known good answers while maintaining AI flexibility [060]
- Creation methods: from conversations, bulk import, manual entry [060]
- Hit tracking: monitor which annotations are matched, frequency, similarity scores [060]
- Independent RAG mechanism separate from knowledge base [061]
- Cost savings: avoids redundant LLM calls for duplicate questions [061]
- Data asset: accumulated Q&A pairs can be exported for future model fine-tuning [061]
- Comparison with GPTCache: Dify persists custom annotated responses vs auto-cached LLM outputs [061]

**Cross-cluster connections**: Observability monitors Workflow execution, Agent reasoning traces, RAG retrieval quality, and Model Provider usage. Annotation system connects to API (annotation reply for deployed apps).

---

## 11. Plugin & Extension System (cluster: plugin_system)

### Dify plugin system
- Introduced in v1.0.0; decouples horizontally scalable modules from core [006, 063]
- Six plugin types: Model, Tool, Agent Strategy, Data Source, Trigger, Extension (Endpoint) [005, 064]
- Plugin daemon runs as isolated service on Port 5003 [005]
- Security: cryptographic signatures, permission declarations, privacy policy enforcement [006, 064]
- Four runtime types: Local subprocess, SaaS (AWS Lambda), Enterprise, Remote debugging [006]
- Reverse invocation: plugins can call internal Dify services (LLMs, apps, knowledge bases, tools) [006]
- Debugging: remote debugging via TCP long connections; traffic forwarding via Redis HashMap [006]
- Persistent key-value storage at plugin and workspace levels [064]

### Dify marketplace
- Launched with v1.0.0; platform for aggregating, distributing, managing plugins [063]
- 120+ plugins including models (OpenAI, Gemini, DeepSeek, Ollama), tools (Perplexity, Discord, Slack, Firecrawl, Jina AI) [063]
- Three distribution channels: Marketplace, community sharing (GitHub), local deployment [063]
- Initial partners: OpenRouter, Brave, E2B, SiliconFlow, Agora, Fish Audio, Dupdub [063]
- All marketplace plugins undergo code review and privacy policy review [006, 064]
- Available at marketplace.dify.ai [064]

### Dify plugin development
- Prerequisites: dify-plugin-daemon CLI, Python >= 3.12 [065]
- Initialize with `dify plugin init`, select plugin type and template [065]
- Tool plugin structure: provider YAML (identity, credentials), tool YAML (parameters), Python code (Tool class) [065]
- Key attributes: name, type, label, form (llm or form), required, human_description, llm_description [065]
- Remote debugging: get debug key from Plugin Management, configure .env, run `python -m main` [065]
- Package: `dify plugin package ./name` creates .difypkg file [065]
- Publish: submit PR to dify-official-plugins repository [065]
- Documentation: https://docs.dify.ai/plugins/introduction [064]

### Dify endpoint plugin
- Extension-type plugin providing custom HTTP request handling [066]
- Dify generates random URL; forwards HTTP requests to plugin code (serverless function pattern) [066]
- Reverse call feature: plugins can invoke Dify apps, models, and other internal services [066]
- Use cases: custom WebApp templates, OpenAI-compatible API endpoints, asynchronous event triggers [066]
- SaaS runtime: serverless architecture using AWS Lambda for elastic scaling [066]
- Example: custom chatbot UI skins as plugin templates [066]
- Example: OpenAI-compatible interface wrapping Dify models [066]

**Cross-cluster connections**: Plugin system enables Model Providers (model plugins), Tools (tool plugins), Agent Strategies (strategy plugins), Knowledge Pipeline (data source plugins), and Monitoring (endpoint plugins for integrations).

---

## 12. Enterprise Features & Security (cluster: enterprise_security)

### Dify enterprise
- Enterprise edition for building agentic AI at scale [068]
- Key challenges solved: no-code AI building, unified knowledge management, autonomous agents for teams, enterprise-grade security [068]
- Infrastructure: high availability, flexible deployment (on-premise, public cloud, VPC), scalable, seamless integration [068]
- Available on AWS Marketplace and Microsoft Azure Marketplace [070]
- Customer testimonials from Volvo Cars, ETS, Ricoh [068]
- 1M+ applications running, deployed in 120+ countries [068, 080]
- Trusted by Fortune 500 companies [081]

### Dify SSO and access control
- Multi-tenant management with multiple workspaces [005, 056]
- RBAC: Admin, Editor, Viewer roles [005]
- SSO: SAML, OIDC, OAuth2 integration [056, 070]
- Two-step verification and MFA support [056]
- Centralized access control [070]
- Comprehensive audit logging [070]
- Enterprise edition extends with multi-workspace setups and advanced authentication [011]

### Dify compliance and data residency
- SOC 2 Type I and Type II certified [069]
- ISO 27001:2022 certified [069]
- GDPR certified [069]
- Comprehensive security controls: encryption at rest, encrypted data transmission, firewall management, intrusion detection, network segmentation, penetration testing [069]
- Customer data deleted upon leaving service [069]
- Trust Center at security.dify.ai with detailed control statuses [069]
- Self-hosting enables full data sovereignty [053]
- On-premise deployment for maximum compliance [070]

**Cross-cluster connections**: Enterprise features extend Self-Hosting (Kubernetes deployment), connect to API (authentication), and influence Knowledge Base (metadata filtering for access control).

---

## 13. Comparison with Alternatives (cluster: comparison_alternatives)

### Dify vs LangChain
- Core difference: Dify is a platform (visual, low-code); LangChain is a Python library (code-first) [071]
- Dify removed LangChain from its codebase citing it slowed platform development [074]
- Dify: faster development, visual workflow, battle-tested features, dedicated team maintenance [071]
- LangChain: more flexibility for deep customization, extensive Python ecosystem, but less accountable third-party contributions [071]
- Dify analogy: scaffolding system with refined engineering. LangChain: toolbox with hammers and nails [071]

### Dify vs Flowise
- Dify: full-stack LLM platform with prompt IDE, knowledge base, agent orchestration, app hosting [072]
- Flowise: lightweight open-source LangChain builder for chatbot/agent flows [072, 074]
- Dify stronger in: debugging, logic control (iterations, loops), workflow-as-tools, LLMOps, stability [074]
- Flowise stronger in: simpler setup, lighter weight, MIT/Apache license, multi-channel deployment [072, 074]
- Flowise lacks: iteration/loop support, advanced debugging, comprehensive logic controls [074]

### Dify vs n8n
- n8n: workflow automation tool (400+ app integrations) with AI as one component [073]
- Dify: LLM application platform with AI as the entire product [073]
- n8n wins for: business process automation spanning multiple tools (CRM, email, databases) [073]
- Dify wins for: building AI-first applications, chatbots, knowledge assistants with publishing [073]
- Both: open-source, self-hostable, can be used together (n8n triggers Dify via HTTP) [073]

### Dify vs Langflow
- Both visual low-code platforms, but different approaches [074, 075]
- Dify: concise component set (15+), removed LangChain, powerful variable system [074]
- Langflow: extensive LangChain components, allows source code modification, MIT license [074]
- Dify excels: debugging (complete log history), nested workflows, intuitive UI [074]
- Langflow excels: component code customization, flexible RAG debugging, Datastax financial backing [074]
- Dify more restrictive license (prohibits competing services) vs Langflow MIT [074]

**Cross-cluster connections**: Comparisons reference Workflow (ease of building), RAG (quality comparison), Observability (integration comparison), and Enterprise (licensing, compliance).

---

## 14. Use Cases & Tutorials (cluster: use_cases_tutorials)

### Dify use cases
- Internal chatbots: 65% reduction in search time, 57% decrease in IT inquiries [079]
- Customer support: RAG-based bots with knowledge base grounding [017, 079]
- Deep research: iterative multi-step investigation with loop variables and agent nodes [077]
- Travel planning: parameter extraction + external API + LLM reasoning [078]
- Sales/bid team knowledge bases: 80%+ answer accuracy [079]
- NVIDIA GTC 2025 showcase: AI agents across industries [080]
- Enterprise examples: Volvo Cars, ETS, Ricoh [068]
- Content generation, document processing, research & analysis [017]

### Dify chatbot tutorial
- Simple chatbot: LLM node + Code node + Answer node in Chatflow [076]
- Internal chatbot guide: Knowledge base creation -> Chatbot app -> Prompt configuration -> KB connection -> Testing -> Deployment [079]
- Key settings: Top K (3-8), Score Threshold (0.5-0.75), chunking strategy [079]
- Testing recommendations: 30 prepared questions, informal queries, 5-7 users from different departments over 2-3 days [079]
- Troubleshooting: hallucination (increase threshold), missing info (lower threshold, increase chunk size), slow response (smaller model, reduce Top-K) [079]

### Dify workflow tutorial
- Deep Research workflow: intent identification -> iterative exploration (loop node with six variables) -> synthesis [077]
- Travel planner: parameter extraction -> IF/ELSE routing -> API calls -> LLM planning [078]
- Science Writing Assistant: nested parallel branches with question classification [012]
- Investment Research: parallel knowledge retrieval + web scraping -> template merge -> LLM processing [014]
- Structured output patterns: JSON schema for reliable downstream processing [076, 077]

### Dify RAG application tutorial
- Dify + Milvus: self-host Dify, configure Milvus vector store, create knowledge base, build RAG chatbot [023]
- Dify + Ollama + Xinference: local models with embedding (bge-m3) and rerank (bge-reranker-v2-m3) [045]
- Dify + Lemonade: fully private RAG on AMD Ryzen AI PCs [046]
- Steps: upload documents -> configure chunking -> select embedding model -> set retrieval method -> create chatbot -> connect knowledge base [023, 045]

**Cross-cluster connections**: Tutorials demonstrate practical integration of Workflow, RAG, Agent, and Tool capabilities. They serve as concrete examples of concepts from all other clusters.

---

## 15. Community & Ecosystem (cluster: community_ecosystem)

### Dify open-source community
- Open-sourced May 15, 2023; reached 100K stars June 2025 [081]
- Top 100 open-source projects globally [081]
- 134,700+ stars, 21,000+ forks as of March 2026 [001]
- 2.4 million Community Version downloads [081]
- Active across Discord, Reddit, GitHub discussions, forum.dify.ai [001, 002]
- Notable contributors: @fdb02983rhy (LLM integration), @kurokobo (deployment/security), @junjiem (MCP plugins), @hjlarry (MCP strategy), @Woo0ood (Loop node) [081]
- Community events: IF Con Tokyo 2025, European Roadtrip (5 countries), AWS Partner Award 2025 [081]
- Company behind Dify: LangGenius Inc. (CEO: Luyu Zhang) [070]
- Founding team background at Tencent DevOps [074]

### Dify pricing plans
- **Sandbox (Free)**: 200 credits, 1 member, 5 apps, 50 docs, 50MB storage, 30-day logs [083]
- **Professional ($59/mo)**: 5,000 credits, 3 members, 50 apps, 500 docs, 5GB, priority processing [083]
- **Team ($159/mo)**: 10,000 credits, 50 members, 200 apps, 1,000 docs, 20GB, top priority [083]
- **Enterprise (Custom)**: Contact sales, typically unlimited [083]
- Annual billing saves 17% [083]
- All plans: LLM API load balancing, all app types, marketplace access, batch document upload, webapp/API publishing [083]
- Self-hosted: community edition (free) or Enterprise edition (licensed) [083]
- Free for students and educators [083]
- Cost comparison: small teams favor cloud; large organizations favor self-hosting [053]
- Message credits = API calls to language models [053]

**Cross-cluster connections**: Community drives Plugin Marketplace growth, contributes to all clusters. Pricing affects deployment decisions (Self-Hosting vs Cloud).
