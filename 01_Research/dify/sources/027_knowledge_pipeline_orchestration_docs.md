---
source_id: "027"
title: "Step 2: Orchestrate Knowledge Pipeline - Dify Docs"
url: "https://docs.dify.ai/en/use-dify/knowledge/knowledge-pipeline/knowledge-pipeline-orchestration"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify knowledge pipeline", "Dify document processing", "Dify knowledge base"]
content_length: 8450
---

## Knowledge Pipeline Orchestration

Imagine setting up a factory production line where each station (node) performs a specific task, and you connect them to assemble widgets into a final product. This is knowledge pipeline orchestration -- a visual workflow builder that allows you to configure data processing sequences through a drag-and-drop interface. It provides control over document ingestion, processing, chunking, indexing, and retrieval strategies.

### Interface Status

When entering the knowledge pipeline orchestration canvas, you'll see:
- **Tab Status**: Documents, Retrieval Test, and Settings tabs will be grayed out and unavailable at the moment.
- **Essential Steps**: You must complete knowledge pipeline orchestration and publishing before uploading files.

Your starting point depends on the template choice. If you chose Blank Knowledge Pipeline, you'll see a canvas that contains Knowledge Base node only.

### Pipeline Nodes

**Data Source Nodes**: Select data sources for the pipeline. Dify supports 4 types of data sources: File Upload (pdf, docx, etc.), Online Drive (Google Drive, OneDrive, etc.), Online Doc (Notion), and Web Crawler (Jina Reader, Firecrawl). Additional data sources can be installed from the Dify Marketplace.

**Extractor Nodes**: Extract text content from documents. Documents come in different formats -- PDF, XLSX, DOCX. Extractors handle the conversion so content is ready for the next step. You can choose Dify's Doc Extractor to process files, or select tools based on your needs from Marketplace which offers Dify Extractor and third-party tools such as Unstructured.

**Processor Nodes (optional)**: Transform or clean extracted text before chunking. Processors can perform operations such as text cleaning, content filtering, format normalization, and language translation. These nodes sit between extraction and chunking, allowing you to apply custom transformations to your content.

**Chunker Nodes**: Split processed text into chunks suitable for indexing. Configure chunking strategy (General or Parent-child), delimiters, maximum chunk length, and overlap settings. The chunker determines how your documents are segmented for retrieval.

**Indexer Nodes**: Configure how chunks are embedded and indexed. Settings include:
- Embedding model selection (choose from available models, multimodal models marked with VISION badge)
- Index method: High Quality (vector embedding) or Economical (keyword-based)
- Retrieval settings: Vector Search, Full Text Search, or Hybrid Search

**Knowledge Base Node**: The final destination node representing the knowledge base itself. This node defines the output target and retrieval configuration. All pipeline paths must ultimately connect to this node.

### Building a Pipeline

1. Start with a Data Source node -- select the type of data you want to ingest.
2. Connect an Extractor node to process the raw documents.
3. Optionally add Processor nodes for text cleaning or transformation.
4. Add a Chunker node to define how text is split.
5. Connect an Indexer node to configure embedding and search settings.
6. Connect everything to the Knowledge Base node.

Each node has configuration panels where you set parameters. Nodes are connected by dragging edges between them on the canvas.

### Pipeline Variables and User Input

Pipelines support user input fields that can be referenced in node configurations. When users upload files, they can fill in these parameters. This allows dynamic configuration based on the specific documents being processed.

Chunk structure remains consistent with the pipeline configuration and won't change with user input parameters.

### Publishing the Pipeline

After configuring all nodes:
1. Click Publish to finalize the pipeline configuration.
2. Once published, the Documents tab becomes available for uploading files.
3. The pipeline processes files according to the configured node sequence.

### Supported File Formats

Dify supports various document formats including TXT, MARKDOWN, PDF, HTML, XLSX, XLS, DOCX, CSV, EML, MSG, PPTX, PPT, XML, EPUB, with each file not exceeding 15 MB.

### Image Extraction

For PDF documents, Dify enables targeted extraction of images and tables. JPG, JPEG, PNG, and GIF images under 2 MB are automatically extracted as attachments to their corresponding chunks. If you select a multimodal embedding model (marked with a VISION icon), the extracted images will also be embedded and indexed for retrieval.
