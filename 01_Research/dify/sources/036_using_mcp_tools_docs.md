---
source_id: "036"
title: "Using MCP Tools - Dify Official Documentation"
url: "https://docs.dify.ai/en/use-dify/build/mcp"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify MCP integration", "Dify tool integration", "Dify agent node"]
content_length: 3180
---

# Using MCP Tools - Dify Docs

Connect external tools from MCP servers to your Dify apps. Instead of just built-in tools, you can use tools from the growing MCP ecosystem (https://mcpservers.org/).

Only supports MCP servers with HTTP transport right now.

## Adding MCP Servers

Go to Tools > MCP in your workspace. Click Add MCP Server (HTTP):

- Server URL: Where the MCP server lives (like https://api.notion.com/mcp)
- Name & Icon: Call it something useful. Dify tries to grab icons automatically.
- Server ID: Unique identifier (lowercase, numbers, underscores, hyphens, max 24 chars)

Important: Never change the server ID once you start using it. This will break any apps that use tools from this server.

## What Happens Next

Dify automatically:
1. Connects to the server
2. Handles any OAuth stuff
3. Gets the list of available tools
4. Makes them available in your app builder

You'll see a server card once it finds tools.

## Managing Servers

Click any server card to:
- Update Tools: Refresh when the external service adds new tools
- Re-authorize: Fix auth when tokens expire
- Edit Settings: Change server details (but not the ID!)
- Remove: Disconnect the server (this breaks apps using its tools)

## Using MCP Tools

Once connected, MCP tools show up everywhere you'd expect:
- In agents: Tools appear grouped by server ("Notion MCP > Create Page")
- In workflows: MCP tools become available as nodes
- In agent nodes: Same as regular agents

## Customizing Tools

When you add an MCP tool, you can customize it:
- Description: Override the default description to be more specific
- Parameters: For each tool parameter, choose:
  - Auto: Let the AI decide the value
  - Fixed: Set a specific value that never changes

Example: For a search tool, set numResults to 5 (fixed) but keep query on auto.

## Sharing Apps

When you export apps that use MCP tools:
- The export includes server IDs
- To use the app elsewhere, add the same servers with identical IDs
- Document which MCP servers your app needs

## Troubleshooting

- "Unconfigured Server": Check the URL and re-authorize
- Missing tools: Hit "Update Tools"
- Broken apps: You probably changed a server ID. Add it back with the original ID.

## Tips

- Use permanent, descriptive server IDs like "github-prod" or "crm-system"
- Keep the same MCP setup across dev/staging/production
- Set fixed values for config stuff, auto for dynamic inputs
- Test MCP integrations before deploying
