---
source_id: "022"
title: "Introducing Knowledge Pipeline"
url: "https://dify.ai/blog/introducing-knowledge-pipeline"
type: "blog"
scraped_at: "2026-03-27"
keywords: ["Dify RAG pipeline", "Dify retrieval strategy", "Dify embedding and reranking"]
content_length: 7450
---

# Introducing Knowledge Pipeline

By Leilei, Product Marketing. Written on Sep 23, 2025.

An adaptable, scalable and observable RAG data processing pipeline that converts enterprise unstructured data into high-quality context usable by LLM.

Today we are introducing the new Knowledge Pipeline, a visual pipeline that turns messy enterprise data into high quality context for LLMs.

In most enterprises, the bottleneck is not the model. It is context engineering on unstructured data. Critical information sits in PDFs, PPT, Excel, images, HTML, and more. The challenge is to convert scattered, heterogeneous, and constantly changing internal data into reliable context that LLMs can consume.

Traditional RAG often struggles on enterprise data due to three issues:

1. Fragmented sources: Data lives across ERP, wikis, email, and drives, each with its own auth and format, making point by point integration costly.
2. Parsing loss: After parsing, documents become unstructured text with charts and formulas dropped, and when naive chunking further breaks document logic, LLMs end up answering from incomplete fragments.
3. Black box processing: Little visibility into each step makes it hard to tell whether failures come from parsing, chunking, or embedding, and reproducing errors is painful.

Knowledge Pipeline provides the missing data infrastructure for context engineering.

## Visual and Orchestrated Knowledge Pipeline

Knowledge Pipeline inherits Dify Workflow's canvas experience and makes the RAG ETL path visible. Each step is a node. From source connection and document parsing to chunking strategies, you choose the right plugin for text, images, tables, and scans. Backed by the Dify Marketplace, teams assemble document processing lines like building blocks and tailor flows by industry and data type.

When needed, you can embed Workflow nodes such as If-else, Code, and LLM into the pipeline. Use a model for content enrichment and code for rule based cleaning to achieve true flexibility.

### Enterprise Grade Data Source Integrations

Knowledge Pipeline brings Data Source as a new plugin type, letting each knowledge base connect to multiple unstructured sources without custom adapters or auth code.

Covered sources include:
- Local files: 30+ formats such as PDF, Word, Excel, PPT, Markdown
- Cloud storage: Google Drive, AWS S3, Azure Blob, Box, OneDrive, Dropbox
- Online docs: Notion, Confluence, SharePoint, GitLab, GitHub
- Web crawling: Firecrawl, Jina, Bright Data, Tavily

### Pluggable Data Processing Pipeline

Processing is broken into standard nodes to make the pipeline predictable and extensible.

- Extract: Ingestion from many sources. The next steps adapt to the upstream output type, whether file objects or page content, including text and images.

- Transform: The core of the pipeline, composed of four stages:
  1. Parse: Choose the optimal parser per file type, extract text and structured metadata. For scans, tables, or PPT text box ordering, run multiple parsers in parallel to avoid loss.
  2. Enrich: Use LLM and Code nodes for entity extraction, summarization, classification, redaction, and more.
  3. Chunk: Three strategies are available: General, Parent-Child, and Q&A, covering common documents, long technical files, and structured table queries.
  4. Embed: Choose embeddings by cost, language, and dimension from different providers.

- Load: Write vectors and metadata into the knowledge base and build efficient indexes. Support high quality vector indexes and cost efficient inverted indexes. Configure metadata tags for precise filtering and access control.

After processing, retrieval supports vector, full text, or hybrid strategies. Use metadata filters and reranking to return precise results with original citations.

### Observable Debugging

Legacy pipelines behave like a black box. With Knowledge Pipeline you can Test Run the entire flow step by step and inspect inputs and outputs at each node. The Variable Inspect panel shows intermediate variables and context in real time, so you can quickly locate parsing errors, chunking issues, or missing metadata.

### Templates for Common Scenarios

Seven built-in templates help you start fast:
- General document processing (General Mode, ECO)
- Long document processing (Parent-Child, HQ)
- Table data extraction (Simple Q&A)
- Complex PDF parsing (Complex PDF with Images & Tables)
- Multimodal enrichment (Contextual Enrichment Using LLM)
- Document format conversion (Convert to Markdown)
- Intelligent Q&A generation (LLM Generated Q&A)

## RAG Plugin Ecosystem

Dify provides an open plugin ecosystem built by the team, partners, and community:
- Connector: Google Drive, Notion, Confluence, and many more
- Ingestion: LlamaParse, Unstructured, OCR tools
- Storage: Qdrant, Weaviate, Milvus, Oracle and other leading vector databases

## Why Knowledge Pipeline

Knowledge Pipeline operationalizes context engineering. It converts unstructured enterprise data into high quality context that powers retrieval, reasoning, and applications.

Three core benefits:
1. Bridge business and data engineering: Visual orchestration and real time debugging let business teams participate directly.
2. Lower build and maintenance cost: Processing becomes reusable assets. Templates that teams can copy and adapt, reducing rebuilds.
3. Adopt best-of-breed vendors: Swap OCR, parsing, structured extraction, vector stores, and rerankers at any time while keeping the overall architecture stable.
