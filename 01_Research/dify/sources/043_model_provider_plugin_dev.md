---
source_id: "043"
title: "Model Provider Plugin Development - Dify Docs"
url: "https://docs.dify.ai/en/develop-plugin/dev-guides-and-walkthroughs/creating-new-model-provider"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify model provider plugin", "predefined model", "customizable model", "plugin development"]
content_length: 8450
---

This comprehensive guide provides detailed instructions on creating model provider plugins, covering project initialization, directory structure organization, model configuration methods, writing provider code, and implementing model integration.

Prerequisites: Dify CLI, basic Python programming skills and understanding of OOP, familiarity with the API documentation of the model provider you want to integrate.

Step 1: Create and Configure a New Plugin Project

Initialize the project with `dify plugin init`. Select the LLM type plugin template. Configure permissions: Models (base permission), LLM (large language model functionality), Storage (file operations if needed).

Directory Structure:
```
models/my_provider/
  models/
    llm/
      _position.yaml
      model1.yaml
      llm.py
    text_embedding/
      _position.yaml
      embedding-model.yaml
      text_embedding.py
  provider/
    my_provider.py
  manifest.yaml
```

Step 2: Understand Model Configuration Methods

Dify supports two model configuration methods:

Predefined Models (predefined-model): Models that only require unified provider credentials to use. Once a user configures their API key, they can immediately access all predefined models. Example: OpenAI provider offers gpt-3.5-turbo-0125 and gpt-4o-2024-05-13.

Custom Models (customizable-model): Require additional configuration for each specific model instance. Useful when models need individual parameters beyond provider-level credentials. Example: Xinference supports both LLM and Text Embedding, but each model has a unique model_uid.

These configuration methods can coexist within a single provider. A provider might offer some predefined models while also allowing users to add custom models with specific configurations.

Step 3: Create Model Provider Files

Two main components: Provider Configuration YAML File (defines basic information, supported model types, credential requirements) and Provider Class Implementation (implements authentication validation).

The provider YAML includes: provider identifier, display labels, description, icons, help information, supported_model_types (e.g., llm), configurate_methods (e.g., predefined-model), provider_credential_schema (credential form definitions like API key fields).

Provider class must inherit from ModelProvider and implement validate_provider_credentials method. This method is called whenever a user saves provider credentials. It should attempt API call validation, return silently on success, or raise CredentialsValidateFailedError on failure.

For custom model providers (like Xinference), validation happens at the model level, so the provider-level validate method can pass.

Step 4: Implement Model-Specific Code

Create model YAML files for each model defining: model identifier, label, model_type, features (agent-thought, vision, tool-call, stream-tool-call, document), model_properties (mode: chat/completion, context_size), parameter_rules (temperature, top_p, max_tokens), and pricing.

Implement model calling code in Python. The core _invoke method handles: transforming Dify's standardized inputs into provider API format, making API calls with error handling, transforming responses back to Dify format, handling both streaming and non-streaming modes.

Key methods to implement: _invoke (core API communication), validate_credentials (credential validation), get_num_tokens (optional token estimation), _invoke_error_mapping (map vendor exceptions to Dify standard exceptions).

Step 5: Debug and Test

Dify provides remote debugging: get debug key from Plugin Management, configure .env with INSTALL_METHOD=remote, REMOTE_INSTALL_HOST, PORT, KEY. Run with `python -m main`.

Step 6: Package and Publish

Package with `dify plugin package models/<provider_name>`. Submit pull request to dify-official-plugins repository.
