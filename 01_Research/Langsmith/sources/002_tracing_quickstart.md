---
source_id: 002
title: "LangSmith Tracing Quickstart — Setup, Environment Variables, First Trace"
url: "https://docs.langchain.com/langsmith/observability-quickstart"
type: docs
scraped_at: 2026-03-27
keywords: ["tracing", "runs", "projects"]
content_length: 3210
---

# LangSmith Tracing Quickstart — Setup, Environment Variables, First Trace

## Overview

LangSmith provides observability for LLM applications through tracing, which captures the complete record of how your application handles requests. The platform records individual "runs" representing specific operations like LLM calls or retrieval steps.

## Prerequisites

- A LangSmith account at smith.langchain.com
- A LangSmith API key (generated from your account settings)
- An OpenAI API key from the OpenAI dashboard

## Step 1: Project Setup

```bash
# Python
mkdir ls-observability-quickstart && cd ls-observability-quickstart
python -m venv .venv && source .venv/bin/activate
pip install -U langsmith openai

# TypeScript
mkdir ls-observability-quickstart-ts && cd ls-observability-quickstart-ts
npm init -y
npm install langsmith openai typescript ts-node
```

## Step 2: Environment Configuration

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="<your-langsmith-api-key>"
export OPENAI_API_KEY="<your-openai-api-key>"
export LANGSMITH_WORKSPACE_ID="<your-workspace-id>"
```

The workspace ID is optional if your API key is linked to a single workspace. By default, traces go to a project named `"default"`.

## Step 3: Instrument LLM Calls with wrap_openai

Wrap the OpenAI client using LangSmith's wrapper to automatically log model interactions:

**Python:**
```python
from langsmith.wrappers import wrap_openai
from openai import OpenAI

client = wrap_openai(OpenAI())
```

**TypeScript:**
```typescript
import { wrapOpenAI } from "langsmith/wrappers";
import OpenAI from "openai";

const client = wrapOpenAI(new OpenAI());
```

Run your application and check the LangSmith UI to see the traced LLM call in your default tracing project.

## Step 4: Trace the Entire Application with @traceable

Use the `@traceable` decorator to capture your complete application pipeline:

**Python:**
```python
from langsmith import traceable

@traceable
def rag(question: str) -> str:
    docs = retriever(question)
    system_message = (
        "Answer the user's question using only the provided information below:\n"
        + "\n".join(docs)
    )
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question},
        ],
    )
    return resp.choices[0].message.content
```

**TypeScript:**
```typescript
import { traceable } from "langsmith/wrappers";

const rag = traceable(async (question: string) => {
    const docs = retriever(question);
    const systemMessage =
        "Answer the user's question using only the provided information below:\n" +
        docs.join("\n");

    const resp = await client.chat.completions.create({
        model: "gpt-4.1-mini",
        messages: [
            { role: "system", content: systemMessage },
            { role: "user", content: question },
        ],
    });

    return resp.choices[0].message?.content;
});
```

## Key Environment Variables

| Variable | Purpose |
|---|---|
| `LANGSMITH_TRACING` | Enables/disables tracing (`true`/`false`) |
| `LANGSMITH_API_KEY` | Authentication key for LangSmith API |
| `LANGSMITH_PROJECT` | Target project name (default: `"default"`) |
| `LANGCHAIN_PROJECT` | Legacy alias for older JS SDK versions (<0.2.16) |
| `LANGSMITH_WORKSPACE_ID` | Multi-workspace routing |
