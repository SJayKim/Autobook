---
source_id: 007
title: "LangSmith — Distributed Tracing (Context Propagation Headers, Cross-Service)"
url: "https://docs.langchain.com/langsmith/distributed-tracing"
type: docs
scraped_at: 2026-03-27
keywords: ["tracing", "runs"]
content_length: 3920
---

# LangSmith — Distributed Tracing (Context Propagation Headers, Cross-Service)

## Overview

LangSmith enables tracing across multiple services through built-in distributed tracing capabilities. The system uses context propagation headers to link runs within a trace across different services.

## Context Propagation Headers

- `langsmith-trace`: Primary identifier for connecting distributed traces
- `baggage`: Optional header for propagating metadata and tags across services

## Python: Client-Side (Extracting Headers)

On the client, extract the current run tree and convert it to headers:

```python
from langsmith.run_helpers import get_current_run_tree, traceable
import httpx

@traceable
async def my_client_function():
    headers = {}
    async with httpx.AsyncClient(base_url="...") as client:
        if run_tree := get_current_run_tree():
            headers.update(run_tree.to_headers())
        return await client.post("/my-route", headers=headers)
```

## Python: Server-Side (Receiving Headers)

### With FastAPI — TracingMiddleware (Recommended)

For ASGI frameworks like FastAPI and Starlette, use `TracingMiddleware` (available in `langsmith>=0.1.133`):

```python
from langsmith import traceable
from langsmith.middleware import TracingMiddleware
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(TracingMiddleware)

@traceable
async def some_function():
    ...

@app.post("/my-route")
async def fake_route(request):
    return await some_function()
```

### With Starlette

```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from langsmith.middleware import TracingMiddleware

middleware = [Middleware(TracingMiddleware)]
app = Starlette(..., middleware=middleware)
```

### Manual Context Management (Other Frameworks)

```python
import langsmith as ls
from fastapi import FastAPI, Request

@ls.traceable
async def my_application():
    ...

app = FastAPI()

@app.post("/my-route")
async def fake_route(request: Request):
    with ls.tracing_context(parent=request.headers):
        return await my_application()
```

Or pass headers directly via `langsmith_extra`:

```python
@app.post("/my-route")
async def fake_route(request: Request):
    my_application(langsmith_extra={"parent": request.headers})
```

## TypeScript: Client Setup

```typescript
import { getCurrentRunTree, traceable } from "langsmith/traceable";

const client = traceable(
    async () => {
        const runTree = getCurrentRunTree();
        return await fetch("...", {
            method: "POST",
            headers: runTree.toHeaders(),
        }).then((a) => a.text());
    },
    { name: "client" }
);

await client();
```

## TypeScript: Server Setup with Express.js

```typescript
import { RunTree } from "langsmith";
import { traceable, withRunTree } from "langsmith/traceable";
import express from "express";

const server = traceable(
    (text: string) => `Hello from the server! Received "${text}"`,
    { name: "server" }
);

const app = express();
app.post("/", async (req, res) => {
    const runTree = RunTree.fromHeaders(req.headers);
    const result = await withRunTree(runTree, () => server(req.body));
    res.send(result);
});
```

## TypeScript: Server Setup with Hono

```typescript
import { RunTree } from "langsmith";
import { traceable, withRunTree } from "langsmith/traceable";
import { Hono } from "hono";

const server = traceable(
    (text: string) => `Hello from the server! Received "${text}"`,
    { name: "server" }
);

const app = new Hono();
app.post("/", async (c) => {
    const body = await c.req.text();
    const runTree = RunTree.fromHeaders(c.req.raw.headers);
    const result = await withRunTree(runTree, () => server(body));
    return c.body(result);
});
```

## Key Concepts

- `run_tree.to_headers()`: Extracts current trace context as HTTP headers for outbound requests.
- `RunTree.fromHeaders(headers)`: Reconstructs run context from incoming HTTP headers on the server.
- `withRunTree(runTree, fn)`: Ensures proper propagation of run context within traceable function invocations, maintaining trace continuity across service boundaries.
- The `TracingMiddleware` handles header extraction automatically for ASGI apps.
