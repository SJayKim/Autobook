---
source_id: "042"
title: "Model Providers - Dify Docs"
url: "https://docs.dify.ai/en/use-dify/workspace/model-providers"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify model providers", "Dify supported models", "model configuration", "LLM integration"]
content_length: 5940
---

Model providers give your workspace access to AI models. Every application you build needs models to function, and configuring providers at the workspace level means all team members can use them across all projects.

System vs Custom Providers

System Providers are managed by Dify. You get immediate access to models without setup, billing through your Dify subscription, and automatic updates when new models become available. Best for getting started quickly.

Custom Providers use your own API keys for direct access to model providers like OpenAI, Anthropic, or Google. You get full control, direct billing, and often higher rate limits. Best for production applications.

You can use both simultaneously -- system providers for prototyping, custom providers for production.

Configure Custom Providers

Only workspace admins and owners can configure model providers. The process is consistent across providers:
1. Navigate to Settings -> Model Providers
2. Select your provider (OpenAI, Anthropic, Google, Cohere, or other supported providers)
3. Add credentials (API key and any additional configuration)
4. Test and save (Dify validates your credentials before making the provider available)

Supported Providers

Large Language Models: OpenAI (GPT-4, GPT-3.5-turbo), Anthropic (Claude), Google (Gemini), Cohere, Local models via Ollama.

Embedding Models: OpenAI Embeddings, Cohere Embeddings, Azure OpenAI, Local embedding models.

Specialized Models: Image generation (DALL-E, Stable Diffusion), Speech (Whisper, ElevenLabs), Moderation APIs.

Provider Configuration Examples

OpenAI: Required: API Key from OpenAI Platform. Optional: Custom base URL for Azure OpenAI or proxies, Organization ID for organization-scoped usage. Available Models: GPT-4, GPT-3.5-turbo, DALL-E, Whisper, Text embeddings.

Anthropic: Required: API Key from Anthropic Console. Available Models: Claude 3 (Opus, Sonnet, Haiku), Claude 2.1, Claude Instant.

Local (Ollama): Required: Ollama server URL (typically http://localhost:11434). Setup: Install Ollama, pull models (ollama pull llama2), configure Dify connection. Benefits: Complete data privacy, no external API costs, custom model fine-tuning.

Manage Model Credentials

Add multiple credentials for a model provider's predefined and custom models, and easily switch between, delete, or modify these credentials. Scenarios where adding multiple credentials is helpful:
- Environment Isolation: Configure separate model credentials for different environments (development, testing, production).
- Cost Optimization: Add and switch between multiple credentials from different accounts or model providers to maximize free or low-cost quotas.
- Model Testing: During model fine-tuning or iteration, quickly switch between model versions to test and evaluate performance.

Configure Model Load Balancing

Load balancing is a paid feature (SaaS subscription or Enterprise license). Model providers typically enforce rate limits on API access. For enterprise applications, a high volume of concurrent requests from a single credential can easily trigger these limits.

Dify employs a round-robin strategy for load balancing, sequentially routing model requests to each credential in the load balancing pool. If a credential hits a rate limit, it is temporarily removed from rotation for one minute.

Access and Billing

System providers are billed through your Dify subscription with usage limits based on your plan. Custom providers bill you directly through the provider (OpenAI, Anthropic, etc.) and often provide higher rate limits.

Team access follows workspace permissions:
- Owners/Admins can configure, modify, and remove providers
- Editors/Members can view available providers and use them in applications

API keys are stored securely but grant workspace-wide model access. Only give admin privileges to trusted team members who should have billing responsibility.
