---
source_id: 008
title: "LangSmith — Filter Traces in Application (Query Syntax, Tags, Metadata, SDK)"
url: "https://docs.langchain.com/langsmith/filter-traces-in-application"
type: docs
scraped_at: 2026-03-27
keywords: ["tags and metadata", "runs", "tracing"]
content_length: 2870
---

# LangSmith — Filter Traces in Application (Query Syntax, Tags, Metadata, SDK)

## Overview

LangSmith enables filtering of tracing project data to "quickly narrow down to specific runs for ad-hoc analysis" and "identify and examine errors, failed runs, and performance bottlenecks."

## Primary Filtering Methods

### UI-Based Filtering

Two main interfaces exist:

1. **Filter Bar** (top left of Tracing project page)
   - View dropdown for default and saved filters
   - Quick toggle between Traces or Runs
   - "+ Add filter" button for custom criteria

2. **Filter Shortcuts** (right sidebar)
   - Quick access to frequently occurring attributes

**Default behavior**: "The Traces filter is applied, which displays only top-level root runs." Switch to Runs to see all execution spans.

## Available Filter Operators

| Operator | Description |
|---|---|
| `is` / `is not` | Exact matching |
| `contains` / `does not contain` | Partial matching |
| `is one of` | Multiple value matching |
| `>` / `<` | Numeric field comparisons |

## Filtering Techniques

### By Tags and Metadata

"Run metadata and tags are also useful to filter on" when consistent tagging is implemented across pipelines. Filter by any metadata key-value pair, or by tag string.

### By Inputs and Outputs

**Full-Text Search** limitations:
- "We index up to 250 characters of data for full-text search"
- Minimum token length: 2 characters
- Common stop words excluded from indexing

**Targeted Search**: Use Input or Output filters for field-specific matching.

### By Key-Value Pairs (Structured Data)

- LangSmith indexes up to **100 unique keys per run**
- Each key limited to **250 characters** per value
- Use dot notation for nested paths (e.g., `documents.page_content`)
- Example nested search: `generations.message.kwargs.tool_calls.name = Plan`

## Advanced Filtering

### Negative Filtering

Apply exclusion logic to Metadata, Input, and Output fields:
- Key operator set to `is not` excludes specific keys
- Value operator set to `is not` excludes specific values

### Root Property Filtering

Filter runs within traces whose root run has specific attributes (e.g., feedback scores).

### Child Run Filtering

Search for runs containing specific sub-run types using Tree filters in Advanced settings.

## Saving and Managing Filters

- Create saved filters via "Save as" after constructing criteria.
- Saved filters appear in the view dropdown for reuse within that tracing project.
- Delete saved filters via ellipsis menu next to filter name.

## Programmatic Access (SDK)

```python
from langsmith import Client

client = Client()

# List runs with filters
runs = client.list_runs(
    project_name="my-project",
    filter='and(eq(is_root, true))',  # Only root runs (traces)
)

# Filter by tag
runs = client.list_runs(
    project_name="my-project",
    filter='has(tags, "my-tag")',
)

# Filter by metadata
runs = client.list_runs(
    project_name="my-project",
    filter='eq(metadata_key("user_id"), "user_123")',
)
```

## LangSmith Query Language Syntax

Complex filters use LangSmith's query language:

```
and(eq(is_root, true), and(eq(feedback_key, "user_score"), eq(feedback_score, 1)))
```

Reference the Trace query syntax documentation for the complete language specification.

## Trace View Filtering (Within a Single Trace)

When viewing an individual trace, apply filters with view options:
- **Filtered Only**: Show matching runs exclusively
- **Show All**: Display all runs with matches highlighted
- **Most relevant**: Contextual matching display
