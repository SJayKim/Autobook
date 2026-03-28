---
source_id: "044"
title: "How to Run Open Source Model Gemma on Dify"
url: "https://dify.ai/blog/how-to-run-open-source-model-gemma-on-dify"
type: "blog"
scraped_at: "2026-03-27"
keywords: ["Dify supported models", "Dify local model deployment", "Hugging Face integration", "open source models"]
content_length: 5120
---

This post explains how to use open-source models like Google's Gemma on Dify, demonstrating two integration methods via Hugging Face. The principles apply broadly to any open-source model integration with Dify.

How to Use Gemma in Dify

Dify supports Text-Generation models and Embeddings models on Hugging Face. Steps:
1. Have a Hugging Face account
2. Set up Hugging Face's API key
3. Go to the model detail page, copy the model name or Endpoint URL

Two access methods:

Method 1: Hosted Inference API
- Free of charge, but only a few models support this method.
- In Settings > Model Provider > Hugging Face > Model Type, select Hosted Inference API as the Endpoint Type.
- Enter API Token and model name (e.g., google/gemma-6b-it for instruction-tuned version).

Method 2: Inference Endpoint
- Uses cloud resources (AWS) accessed by Hugging Face to deploy the model. Requires payment.
- Click deploy button, select Inference Endpoint, add credit card if needed, create endpoint.
- Takes about 10 minutes to initialize. After deployment, copy Endpoint URL.
- In Settings > Model Provider > Hugging Face, select Inference Endpoints as Endpoint Type.
- For Embeddings, the "Username / Organization Name" needs to match your Hugging Face deployment.

Dify Supports All Open Source Models on the Market

Dify provides support for well-known text generation open-source models: Gemma, LLaMA 2, Mistral, Baichuan, Yi, etc. Supports Hugging Face model types: text-generation, text2text-generation (for Text-Generation), and feature-extraction (for Embeddings).

For local deployment, Dify supports various inference frameworks: Replicate, Xinference, OpenLLM, LocalAI, and Ollama. These services enable users to deploy and run models in a local environment, ensuring data privacy and security while providing better performance and response speed.

Dify also includes a visual operation interface, allowing users to quickly experience and test models without technical background.

Performance Comparison: Gemma 2B and 7B have industry-leading performance compared to LLaMA 2 (7B), LLaMA 2 (13B), and Mistral (7B). In mathematics/science and coding tasks, Gemma 7B even surpasses Mistral 7B.
