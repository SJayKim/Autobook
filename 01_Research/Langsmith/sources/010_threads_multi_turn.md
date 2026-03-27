---
source_id: 010
title: "LangSmith — Configure Threads for Multi-Turn Conversations (session_id, thread_id)"
url: "https://docs.langchain.com/langsmith/threads"
type: docs
scraped_at: 2026-03-27
keywords: ["tracing", "tags and metadata", "runs"]
content_length: 3280
---

# LangSmith — Configure Threads for Multi-Turn Conversations (session_id, thread_id)

## Overview

LangSmith uses *threads* to organize multi-turn conversations. "A *thread* is a sequence of traces representing a single conversation. Each response is represented as its own trace, but these traces are linked together by being part of the same thread."

## Metadata Keys for Thread Association

To group traces into threads, pass metadata using one of these key names:

- `session_id`
- `thread_id`
- `conversation_id`

The documentation recommends UUID values (e.g., `f47ac10b-58cc-4372-a567-0e02b2c3d479`).

## Critical Implementation Detail

"To ensure filtering and token counting work correctly across your entire thread, you must set the thread metadata on **all runs**, including child runs within a trace." Without proper propagation to child runs, filtering, token usage calculation, and cost aggregation will be incomplete.

## Python Implementation Example

```python
import openai
from langsmith import traceable, Client
from langsmith.wrappers import wrap_openai

langsmith_client = Client()
client = wrap_openai(openai.Client())

THREAD_ID = "thread-id-1"

@traceable(name="Chat Bot", metadata={"thread_id": THREAD_ID})
def chat_pipeline(messages: list, get_chat_history: bool = False):
    if get_chat_history:
        history_messages = get_thread_history(THREAD_ID)
        all_messages = history_messages + messages
    else:
        all_messages = messages

    chat_completion = client.chat.completions.create(
        model="gpt-4.1-mini", messages=all_messages
    )

    response_message = chat_completion.choices[0].message
    full_conversation = all_messages + [
        {"role": response_message.role, "content": response_message.content}
    ]
    save_thread_history(THREAD_ID, full_conversation)
    return {"messages": full_conversation}

# Turn 1
chat_pipeline([{"content": "Hi, my name is Sally", "role": "user"}], get_chat_history=False)

# Turn 2
chat_pipeline([{"content": "What is my name", "role": "user"}], get_chat_history=True)
```

## TypeScript Implementation Example

```typescript
import { traceable } from "langsmith/traceable";
import { wrapOpenAI } from "langsmith/wrappers";
import OpenAI from "openai";

const client = wrapOpenAI(new OpenAI());
const THREAD_ID = "thread-id-1";

type Message = { role: string; content: string };

const chatPipeline = traceable(
    async function chatPipeline({
        messages,
        get_chat_history = false
    }: { messages: Message[]; get_chat_history?: boolean }) {
        if (get_chat_history) {
            const historyMessages = getThreadHistory(THREAD_ID);
            messages = [...historyMessages, ...messages];
        }

        const chatCompletion = await client.chat.completions.create({
            model: "gpt-4.1-mini", messages,
        });

        const responseMessage = chatCompletion.choices[0].message;
        const fullConversation = [
            ...messages,
            { role: responseMessage.role, content: responseMessage.content ?? "" },
        ];
        saveThreadHistory(THREAD_ID, fullConversation);
        return { messages: fullConversation };
    },
    { name: "Chat Bot", metadata: { thread_id: THREAD_ID } }
);
```

## Viewing Threads in LangSmith

Access threads through the **Threads** tab in any project's details page. Individual threads can be viewed in two formats:

1. **Thread overview**: A chatbot-like UI displaying inputs/outputs for each conversation turn
2. **Trace view**: Similar to single-run trace viewing, with easy access to all runs in the thread

Keyboard shortcut `T` toggles between these views.

The thread overview supports **JSON path syntax** with negative indexing (e.g., `inputs.messages[-1].content`) to access specific message elements.

## Feedback Aggregation

When viewing a thread, feedback aggregates across all runs, displaying average scores when multiple runs share the same evaluation criteria.
