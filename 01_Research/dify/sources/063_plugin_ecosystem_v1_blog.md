---
source_id: "063"
title: "Dify v1.0.0: Building a Vibrant Plugin Ecosystem"
url: "https://dify.ai/blog/dify-v1-0-building-a-vibrant-plugin-ecosystem"
type: "blog"
scraped_at: "2026-03-27"
keywords: ["Dify plugin system", "Dify marketplace"]
content_length: 6450
---

# Dify v1.0.0: Building a Vibrant Plugin Ecosystem

We're thrilled to announce the official launch of Dify v1.0.0, marking a major milestone for Dify as an AI application development platform. Notable highlights:

- **Version Upgrade:** Both the Dify Community and Dify Cloud have been upgraded to v1.0.0.
- **Plugins Mechanism**: A new plugin-based architecture with Models and Tools migrated to Plugins, introducing Agent Strategies, Extensions, and Bundles.
- **Workflow Enhancements**: The Agent node has been added for intelligent orchestration and task execution in Workflows and Chatflows.
- **Open Ecosystem**: The launch of Dify Marketplace to foster a thriving plugin ecosystem.

## New Paradigm in AI Application Development

With the rapid rise of generative AI, 2025 has ushered in significant innovations. Dify is committed to building the next-generation AI application platform, providing developers with four core capabilities:

- **Reasoning**: Integration of enhanced reasoning models for superior problem-solving.
- **Action**: Expanded AI ability to execute operations across digital and physical environments.
- **Dynamic Memory**: Optimized RAG and Memory mechanisms for improved context understanding.
- **Multimodal I/O**: Processing diverse data modalities for intuitive human-computer interactions.

## Plugin Architecture

Before v1.0.0, Dify faced a major challenge: models and tools were tightly integrated into the core platform, requiring changes to the core repository to add new features. To solve this, the architecture was restructured with four key advantages:

- **Modular Plugins:** Plugins are decoupled from Dify's core architecture, allowing models and tools to operate independently, enabling updates without a full platform upgrade.
- **Developer-Friendly Experience:** Standardized development protocols with comprehensive tool chain, remote debugging, code samples, and API documentation.
- **Hot-Swappable Design**: Dynamic plugin expansion and flexible usage.
- **Multiple Distribution Channels**:
  - **Dify Marketplace:** A platform for aggregating, distributing, and managing plugins, currently featuring 120+ plugins including:
    - Models: OpenAI o1-series, Gemini 2.0-series, DeepSeek-R1, OpenRouter, Ollama, Azure AI Foundry, Nvidia Catalog, etc.
    - Tools: Perplexity, Discord, Slack, Firecrawl, Jina AI, Stability, ComfyUI, Telegraph, etc.
  - **Community Sharing:** Free sharing on platforms like GitHub.
  - **Local Deployment:** Install from local package files for enterprise internal tools.

## Intelligent Workflow

The v1.0.0 release introduces the Agent node enhanced with reasoning strategies through Agent Strategy plugins:

- **Agent Node**: The decision-making center in workflows and chatflows, dynamically calling models based on strategies for resource scheduling, state management, inference recording, and tool selection.
- **Agent Strategies**: Decision logic abstracted into plugins with pre-set strategies like ReAct and Function Calling, supporting Chain-of-Thoughts and Tree-of-Thoughts.

## Open Ecosystem

- **Ecosystem Connectors: Extensions** that enable seamless integration with external platforms (e.g., Slack), facilitating data and functionality interoperability. Plugin Endpoints also support reverse calls to Dify's core capabilities.
- **Multimodal Interaction:** Support for multimodal models and tool plugins for image generation, voice interaction, and more.
- **Value-Sharing Platform:** Dify Marketplace serves as both a plugin distribution platform and a creative exchange hub.
- **Initial partners:** OpenRouter, Brave, E2B, SiliconFlow, Agora, Fish Audio, Dupdub, and more.

## Outlook

Dify will continue to decouple and open core capabilities through plugins, enhancing platform flexibility. A continuous partner network will create an open AI middleware platform connecting tools with users. Developer documentation and toolchain support will be improved, with community activities to co-build the ecosystem.
