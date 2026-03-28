---
source_id: "023"
title: "Building RAG with Dify and Milvus"
url: "https://zilliz.com/learn/building-rag-with-dify-and-milvus"
type: "tutorial"
scraped_at: "2026-03-27"
keywords: ["Dify RAG pipeline", "Dify retrieval strategy", "Dify embedding and reranking"]
content_length: 6820
---

# Building RAG with Dify and Milvus

By Ruben Winastwan, Zilliz Learn. Published Feb 05, 2025.

Learn how to build Retrieval Augmented Generation (RAG) applications using Dify for orchestration and Milvus for vector storage in this step-by-step guide.

## The Fundamentals of RAG

RAG is an approach designed to help mitigate the risk of LLM hallucination. LLMs are trained and fine-tuned on massive datasets with specific cut-off dates. They will most likely work if we ask general questions available on the internet before their cut-off dates. However, if we ask them questions that require internal knowledge, our LLMs would likely fail to give us correct answers.

RAG helps mitigate this issue by providing LLMs with relevant contexts that might help answer users' queries. There are three components in a RAG system: retrieval, augmentation, and generation.

In the retrieval component, the top-k most relevant contexts according to a given user query are fetched. Next, these relevant contexts are reranked based on their similarity score with the user query. In the augmentation component, the most relevant context after the reranking process is integrated into the final prompt together with the original user query as input to the LLM. Finally, in the generation component, the LLM generates the final answer to the user query using the relevant contexts.

## What is Dify?

Dify, which originates from the words "Define" and "Modify," is an open-source platform that enables building various GenAI applications without the hassle of setting up various components. Dify offers a combination of Backend-as-a-Service and LLMOps to orchestrate the workflow of popular GenAI applications, including RAG.

Dify provides a low-code workflow that enables skipping the complexity of setting up different RAG components. Dify offers several advantages:
- Easy integration with popular LLM providers
- A flexible AI agent framework
- An intuitive and easy-to-use UI and APIs
- High-quality RAG engines

## What is Milvus?

Milvus is an open-source vector database perfectly suitable for GenAI applications, including RAG. Milvus offers many advanced features to optimize the implementation of RAG:
- Advanced data indexing methods (FLAT, IVF_FLAT, HNSW, SCANN)
- Easy integration with popular orchestration tools
- Advanced searching methods such as hybrid search
- Product quantization for memory compression
- Metadata filtering for further refining search results

## RAG with Dify and Milvus: Step-by-Step

### Step 1: Starting Dify and Milvus Containers

Self-host Dify with Docker compose. Clone the Dify source code and configure the .env file:
- Set VECTOR_STORE=milvus
- Set MILVUS_URI=http://host.docker.internal:19530
- Run docker compose up -d

### Step 2: Setting Up OpenAI API Key

Go to Settings > Model Provider > OpenAI and configure the API key to enable embedding model and LLM usage.

### Step 3: Inserting Documents into Knowledge Base

Before implementation, documents need to be:
1. Divided into text chunks
2. Each chunk transformed into an embedding via an embedding model
3. Embeddings stored into Milvus as vector database

Dify makes it easy to split texts into chunks and turn them into embeddings. Upload the PDF file, set the chunk length, and choose the embedding model via a slider. Configuration includes:
- Chunk Setting: Set the maximum chunk length (e.g., 100)
- Index Method: Choose "High Quality" for similarity searches
- Embedding Model: Choose from OpenAI models (e.g., text-embedding-3-small)
- Retrieval Setting: Choose "Vector Search" for similarity searches

### Step 4: Creating the RAG App

Go to Studio > Create from Blank > Chatbot. Under "Instruction," write a system prompt (e.g., "Answer the query from the user concisely"). As "Context," add the knowledge base that was just created. Choose the LLM from OpenAI in the upper right corner. Click "Publish" and "Run App."

The RAG-powered chatbot can now deliver contextualized answers based on internal documents stored in the knowledge base.

## Conclusion

By using both Dify and Milvus, implementing a RAG system becomes significantly more accessible, even for those without deep technical expertise. Dify streamlines the orchestration of various RAG components, while Milvus provides efficient vector storage and retrieval capabilities.
