---
source_id: "052"
title: "Dify v1.6.0: Built-in Two-Way MCP Support - Dify Blog"
url: "https://dify.ai/blog/v1-6-0-built-in-two-way-mcp-support"
type: "blog"
scraped_at: "2026-03-27"
keywords: ["Dify MCP server", "Dify API", "Dify application publishing"]
content_length: 4850
---

# Dify v1.6.0: Built-in Two-Way MCP Support

Dify now integrates MCP natively, so you can use any MCP server as a tool or expose your Dify agents and workflows as MCP servers.

Published: Jul 10, 2025

AI applications are quickly moving beyond simple conversation. To act effectively, an agent must reach external data, APIs, calendars, and code bases. Until now that meant writing large amounts of custom glue code, which was costly to build and hard to scale.

The Model Context Protocol (MCP) standardizes how AI agents discover and use outside servers. In Dify v1.6.0, MCP is built in both directions:

- Call any MCP server directly from Dify.
- Expose your own Dify agents or workflows as MCP servers for other clients.

## Three Ways to Use MCP in Dify

### 1. Configure an MCP Server as a Tool

On the Tools page, select MCP and add a server such as Linear, Notion (native MCP apps) or Zapier, Composio (integration platforms). One Zapier configuration unlocks more than 8,000 authorized apps.

Note: HTTP-based MCP servers only. Protocol version 2025-03-26.

Example Linear setup:
1. Tools > MCP > Add MCP Server
2. Enter the Linear MCP URL, a display name, and a server identifier.
3. Complete authorization. You now have 22 Linear tools for creating, updating, and querying projects, issues, comments, documents, teams, and users.

### 2. Let an Agent Call MCP Tools Intelligently

Define the agent's role in the prompt and attach the Linear server. When a user asks to create an issue for the R&D team, the agent selects get_team, get_user, and create_issue, then creates and assigns the task automatically.

### 3. Orchestrate MCP Tools in a Workflow

**Dynamic Path: Agent Node** - Insert an agent node into a workflow. The agent chooses the right tools at runtime. Ideal for complex, varied tasks such as triaging user feedback into three specialized agents:
- Positive Feedback Agent -> forwards highlights to Marketing.
- Technical Issue Agent -> creates bug tasks for Support.
- Product Suggestion Agent -> generates structured requirement docs for Product.

**Precise Path: Standalone MCP Nodes** - Add individual MCP tools as separate workflow nodes. You decide the call order, with no LLM decisions involved. This approach suits:
- Standardized business processes
- Strictly ordered task chains
- Situations with tight latency or cost constraints

You can enrich workflows by adding knowledge bases, notification plugins, or extra MCP servers to enable collaboration across platforms.

## Publish Your AI as an MCP Server

Any Dify agent or workflow can be exposed as a standard MCP endpoint:

1. **Service description**: State concisely what the workflow does, so external LLMs know when to invoke it.
2. **Parameter description**: Document every input on the Start node to ensure clients pass the correct values.

After you complete these two fields, Dify issues a server URL. From that address your workflow becomes a reusable MCP-standard server that tools such as Claude, Cursor, or any other MCP client can call directly.

## Ready for a Connected Future

Native MCP integration is more than a feature. It is a commitment to open standards. The applications you build today are already prepared for tomorrow's interconnected AI ecosystem.
