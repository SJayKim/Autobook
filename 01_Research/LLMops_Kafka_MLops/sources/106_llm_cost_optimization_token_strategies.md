---
source_id: 106
title: "Reduce LLM Costs: Token Optimization Strategies"
url: "https://www.glukhov.org/post/2025/11/cost-effective-llm-applications"
type: web
scraped_at: 2026-03-27
keywords: ["kw_039"]
content_length: 9800
---

# Reduce LLM Costs: Token Optimization Strategies

Token optimization is the critical skill separating cost-effective LLM applications from budget-draining experiments. With API costs scaling linearly with token usage, understanding and implementing optimization strategies can reduce expenses by 60-80% while maintaining quality.

## Understanding Token Economics

Tokens are the fundamental units LLMs process - roughly equivalent to 4 characters or 0.75 words in English.

### Pricing Models Comparison (2025)

OpenAI: GPT-4 Turbo $0.01/$0.03 per 1K tokens, GPT-3.5 Turbo $0.0005/$0.0015, GPT-4o $0.005/$0.015.
Anthropic: Claude 3 Opus $0.015/$0.075, Claude 3 Sonnet $0.003/$0.015, Claude 3 Haiku $0.00025/$0.00125.

Key Insight: Output tokens cost 2-5x more than input tokens. Limiting output length has outsized impact on costs.

## Prompt Engineering for Efficiency

### Eliminate Redundancy
Bad (127 tokens): "You are a helpful assistant. Please help me with the following task. I would like you to analyze the following text and provide me with a summary..."
Optimized (38 tokens): "Summarize the key points: [text]"
Savings: 70% token reduction, identical output quality.

### Use Structured Formats
JSON and structured outputs reduce token waste from verbose natural language.

### Few-Shot Learning Optimization
Use minimum examples needed (1-3 usually sufficient), keep examples concise, share common prefixes.

## Context Caching Strategies

Context caching is the single most effective optimization for applications with repeated static content. Providers like OpenAI and Anthropic cache prompt prefixes that appear across multiple requests. Cached portions cost 50-90% less.

Requirements: Minimum cacheable content 1024 tokens (OpenAI) or 2048 tokens (Anthropic). Cache TTL: 5-60 minutes. Content must be identical and appear at prompt start.

Real-world Impact: Applications with knowledge bases or lengthy instructions see 60-80% cost reduction.

## Model Selection Strategy

The Model Ladder:
1. GPT-4 / Claude Opus - Complex reasoning, creative tasks, critical accuracy
2. GPT-4o / Claude Sonnet - Balanced performance/cost, general purpose
3. GPT-3.5 / Claude Haiku - Simple tasks, classification, extraction
4. Fine-tuned smaller models - Specialized repetitive tasks

### Routing Pattern
Route based on task complexity. Case Study: A chatbot routing 80% of queries to GPT-3.5 and 20% to GPT-4 reduced costs by 75%.

## Batch Processing

For non-time-sensitive workloads, batch processing offers 50% discounts from most providers. OpenAI Batch API provides 50% discount with 24hr processing window.

Use Cases: Data labeling, content generation, report generation, batch translations, synthetic data generation.

## Output Control Techniques

Since output tokens cost 2-5x more: set max_tokens limits, use stop sequences, request concise formats ("Answer in under 50 words", "Return JSON only, no explanation").

## RAG Optimization

Efficient RAG: Retrieve relevant chunks (top_k=3, not too many), compress chunks (remove redundancy), truncate to token limit, use structured prompt.

Optimization: Use semantic chunking (not fixed-size), remove markdown from retrieved chunks, implement re-ranking, consider chunk summarization.

## Response Caching

Cache identical or similar requests to avoid API calls entirely. Semantic Caching: use vector embeddings to find cached responses for similar (not identical) queries.

## Advanced Techniques

- Prompt Compression Models: LongLLMLingua, AutoCompressors can achieve 10x compression while maintaining 90%+ task performance.
- Speculative Decoding: Run small model alongside large model to predict tokens, 2-3x speedup and cost reduction.
- Quantization: 4-bit (75% memory reduction, minimal quality loss), 8-bit (50% memory reduction, negligible quality loss).

## Real-World Case Study

Customer support chatbot, 100K requests/month.
Before: GPT-4 for all, 800 avg input tokens, 300 avg output tokens, Cost: $4,200/month.
After: Model routing (80% GPT-3.5, 20% GPT-4), Context caching (70%), Prompt compression (40%), Response caching (15% hit rate).
Effective cost: $780/month. Savings: 81% ($3,420/month).
