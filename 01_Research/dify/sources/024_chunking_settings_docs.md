---
source_id: "024"
title: "Configure the Chunk Settings - Dify Docs"
url: "https://docs.dify.ai/en/use-dify/knowledge/create-knowledge/chunking-and-cleaning-text"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify document processing", "Dify knowledge base"]
content_length: 4350
---

## What is Chunking?

Documents imported into knowledge bases are split into smaller segments called **chunks**. Think of chunking like organizing a large book into chapters and paragraphs -- you can't quickly find specific information in one massive block of text, but well-organized sections make retrieval efficient. When users ask questions, the system searches through these chunks for relevant information and provides it to the LLM as context. Without chunking, processing entire documents for every query would be slow and inefficient.

**Key Chunk Parameters**

- **Delimiter**: The character or sequence where text is split. For example, `\n\n` splits at paragraph breaks, `\n` at line breaks. Delimiters are removed during chunking. For example, using `A` as the delimiter splits `CBACD` into `CB` and `CD`. To avoid information loss, use non-content characters that don't naturally appear in your documents.

- **Maximum chunk length**: The maximum size of each chunk in characters. Text exceeding this limit is force-split regardless of delimiter settings.

## Choose a Chunk Mode

The chunk mode cannot be changed once the knowledge base is created. However, chunk settings like the delimiter and maximum chunk length can be adjusted at any time.

### Mode Overview

**General Mode**

In General mode, all chunks share the same settings. Matched chunks are returned directly as retrieval results.

Beyond delimiter and maximum chunk length, you can also configure **Chunk overlap** to specify how many characters overlap between adjacent chunks. This helps preserve semantic connections and prevents important information from being split across chunk boundaries. For example, with a 50-character overlap, the last 50 characters of one chunk will also appear as the first 50 characters of the next chunk.

**Parent-child Mode**

In Parent-child mode, text is split into two tiers: smaller **child chunks** and larger **parent chunks**. When a query matches a child chunk, its entire parent chunk is returned as the retrieval result. This solves a common retrieval dilemma: smaller chunks enable precise query matching but lack context, while larger chunks provide rich context but reduce retrieval accuracy. Parent-child mode balances both -- retrieving with precision and responding with context.

Parent chunks can be created in **Paragraph** or **Full Doc** mode:

- **Paragraph**: The document is split into multiple parent chunks based on the specified delimiter and maximum chunk length. Suitable for lengthy documents with well-structured sections where each section provides meaningful context independently.

- **Full Doc**: The entire document serves as a single parent chunk. Suitable for small, cohesive documents where the full context is essential for understanding any specific detail.

In Full Doc mode:
- Only the first 10,000 tokens are processed. Content beyond this limit will be truncated.
- The parent chunk cannot be edited once created. To modify it, you must upload a new document.

Each parent chunk is further split into child chunks using their own delimiter and maximum chunk length settings.

### Quick Comparison

| Dimension | General Mode | Parent-child Mode |
| --- | --- | --- |
| Chunking Strategy | Single-tier: all chunks use the same settings | Two-tier: separate settings for parent and child chunks |
| Retrieval Workflow | Matched chunks are directly returned | Child chunks are used for matching queries; parent chunks are returned to provide broader context |
| Compatible Index Method | High Quality, Economical | High Quality only |
| Best For | Simple, self-contained content like glossaries or FAQs | Information-dense documents like technical manuals or research papers where context matters |

## Pre-process Text Before Chunking

Before splitting text into chunks, you can clean up irrelevant content to improve retrieval quality.

- **Replace consecutive spaces, newlines, and tabs**: Three or more consecutive newlines become two newlines; multiple spaces become single space; tabs, form feeds, and special Unicode spaces become regular space.
- **Remove all URLs and email addresses**

This setting is ignored in Full Doc mode.

## Enable Summary Auto-Gen

Available for self-hosted deployments only.

Automatically generate summaries for all chunks to enhance their retrievability. Summaries are embedded and indexed for retrieval as well. When a summary matches a query, its corresponding chunk is also returned. You can manually edit auto-generated summaries or regenerate them for specific documents later.

If you select a vision-capable LLM, summaries will be generated based on both the chunk text and any attached images.

## Preview Chunks

Click Preview to see how your content will be chunked. A limited number of chunks will be displayed for a quick review. If the results don't perfectly match your expectations, choose the closest configuration -- you can manually fine-tune chunks later. For multiple documents, click the file name at the top of the preview panel to switch between them.
