---
source_id: "065"
title: "Tool Plugin Development Guide - Dify Docs"
url: "https://docs.dify.ai/en/develop-plugin/dev-guides-and-walkthroughs/tool-plugin"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify plugin development", "Dify plugin system"]
content_length: 8920
---

# Tool Plugin Development Guide

Tools refer to third-party services that can be called by Chatflow / Workflow / Agent-type applications, providing complete API implementation capabilities to enhance Dify applications. For example, adding extra features like online search, image generation, and more.

A "Tool Plugin" refers to a complete project that includes tool provider files, functional code, and other structures. A tool provider can include multiple Tools.

This guide uses Google Search as an example to demonstrate how to quickly develop a tool plugin.

## Prerequisites

- Dify plugin scaffolding tool (dify-plugin-daemon)
- Python environment, version >= 3.12

## Creating a New Project

Run the scaffolding command line tool to create a new Dify plugin project:

```
dify plugin init
```

## Choosing Plugin Type and Template

All templates in the scaffolding tool provide complete code projects. Select the Tool plugin type.

### Configuring Plugin Permissions

Grant the following permissions to the plugin:
- Tools
- Apps
- Enable persistent storage Storage
- Allow registering Endpoints

## Developing the Tool Plugin

### 1. Creating the Tool Provider File

The tool provider file is a YAML format file that serves as the basic configuration entry for the tool plugin, providing authorization information to the tool.

Example `google.yaml`:
```yaml
identity:
    author: Your-name
    name: google
    label:
        en_US: Google
    description:
        en_US: Google
    icon: icon.svg
    tags:
        - search
```

Supported tags: search, image, videos, weather, finance, design, travel, social, news, medical, productivity, education, business, entertainment, utilities, other.

### 2. Completing Third-Party Service Credentials

Add `credentials_for_provider` field to the YAML file for API keys. The tool provider YAML includes `credentials_for_provider` for third-party service authentication, `tools` list referencing tool YAML files, and `extra.python.source` pointing to the provider's Python implementation.

### 3. Filling in the Tool YAML File

Each tool function needs a YAML file describing basic information, parameters, and output. Parameters have key attributes:
- `name`: unique parameter name
- `type`: string, number, boolean, select, secret-input
- `label`: frontend display label
- `form`: llm (LLM-inferred) or form (user-preset)
- `required`: whether required
- `human_description`: frontend description
- `llm_description`: description passed to LLM

### 4. Preparing Tool Code

Create tool functionality code extending the `Tool` class from `dify_plugin`:

```python
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GoogleSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        params = {
            "api_key": self.runtime.credentials["serpapi_api_key"],
            "q": tool_parameters["query"],
            "engine": "google",
        }
        response = requests.get(url=SERP_API_URL, params=params, timeout=5)
        response.raise_for_status()
        valuable_res = self._parse_response(response.json())
        yield self.create_json_message(valuable_res)
```

### 5. Completing the Tool Provider Code

Create provider implementation code with credential validation logic:

```python
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

class GoogleProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in GoogleSearchTool.from_credentials(credentials).invoke(
                tool_parameters={"query": "test", "result_type": "link"},
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
```

## Debugging the Plugin

Dify provides remote debugging. Go to Plugin Management page to obtain the remote server address and debugging Key. Fill in `.env` file:

```
INSTALL_METHOD=remote
REMOTE_INSTALL_URL=debug.dify.ai:5003
REMOTE_INSTALL_KEY=********-****-****-****-************
```

Run `python -m main` to start the plugin.

## Packaging the Plugin (Optional)

Package using: `dify plugin package ./google`

This creates a `google.difypkg` file as the final plugin package.

## Publishing the Plugin (Optional)

To publish to Dify Marketplace, ensure the plugin follows the Publish to Dify Marketplace specifications. After review, the code will be merged and launched to Dify Marketplace.

## Related Documentation

- Extension Plugin development (Endpoints)
- Model Plugin development
- Bundle Plugins (packaging multiple plugins)
- General Specifications (Manifest Structure)
- Reverse Invocation (calling Dify capabilities from plugins)
- Remote Debugging Plugins
- Persistent Storage (KV store in plugins)
