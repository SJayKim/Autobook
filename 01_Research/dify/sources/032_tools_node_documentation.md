---
source_id: "032"
title: "Tools Node - Dify Official Documentation"
url: "https://docs.dify.ai/en/use-dify/nodes/tools"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify tool integration", "Dify agent node"]
content_length: 3250
---

# Tools Node - Dify Docs

The Tools node connects your workflow to external services and APIs through pre-built integrations. Unlike HTTP Request nodes, Tools provide structured interfaces, built-in error handling, and simplified configuration for popular services.

## Tool Types

Dify supports multiple types of tools to handle different integration needs:

### Built-in Tools

Ready-to-use integrations maintained by Dify for popular services including Google Search, weather APIs, productivity tools, and AI services. These tools require minimal configuration and provide reliable, tested integrations.

### Custom Tools

Import your own tools using OpenAPI/Swagger specifications. Perfect for internal APIs, specialized services, or any API not covered by built-in options. Configure once and reuse across multiple workflows.

### Workflow Tools

Publish complex workflows as reusable tools. This creates modular building blocks that can be shared across different applications, promoting code reuse and simplifying maintenance.

### MCP Tools

Tools from external MCP (Model Context Protocol) servers that provide specialized capabilities. Connect to a growing ecosystem of MCP servers for expanded functionality.

## Configuration

### Authentication

Many tools require API keys or OAuth authentication. Configure these credentials in the Tools section of your workspace before using them in workflows. Authentication is handled automatically once configured.

### Input Parameters

Tools provide structured forms with validation for input configuration. Set parameters using variables from previous workflow nodes. The interface automatically handles data type validation and provides helpful descriptions for each parameter.

### Output Handling

Tools return structured data that becomes available as variables for downstream nodes. Output schemas are predefined, ensuring compatibility and reducing integration complexity.

## Advantages Over HTTP Requests

- Structured Interfaces: Form-based configuration with built-in validation, making setup easier than manual HTTP request configuration.
- Built-in Error Handling: Automatic retry logic and error management, reducing the complexity of handling API failures.
- Type Safety: Input and output schemas maintain data compatibility between workflow nodes.
- Documentation: Usage examples and detailed parameter descriptions for each tool.

## Error Handling and Retries

Configure robust error handling for tools that depend on external services:

- Retry Settings: Automatically retry failed tool executions up to 10 times with configurable intervals (maximum 5000ms). This handles temporary service issues or network problems.
- Error Handling: Defines alternative workflow paths when tool execution fails, ensuring your workflow continues even when external services are unavailable.

## Creating Custom Tools

- OpenAPI Integration: Import any service with an OpenAPI/Swagger specification. Once imported, the service becomes available as a tool with the same ease of use as built-in options.
- Workflow Publishing: Converts multi-node workflows into single-node tools that can be reused across different applications. This promotes modularity and simplifies complex workflow management.

## Tool Management

Access tool configuration through Tools in your workspace navigation. Here you can manage authentication credentials, import custom tools, configure MCP servers, and publish workflows as tools. For detailed guidance on tool creation, management, and publishing workflows as tools, see the Plugin Development Guide.
