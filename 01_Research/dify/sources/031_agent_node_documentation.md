---
source_id: "031"
title: "Agent Node - Dify Official Documentation"
url: "https://docs.dify.ai/en/use-dify/nodes/agent"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify agent node", "Dify agent strategy"]
content_length: 3820
---

# Agent Node - Dify Docs

The Agent node gives your LLM autonomous control over tools, enabling it to iteratively decide which tools to use and when to use them. Instead of pre-planning every step, the Agent reasons through problems dynamically, calling tools as needed to complete complex tasks.

## Agent Strategies

Agent strategies define how your Agent thinks and acts. Choose the approach that best matches your model's capabilities and task requirements.

### Function Calling

Uses the LLM's native function calling capabilities to directly pass tool definitions through the tools parameter. The LLM decides when and how to call tools using its built-in mechanism. Best for models like GPT-4, Claude 3.5, and other models with robust function calling support.

### ReAct (Reason + Act)

Uses structured prompts that guide the LLM through explicit reasoning steps. Follows a Thought > Action > Observation cycle for transparent decision-making. Works well with models that may not have native function calling or when you need explicit reasoning traces.

Install additional strategies from Marketplace > Agent Strategies or contribute custom strategies to the community repository (https://github.com/langgenius/dify-plugins).

## Configuration

### Model Selection

Choose an LLM that supports your selected agent strategy. More capable models handle complex reasoning better but cost more per iteration. Ensure your model supports function calling if using that strategy.

### Tool Configuration

Configure the tools your Agent can access. Each tool requires:
- Authorization: API keys and credentials for external services configured in your workspace
- Description: Clear explanation of what the tool does and when to use it (this guides the Agent's decision-making)
- Parameters: Required and optional inputs the tool accepts with proper validation

### Instructions and Context

Define the Agent's role, goals, and context using natural language instructions. Use Jinja2 syntax to reference variables from upstream workflow nodes. Query specifies the user input or task the Agent should work on. This can be dynamic content from previous workflow nodes.

### Execution Controls

Maximum Iterations sets a safety limit to prevent infinite loops. Configure based on task complexity - simple tasks need 3-5 iterations, while complex research might require 10-15.

Memory controls how many previous messages the Agent remembers using TokenBufferMemory. Larger memory windows provide more context but increase token costs. This enables conversational continuity where users can reference previous actions.

### Tool Parameter Auto-Generation

Tools can have parameters configured as auto-generated or manual input. Auto-generated parameters (auto: false) are automatically populated by the Agent, while manual input parameters require explicit values that become part of the tool's permanent configuration.

## Output Variables

Agent nodes provide comprehensive output including:
- Final Answer: The Agent's ultimate response to the query
- Tool Outputs: Results from each tool invocation during execution
- Reasoning Trace: Step-by-step decision process (especially detailed with ReAct strategy) available in the JSON output
- Iteration Count: Number of reasoning cycles used
- Success Status: Whether the Agent completed the task successfully
- Agent Logs: Structured log events with metadata for debugging and monitoring tool invocations

## Use Cases

- Research and Analysis: Agents can autonomously search multiple sources, synthesize information, and provide comprehensive answers.
- Troubleshooting: Diagnostic tasks where the Agent needs to gather information, test hypotheses, and adapt its approach based on findings.
- Multi-step Data Processing: Complex workflows where the next action depends on intermediate results.
- Dynamic API Integration: Scenarios where the sequence of API calls depends on responses and conditions that can't be predetermined.

## Best Practices

- Clear Tool Descriptions help the Agent understand when and how to use each tool effectively.
- Appropriate Iteration Limits prevent runaway costs while allowing sufficient flexibility for complex tasks.
- Detailed Instructions provide context about the Agent's role, goals, and any constraints or preferences.
- Memory Management: balance context retention with token efficiency based on your use case requirements.
