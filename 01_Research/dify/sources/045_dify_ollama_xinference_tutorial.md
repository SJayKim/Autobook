---
source_id: "045"
title: "Install Dify and Integrate Ollama and Xinference"
url: "https://aisharenet.com/en/anzhuang-dify-bingjicheng/"
type: "tutorial"
scraped_at: "2026-03-27"
keywords: ["Dify Ollama integration", "Dify local model deployment", "Xinference", "Dify self-hosted"]
content_length: 4380
---

This tutorial describes installing Dify via Docker and then integrating Ollama and Xinference to quickly build a knowledge base Q&A application.

Introduction to Dify

Dify is an open source Large Language Modeling (LLM) application development platform. Key features:
- Supports hundreds of proprietary and open-source LLM models (GPT, Mistral, Llama3, etc.)
- Intuitive Prompt Orchestration Interface for writing prompts and comparing model performance
- High quality RAG engine covering document ingestion to retrieval
- Agent Framework integration with ReAct and 50+ built-in tools
- Flexible visual workflow canvas
- Comprehensive monitoring and analysis tools
- Backend as a Service with API access

Dify Installation

Clone the Dify GitHub code locally:
```
git clone https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env
docker compose up -d
```

Pull and run Ollama with GPU support:
```
docker pull ollama/ollama
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama --restart always -e OLLAMA_KEEP_ALIVE=-1 ollama/ollama
docker exec -it ollama bash
ollama run qwen2:7b
```

Dify Add Ollama Model

Log in to Dify homepage via EC2 public IP + port 80. Go to User > Settings. Add the Ollama model. Set model name to qwen2:7b, URL to local IP address, port 11434. Configure context size (qwen2-7b-instruct supports 131,072 tokens using YARN technique).

Create a Chat Assistant application with prompt "You are an AI assistant". Test dialog with the model.

Dify Knowledge Base-Based Q&A with Xinference

Add Xorbits Inference model provider. Add Text Embedding model (bge-m3) with server URL http://172.31.30.167:9997. Add Rerank model (bge-reranker-v2-m3) with same server URL.

Import documents into Knowledge Base. Set text retrieval method with Rerank model enabled (bge-reranker-v2-m3). Score threshold set to 0.5 (matches below 0.5 not recalled).

In the chat application, add the knowledge base. The model now answers in conjunction with the knowledge base. Prompt logs show matching knowledge base content placed in <context></context> tags. Recall test allows matching text in knowledge base with weight scores.
