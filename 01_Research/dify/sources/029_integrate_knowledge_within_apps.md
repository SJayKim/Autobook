---
source_id: "029"
title: "Integrate Knowledge within Apps - Dify Docs"
url: "https://docs.dify.ai/en/use-dify/knowledge/integrate-knowledge-within-application"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify knowledge base", "Dify metadata filtering"]
content_length: 7650
---

## Creating an Application Integrated with Knowledge Base

A "Knowledge Base" can be used as an external information source to provide precise answers to user questions via LLM. You can associate an existing knowledge base with any application type in Dify. Taking a chat assistant as an example, the process is as follows:

1. Go to Knowledge > Create Knowledge > Upload file
2. Go to Studio > Create Application > Select Chatbot
3. Enter Context, click Add, and select one of the knowledge base created
4. Use Metadata Filtering to refine document search in your knowledge base
5. In Context Settings > Retrieval Setting, configure the Retrieval Setting
6. Enable Citation and Attribution in Add Features
7. In Debug and Preview, input user questions related to the knowledge base for debugging
8. After debugging, click Publish button to make an AI application based on your own knowledge

## Connecting Knowledge and Setting Retrieval Mode

In applications that utilize multiple knowledge bases, it is essential to configure the retrieval mode to enhance the precision of retrieved content.

### Retrieval Setting

The retriever scans all knowledge bases linked to the application for text content relevant to the user's question. The results are then consolidated. This method simultaneously queries all knowledge bases connected in "Context", seeking relevant text chunks across multiple knowledge bases, collecting all content that aligns with the user's question, and ultimately applying the Rerank strategy to identify the most appropriate content to respond to the user.

The multi-path retrieval mode provides two Rerank settings:

**Weighted Score**

This setting uses internal scoring mechanisms and does not require an external Rerank model, thus avoiding any additional processing costs. You can select the most appropriate content matching strategy by adjusting the weight ratio sliders for semantics or keywords.

- **Semantic Value of 1**: Activates semantic retrieval only. By utilizing the Embedding model, the search depth can be enhanced even if the exact words from the query do not appear in the knowledge base, as it calculates vector distances to return the relevant content. Useful for multilingual content and cross-language search.

- **Keyword Value of 1**: Activates keyword retrieval only. It matches the user's input text against the full text of the knowledge base, making it ideal for scenarios where the user knows the exact information or terminology. Resource-efficient for large document repositories.

- **Custom Keyword and Semantic Weights**: Flexible custom Weight Score. You can determine the best weight ratio for your business scenario by continuously adjusting the weights of both.

**Rerank Model**

The Rerank model is an external scoring system that calculates the relevance score between the user's question and each candidate document provided, improving the results of semantic ranking. While this method incurs some additional costs, it is more adept at handling complex knowledge base content, such as content that combines semantic queries and keyword matches, or cases involving multilingual returned content. Dify currently supports multiple Rerank models (Cohere, Jina AI, etc.).

**Adjustable Parameters**:
- **TopK**: Determines how many text chunks, deemed most similar to the user's query, are retrieved. The default value is 3; higher numbers recall more text chunks.
- **Score Threshold**: Sets the minimum similarity score required for a chunk to be retrieved. The default value is 0.5. Higher thresholds demand greater similarity and result in fewer chunks.

## Metadata Filtering

### Chatflow/Workflow

The Knowledge Retrieval node allows you to filter documents using metadata fields.

**Filter Modes**:
- **Disabled (Default)**: No metadata filtering.
- **Automatic**: Filters auto-configure from query variables in the Knowledge Retrieval node. Note: Automatic Mode requires model selection for document retrieval.
- **Manual**: Configure filters manually.

For Manual Mode:
1. Click Conditions to open the configuration panel.
2. Click +Add Condition: Select metadata fields from the dropdown list. When multiple knowledge bases are selected, only common metadata fields are shown.
3. Configure filter conditions based on field type:

| Field Type | Operators |
| --- | --- |
| String | is, is not, is empty, is not empty, contains, not contains, starts with, ends with |
| Number | =, !=, >, <, >=, <=, is empty, is not empty |
| Date | is, before, after, is empty, is not empty |

4. Add filter values using Variable (existing Chatflow/Workflow variables) or Constant (specific values). Time-type fields can only be filtered by constants.
5. Filter values are case-sensitive and require exact matches.
6. Set logic operators: AND (match all conditions) or OR (match any condition).

### Chatbot

Access Metadata Filtering below Knowledge (bottom-left). Configuration steps are the same as in Chatflow/Workflow.

## Frequently Asked Questions

1. **How should I choose Rerank settings?** If users know the exact information, use keyword search (Keywords=1). For cross-lingual queries, use Semantic=1. For complex knowledge bases needing highly accurate answers, use a Rerank Model.

2. **Weight Score unavailable?** Check if knowledge bases use consistent embedding models. If inconsistent, set and enable the Rerank model or unify the retrieval settings.

3. **Can't find Weight Score option?** Check whether your knowledge base is using the "Economical" index mode. If so, switch to "High Quality" index mode.
