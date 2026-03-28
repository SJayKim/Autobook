---
source_id: "051"
title: "Turn Your Dify App into an MCP Server - Dify Blog"
url: "https://dify.ai/blog/turn-your-dify-app-into-an-mcp-server"
type: "blog"
scraped_at: "2026-03-27"
keywords: ["Dify MCP server", "Dify publish MCP", "Dify application publishing"]
content_length: 4520
---

# Turn Your Dify App into an MCP Server

With the mcp-server plugin, any Dify app can be turned into an MCP-compliant server endpoint, directly accessible by external MCP clients.

Published: Apr 14, 2025

## MCP Server Plugin: Connecting Dify to MCP Clients

The mcp-server plugin, contributed by the Dify community, is an Extension-type plugin. Once installed, it lets you turn any Dify app into an MCP-compliant server endpoint that external MCP clients can directly access. Here's what it does:

- **Exposes Dify as an MCP tool**: Turns your Dify app into a single MCP tool that clients like Cursor, Claude Desktop, Cline, Windsurf, or even other Dify instances can call.
- **Leverages Dify Endpoint**: After creating an app endpoint, you get a unique URL that MCP clients can use to connect.
- **Runs MCP services**: The plugin automatically starts an HTTP service in Dify's plugin environment, handling requests from MCP clients via HTTP and SSE protocols. This covers everything from protocol handshakes to capability discovery and tool execution.

## How to Set Up a Dify App as an MCP Server

### 1. Install the Plugin

Head to the Dify Marketplace, download, and install the mcp-server plugin.

### 2. Pick Your Dify App

Example uses the "Deep Research" app, which takes a user's question, runs multiple rounds of searches using the Tavily plugin (with the number of searches set by a depth parameter), and then uses an LLM to compile the results into a research report.

### 3. Configure the MCP Server Endpoint

In the mcp-server plugin's settings, fill out:

- **Endpoint Name**: Name your endpoint.
- **App**: Select the Dify app you want to publish as an MCP server.
- **App Type**: Choose whether it's a Chat or Workflow app.
- **App Input Schema**: Define the app's input parameters in JSON to help external systems understand how to interact with it.

Sample JSON for a deep_research app:

```json
{
  "name": "deep_research",
  "description": "Conduct in-depth research based on the user query.",
  "inputSchema": {
    "title": "deep_researchArguments",
    "type": "object",
    "properties": {
      "query": {
        "title": "User Query",
        "description": "The user's main question or topic for research.",
        "type": "string"
      },
      "depth": {
        "title": "Search Depth",
        "description": "Optional: Specifies the desired depth of the research.",
        "type": "number"
      }
    },
    "required": ["query"]
  }
}
```

Schema breakdown:
- **properties**: Lists all parameters the app accepts and their types.
- **description**: Explains the app's main function to MCP clients, helping them discover and use it.
- **required**: Specifies must-have parameters. For chat-based apps (Agent/Chatflow), query is typically required.

### 4. Get Your Endpoint URL

Once you save the config, the plugin generates a unique Endpoint URL (your MCP server address). This URL supports HTTP and SSE protocols, making it easy for MCP clients to connect and interact.

### 5. Add Dify MCP Server to Cursor

In Cursor IDE, update the MCP server settings:

```json
{
  "mcpServers": {
    "dify_deep_research": {
      "url": "https://*******.ai-plugin.io/sse"
    }
  }
}
```

Once set up, Cursor can use the Deep Research tool in Agent mode to run multi-step research, pulling in deeper insights to boost coding efficiency and quality.

## More Ways to Use It

Beyond dev tools, the Dify MCP Server is great for embedding AI into internal workflows. Think tasks like auto-classifying customer requests, summarizing reports, or extracting key info from documents, all built in Dify workflows and shared as MCP services via the plugin.

Unlike REST APIs, MCP is tailor-made for AI scenarios, making it easier for AI agents to discover and dynamically call tools. Agents can figure out how to use Dify services on their own, no hardcoding or manual setup required, which keeps things flexible and efficient.

Security note: For security, it is recommended to run the MCP Server plugin only in private network environments.

## Native MCP Support (v1.6.0+)

Dify v1.6.0 added built-in two-way MCP support. You can now publish your Dify agents or workflows as MCP servers natively by providing clear server and parameter descriptions, allowing any MCP-compatible client to discover and invoke your AI instantly. The native integration supports HTTP-based MCP services with protocol version 2025-03-26 and both pre-authorized and auth-free modes.
