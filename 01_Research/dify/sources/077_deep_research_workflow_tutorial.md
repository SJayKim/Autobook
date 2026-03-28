---
source_id: "077"
title: "Deep Research Workflow in Dify: A Step-by-Step Guide"
url: "https://dify.ai/blog/deep-research-workflow-in-dify-a-step-by-step-guide"
type: "tutorial"
scraped_at: "2026-03-27"
keywords: ["Dify workflow tutorial", "Dify use cases", "Dify RAG application tutorial"]
content_length: 7250
---

# Deep Research Workflow in Dify: A Step-by-Step Guide

Published: May 20, 2025. Authors: Evan Chen (Product Manager), Jing Yan (Technical Writer).

Standard search queries often fail with complex problems. For academic papers, market analyses, or code debugging, finding complete answers typically means piecing together dozens of separate searches. This is where Deep Research comes in. Leading AI platforms such as Google Gemini, ChatGPT, and DeepSeek-R1 now offer this powerful feature.

Deep Research stands out through its smart feedback loop: it identifies knowledge gaps, targets specific questions, explores systematically, and delivers comprehensive reports. Unlike traditional search that fragments information, Deep Research provides answers that go broad and dive down.

This guide shows how to build a Deep Research workflow with Dify using three key components: loop variables, structured outputs, and Agent nodes.

## Workflow Overview

This Deep Research workflow follows three phases:

1. **Intent Identification**: Capture research topic, gather initial context, and analyze goals to establish a clear direction.
2. **Iterative Exploration**: Use loop variables to assess knowledge, find gaps, run targeted searches, and build findings progressively.
3. **Synthesis**: All collected information becomes a structured report with proper citations.

It mirrors expert researchers' thinking: "What do I know already? What's missing? Where should I look next?"

## Phase One: Research Foundation

### Start Node

Configure the Start node with essential input parameters:
- **research topic**: The central question requiring exploration
- **max loop**: The iteration budget for this research session

### Background Knowledge Acquisition

Use the Exa Answer tool to gather preliminary information, ensuring the model understands terminology before going deeper.

### Intent Analysis

Use an LLM node to excavate the user's true intent, distinguishing between surface-level questions and further information needs.

## Phase Two: Dynamic Research Cycles

### Loop Node: The Research Engine

The Loop node powers the entire research. In Dify, it transfers information across iterations so each cycle builds on previous discoveries.

The workflow tracks six crucial variables:
- **findings**: New knowledge discovered in each cycle
- **executed_querys**: Previously used search queries (prevents redundancy)
- **current_loop**: Iteration counter
- **visited_urls**: Source tracking for proper citation
- **image_urls**: Visual content references
- **knowledge_gaps**: Identified information needs

Loop variables fundamentally differ from standard variables:
- Normal references follow a linear path: Node 1 -> Node 2 -> Node 3
- Loop with Previous Iteration Reference creates a knowledge network: nodes can access outputs from both current and previous iterations

This design accumulates knowledge, avoids redundant work, and sharpens focus with each cycle.

### Reasoning Node: Asking Better Questions

The Reasoning node works with a structured output format:

```json
{
    "reasoning": "Detailed justification for the chosen action path...",
    "search_query": "Specific follow-up question targeting knowledge gaps",
    "knowledge_gaps": "Information still needed to answer the original question"
}
```

By enabling Dify's structured output editor in an LLM node, you receive consistent JSON that downstream nodes can process reliably.

### Agent Node: Doing the Research

Agent nodes act as autonomous researchers by selecting the most suitable tools for each context. The workflow equips Agents with:

**Discovery Tools**:
- exa_search: Does web searches and collects results
- exa_content: Obtains full content from specific sources

**Analytical Tools**:
- think: Functions as the system's reflection engine, inspired by Claude's Think Tool. It enables the Agent to evaluate findings, identify patterns, and determine next steps.

Performance is optimized by providing Agents with only the search_query from the previous LLM node instead of the entire context.

### URL Extraction

The workflow automatically identifies URLs and visual references from Agent responses for proper source tracking.

### Variable Assignment

After each cycle, the Variable Assigner node updates the research state, ensuring each iteration builds on previous work rather than duplicating efforts.

## Phase Three: Research Synthesis

The Final Summary node takes all accumulated variables -- findings, sources, and supporting data -- to generate a comprehensive report. Answer nodes at strategic points provide streaming updates throughout the research.

## Conclusion

This Deep Research guide shows what Dify's agentic workflows can achieve. The future of research is not just about having more data -- it's about smarter ways to explore it.

## Reference

- https://github.com/dzhng/deep-research
- https://github.com/jina-ai/node-DeepResearch
- https://github.com/langchain-ai/local-deep-researcher
- https://github.com/nickscamara/open-deep-research
