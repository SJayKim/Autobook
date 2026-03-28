---
source_id: "018"
title: "Specify the Index Method and Retrieval Settings - Dify Docs"
url: "https://docs.dify.ai/en/use-dify/knowledge/create-knowledge/setting-indexing-methods"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify retrieval strategy", "Dify embedding and reranking", "Dify RAG pipeline"]
content_length: 7850
---

# Specify the Index Method and Retrieval Settings - Dify Docs

After selecting the chunking mode, the next step is to define the index method for structured content.

## Select the Index Method

Similar to how search engines use efficient indexing algorithms to match search results most relevant to user queries, the selected index method directly impacts the retrieval efficiency of the LLM and the accuracy of its responses to knowledge base content. The knowledge base offers two index methods: High-Quality and Economical, each with different retrieval setting options.

### High Quality

Once a knowledge base is created in the High Quality index method, it cannot switch to Economical later.

The High Quality index method uses an embedding model to convert content chunks into vector representations. This process is called embedding. Think of these vectors as coordinates in a multi-dimensional space -- the closer two points are, the more similar their meanings. This allows the system to find relevant information based on semantic similarity, not just exact keyword matches.

To enable cross-modal retrieval -- retrieving both text and images based on semantic relevance -- select a multimodal embedding model (marked with a Vision icon). Images extracted from documents will then be embedded and indexed for retrieval. Knowledge bases using such embedding models are labeled Multimodal on their cards.

The High-Quality index method supports three retrieval strategies: vector search, full-text search, or hybrid search.

### Q&A Mode

Q&A mode is available for self-hosted deployments only.

When this mode is enabled, the system segments the uploaded text and automatically generates Q&A pairs for each segment after summarizing its content. Compared with the common Q to P strategy (user questions matched with text paragraphs), the Q&A mode uses a Q to Q strategy (questions matched with questions). This approach is particularly effective because the text in FAQ documents is often written in natural language with complete grammatical structures.

The Q to Q strategy makes the matching between questions and answers clearer and better supports scenarios with high-frequency or highly similar questions.

### Economical

Using 10 keywords per chunk for retrieval, no tokens are consumed at the expense of reduced retrieval accuracy. For the retrieved blocks, only the inverted index method is provided to select the most relevant blocks.

## Configure the Retrieval Settings

Once the knowledge base receives a user query, it searches existing documents according to preset retrieval methods and extracts highly relevant content chunks. These chunks provide essential context for the LLM, ultimately affecting the accuracy and credibility of its answers. Common retrieval methods include:

1. Semantic Retrieval based on vector similarity -- where text chunks and queries are converted into vectors and matched via similarity scoring.
2. Keyword Matching using an inverted index (a standard search engine technique).

Both retrieval methods are supported in Dify's knowledge base. The specific retrieval options available depend on the chosen indexing method.

### Vector Search

Definition: Vectorize the user's question to generate a query vector, then compare it with the corresponding text vectors in the knowledge base to find the nearest chunks.

Vector Search Settings:
- Rerank Model: Disabled by default. When enabled, a third-party Rerank model will sort the text chunks returned by Vector Search to optimize results. This helps the LLM access more precise information and improve output quality. Before enabling this option, go to Settings > Model Providers and configure the Rerank model's API key. If the selected embedding model is multimodal, select a multimodal rerank model (marked with a Vision icon) as well. Otherwise, retrieved images will be excluded from reranking and the retrieval results.
- TopK: Determines how many text chunks, deemed most similar to the user's query, are retrieved. It also automatically adjusts the number of chunks based on the chosen model's context window. The default value is 3, and higher numbers will recall more text chunks.
- Score Threshold: Sets the minimum similarity score required for a chunk to be retrieved. Only chunks exceeding this score are retrieved. The default value is 0.5. Higher thresholds demand greater similarity and thus result in fewer chunks being retrieved.

Note: The TopK and Score configurations are only effective during the Rerank phase. Therefore, to apply either of these settings, it is necessary to add and enable a Rerank model.

### Full-Text Search

Definition: Indexing all terms in the document, allowing users to query any terms and return text fragments containing those terms.

Full-Text Search Settings:
- Rerank Model: Same behavior as Vector Search -- disabled by default, sorts chunks when enabled.
- TopK and Score Threshold: Same as Vector Search settings.

### Hybrid Search

Definition: This process combines full-text search and vector search, performing both simultaneously. It includes a reordering step to select the best-matching results from both search outcomes based on the user's query.

In this mode, you can specify "Weight settings" without needing to configure the Rerank model API, or enable Rerank model for retrieval.

Weight Settings: This feature enables users to set custom weights for semantic priority and keyword priority.

- Semantic Value of 1: This activates only the semantic search mode. Utilizing embedding models, even if the exact terms from the query do not appear in the knowledge base, the search can delve deeper by calculating vector distances, thus returning relevant content. Additionally, when dealing with multilingual content, semantic search can capture meaning across different languages, providing more accurate cross-language search results.
- Keyword Value of 1: This activates only the keyword search mode. It performs a full match against the input text in the knowledge base, suitable for scenarios where the user knows the exact information or terminology. This approach consumes fewer computational resources and is ideal for quick searches within a large document knowledge base.
- Custom Keyword and Semantic Weights: In addition to enabling only semantic search or keyword search, flexible custom weight settings are available. You can continuously adjust the weights of the two methods to identify the optimal weight ratio that suits your business scenario.

Rerank Model: Disabled by default. When enabled, a third-party Rerank model will sort the text chunks returned by Hybrid Search to optimize results.

The "Weight Settings" and "Rerank Model" settings both support TopK and Score Threshold options.

### Economical Indexing

In Economical Indexing mode, only the inverted index approach is available. An inverted index is a data structure designed for fast keyword retrieval within documents, commonly used in online search engines. Inverted indexing supports only the TopK setting.
