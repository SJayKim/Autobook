---
source_id: "021"
title: "Multimodal retrieval is now available in the knowledge-Base"
url: "https://dify.ai/blog/multimodal-retrieval-is-now-available-in-the-knowledge-base"
type: "blog"
scraped_at: "2026-03-27"
keywords: ["Dify multimodal retrieval", "Dify embedding and reranking", "Dify RAG pipeline"]
content_length: 5980
---

# Multimodal retrieval is now available in the knowledge-Base

By Zhenan Sun, Digital Marketing. Written on Jan 7, 2026.

Dify's Multimodal Knowledge Base unifies text and images into a single semantic space, enabling accurate multimodal RAG and vision-enabled reasoning.

Enterprise knowledge has never been limited to text. Product manuals contain real-world photos, technical reports include architecture diagrams, and training guides are filled with UI screenshots. The information density and importance of these visual assets often equal or exceed that of the text itself.

Now, the Dify Knowledge Base officially supports multimodal capabilities. Text and images can be understood, retrieved, and utilized together within Workflow applications. The context retrieved by AI Agents is no longer restricted to text; they can now "see" images, interpret the information within them, and provide answers accordingly.

## Core Breakthrough: A Unified Semantic Space

Starting from Dify v1.11.0, multimodal embeddings were introduced within a unified semantic space. By placing images and text into a shared coordinate system, "Image-to-Text," "Text-to-Image," and "Image-to-Image" retrieval have been enabled, significantly improving search accuracy.

- Multimodal Support: The system automatically extracts images referenced via Markdown links (supporting JPG, PNG, and GIF, up to 2MB). When a multimodal embedding model is selected, these images are vectorized and stored alongside text for retrieval.
- Broad Model Ecosystem: Dify supports multimodal embedding and rerank models from various cloud providers and open-source ecosystems, including AWS Bedrock, Google Vertex AI, Jina, and Tongyi. Models with multimodal capabilities are marked with a VISION badge in the settings panel.

## From "Semantic Matching" to "Visual Understanding"

- Intuitive Intent Capture: Users can describe their needs through natural language or by uploading relevant images. The system retrieves both semantically related text and images to help users locate key information quickly.
- Complete RAG Reasoning: When using a Vision-enabled LLM, the AI is no longer limited to text citations. It can incorporate relevant images into the reasoning process and explain details found within them, resulting in more accurate and helpful answers.

## Technical Value: Why RAG Requires Embedding and Rerank Synergy

In a broad RAG architecture, information moves through a pipeline of "Chunking - Indexing - Retrieval - Reranking - Generation." This process transforms scattered documents into a precise information flow. Within this framework, Embedding and Reranking are both essential:

- Multimodal Embedding maps content into a vector space to perform the first round of fast similarity matching. It determines whether your query can accurately locate relevant content within a massive knowledge base.
- Multimodal Reranking evaluates the specific relevance between the query, text, and images. It ensures that the most critical visual and textual evidence is prioritized, providing the LLM with the most accurate context.

The true value of these capabilities lies in making images searchable, rankable, and actionable evidence. In enterprise RAG and Agentic Workflows, this expands the boundaries of document processing. Product specs, diagrams, and screenshots are no longer just "decorations" -- they are now computable knowledge.

## Example Scenario: A "Look at the Image and Answer" Assistant

Step 1: Create a Multimodal Knowledge Base
1. Importing Documents: Create a new knowledge base and upload your "Product Manual."
2. Configuration: Select an Embedding and Rerank model with the VISION badge. Images in the preview area are processed immediately.
3. Managing Image Chunks: Images can be managed at the chunk level. If a multimodal embedding model is used, images are vectorized and directly involved in retrieval; if a text-only model is used, images are returned only as attachments when their corresponding chunks are retrieved.
4. Testing Retrieval: Uploading a photo of a pair of headphones successfully retrieved the corresponding manual chapters, including structural diagrams and accessory lists.

Step 2: Building a Workflow for Automated Queries
1. Input & Branching: The workflow receives the user's question and image. An "IF/ELSE" node determines if the query can be answered by the knowledge base or if it should be routed elsewhere.
2. Knowledge Retrieval: The system searches the knowledge base to find the most relevant text and image chunks.
3. LLM Node with Vision: Enable Vision mode and select the uploaded image variable. The LLM can then extract key information from the image, combining it with task requirements to analyze and locate the problem.
4. Aggregation & Output: Use a variable aggregation node to merge the retrieval results and the LLM analysis, then output a clear and actionable answer.

## Conclusion: From Text Search to Intelligent Execution

The launch of the Multimodal Knowledge Base marks Dify's evolution from a text-based retrieval tool to a comprehensive enterprise knowledge and automation platform. It is about turning visual information into Workflow context that can support reasoning and actions.
