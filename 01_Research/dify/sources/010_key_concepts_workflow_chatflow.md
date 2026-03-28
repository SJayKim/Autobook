---
source_id: "010"
title: "Key Concepts - Dify Docs (Workflow, Chatflow, Variables)"
url: "https://docs.dify.ai/en/use-dify/getting-started/key-concepts"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify workflow", "Dify chatflow", "Dify workflow nodes"]
content_length: 4526
---

# Key Concepts - Dify Docs

## Dify App

Dify is made for agentic app building. In Studio, you can quickly build agentic workflows via a drag & drop interface and publish them as apps. You can access published apps via API, the web, or as an MCP server. Dify offers two main app types: workflow and chatflow. You will need to choose an app type when creating a new app.

We recommend choosing Workflow or Chatflow as your app type. But in addition to these, Dify also offers 3 more basic app types: Chatbot, Agent, and Text Generator. These app types run on the same workflow engine underneath, but come with simpler legacy interfaces.

## Workflow

Build workflow apps to handle single-turn tasks. The webapp interface and API provides easy access to batch execute many tasks at once.

Underneath it all, workflow forms the basis for all other app types in Dify.

You can specify how and when to start your workflow. There are two types of Start nodes:

- **User Input**: Direct user interaction or API call invokes the app.
- **Trigger**: The application runs automatically on a schedule or in response to a specific third-party event.

User Input and Trigger Start nodes are mutually exclusive -- they cannot be used on the same canvas. To switch between them, right-click the current start node > Change Node. Alternatively, delete the current start node and add a new one.

Only workflows started by User Input can be published as standalone web apps or MCP servers, exposed through backend service APIs, or used as tools in other Dify applications.

## Chatflow

Chatflow is a special type of workflow app that gets triggered at every turn of a conversation. Other than workflow features, chatflow comes with the ability to store and update custom conversation-specific variables, enable memory in LLM nodes, and stream formatted text, images, and files at different points throughout the chatflow run. Unlike workflow, chatflow can't use Trigger to start.

## Dify DSL

All Dify apps can be exported into a YAML file in Dify's own DSL (Domain-Specific Language) and you may create Dify apps from these DSL files directly. This makes it easy to port apps to other Dify instances and share with others.

## Variables

A variable is a labeled container to store information, so you can find and use that information later by referencing its name. You'll come across different types of variables when building a Dify app:

**Inputs**: You can specify any number of input variables at the User Input node for your app's end users to fill in.

### Workflow System Variables

| Variable Name | Data Type | Description |
| --- | --- | --- |
| sys.user_id | String | User ID: A unique identifier automatically assigned by the system to each user |
| sys.app_id | String | App ID: A unique identifier automatically assigned by the system to each App |
| sys.workflow_id | String | Workflow ID: Records information about all nodes in the current Workflow application |
| sys.workflow_run_id | String | Workflow Run ID: Used to record the runtime status and execution logs |
| sys.timestamp | Number | The start time of each workflow execution |

### Chatflow Additional System Variables

| Variable Name | Data Type | Description |
| --- | --- | --- |
| sys.conversation_id | String | A unique ID for the chatting box interaction session |
| sys.dialogue_count | Number | The number of conversation turns during the user's interaction |

User inputs are set at the start of each workflow run and cannot be updated.

**Outputs**: Each node produces one or more outputs that can be referenced in subsequent nodes.

**Environment Variables**: Use environment variables to store sensitive information like API keys specific to your app. This allows a clean separation between secrets and the Dify app itself, so you don't have to risk exposing passwords and keys when sharing your app's DSL.

**Conversation Variables (Chatflow only)**: These variables are conversation-specific -- meaning they persist over multi-turn chatflow runs in a single conversation so you can store and access dynamic information like to-do list and token cost. You can update the value of a conversation variable via the Variable Assigner node.

## Variable Referencing

You can easily pass variables to any node when configuring its input field by selecting from a dropdown. You can also insert variable values into complex text inputs by typing "/" slash, and selecting the desired variable from the dropdown.
