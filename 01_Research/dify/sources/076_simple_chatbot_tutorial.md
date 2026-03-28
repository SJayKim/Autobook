---
source_id: "076"
title: "Simple Chatbot - Dify Docs Tutorial"
url: "https://docs.dify.ai/en/use-dify/tutorials/simple-chatbot"
type: "tutorial"
scraped_at: "2026-03-27"
keywords: ["Dify chatbot tutorial", "Dify workflow tutorial", "Dify use cases"]
content_length: 3850
---

# Simple Chatbot - Dify Docs Tutorial

The real value of Dify lies in how easily you can build, deploy, and scale an idea no matter how complex. It's built for fast prototyping, smooth iteration, and reliable deployment at any level. This guide walks through building a simple chatbot that classifies the user's question, responds directly using the LLM, and enhances the response with a country-specific fun fact.

## Step 1: Create a New Workflow (2 min)

Go to Studio > Workflow > Create from Blank > Orchestrate > New Chatflow > Create

## Step 2: Add Workflow Nodes (6 min)

When you want to reference any variable, type `{` or `/` first and you can see the different variables available in your workflow.

### 1. LLM Node and Output: Understand and Answer the Question

`LLM` node sends a prompt to a language model to generate a response based on user input. It abstracts away the complexity of API calls, rate limits, and infrastructure, so you can just focus on designing logic.

1. Create an LLM node using the Add Node button and connect it to your Start node
2. Choose a default model
3. Set System Prompt:

```
The user will ask a question about a country. The question is {{sys.query}}
Tasks:
1. Identify the country mentioned.
2. Rephrase the question clearly.
3. Answer the question using general knowledge.

Respond in the following JSON format:
{
  "country": "<country name>",
  "question": "<rephrased question>",
  "answer": "<direct answer to the question>"
}
```

4. Enable Structured Output: Toggle Output Variables Structured ON > Configure and click Import from JSON. Paste:

```json
{
  "country": "string",
  "question": "string",
  "answer": "string"
}
```

### 2. Code Block: Get Fun Fact

`Code` node executes custom logic using code. It lets you inject code exactly where needed within a visual workflow, saving you from wiring up an entire backend.

1. Create a Code Node using the Add Node button and connect to LLM block
2. Change one Input Variable name to "country" and set the variable to structured_output > country
3. Paste Python code with a dictionary of fun facts per country
4. Change output variable result to fun_fact

### 3. Answer Node: Final Answer to User

Create an Answer Node and configure the Answer Field:

```
Q: {{ structured_output.question }}
A: {{ structured_output.answer }}
Fun Fact: {{ fun_fact }}
```

## Step 3: Test the Bot (3 min)

Click Preview, then ask:
- "What is the capital of France?"
- "Tell me about Japanese cuisine"
- "Describe the culture in Italy"
- Any other questions

## Conclusion

This guide showed how to integrate language models reliably and scalably without reinventing infrastructure. With Dify's visual workflows and modular nodes, you're not just building faster, you're adopting a clean, production-ready architecture for LLM-powered apps.
