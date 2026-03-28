---
source_id: "012"
title: "Dify v0.8.0: Accelerating Workflow Processing with Parallel Branch"
url: "https://dify.ai/blog/accelerating-workflow-processing-with-parallel-branch"
type: "blog"
scraped_at: "2026-03-27"
keywords: ["Dify workflow engine", "Dify workflow nodes", "Dify workflow"]
content_length: 4215
---

# Dify v0.8.0: Accelerating Workflow Processing with Parallel Branch

Published: Sep 10, 2024

Dify Workflow is widely used for its user-friendly setup and powerful functionality. However, previous versions executed steps serially, waiting for each node to complete before moving to the next. While providing a clear structure, this slowed processing for complex tasks, increasing latency and response times.

Dify v0.8.0 addresses these limitations by introducing parallel processing capabilities. Workflow can now execute multiple branches concurrently, enabling simultaneous processing of different tasks. This significantly improves execution efficiency, allowing LLM applications to handle complex workloads faster and with greater flexibility.

## Creating parallel branches

To define parallel branches in a Workflow:

1. Hover over a node
2. Click the + icon that appears
3. Add different node types

The branches will execute in parallel and combine their outputs.

## Simple parallelism

For basic scenarios, create multiple parallel branches from a fixed node (e.g., the start node). This setup handles similar subtasks concurrently, such as translations or model comparisons.

## Nested parallelism

Nested parallelism allows for multi-level parallel structures within a Workflow. From an initial node, it branches into multiple parallel paths, each containing its own parallel processes. The "Science Writing Assistant" example shows two nesting levels:

1. First level: From the question classifier, two main branches emerge:
   a. Concept explanation
   b. Handling off-topic conversations ("Refuse small talk" branch)

   The concept explanation branch includes:
   - Metaphors and analogies branch for enhanced concept understanding
   - Theme extraction with second level nesting for detailed concept analysis and content generation

2. Second level: The theme extraction branch performs two parallel tasks:
   a. Extract theme and search for background information
   b. Extract theme and generate study plan

This multi-level nested parallel structure is ideal for complex, multi-stage tasks like in-depth concept analysis and science communication content creation. It processes different concept aspects concurrently, including basic explanations, analogies, background research, and learning plans, improving processing efficiency and output quality.

## Iterative Parallelism

Iteration parallelism involves parallel processing within a loop structure. The "Stock News Sentiment Analysis" example demonstrates this approach:

1. Setup: Search and extract multiple news URLs for a specific stock.
2. Iterative processing: For each URL, execute in parallel:
   a. Content retrieval: Use JinaReader to scrape and parse webpage content.
   b. Opinion extraction: Identify optimistic and pessimistic views using a parameter extractor.
   c. Opinion summarization: Use two independent LLM models to summarize optimistic and pessimistic views concurrently.
3. Combine results: Consolidate all findings into a single table.

This method efficiently processes large volumes of news articles, analyzing sentiment from multiple perspectives. Parallel processing within iterations accelerates tasks with similar data structures, saving time and improving performance.

## Conditional parallelism

Conditional branch parallelism runs different parallel task branches based on conditions. The "Interview Preparation Assistant" example shows this setup:

1. Main condition (IF/ELSE node): Splits process based on dialogue_count:
   a. First dialogue: Confirm interview role and company
   b. Later dialogues: Enter deeper processing

2. Secondary condition (IF/ELSE 2 node): In later dialogues, branches based on existing company info and interview questions:
   a. Missing company info: Run parallel tasks to search company, scrape webpage, summarize company info
   b. Missing interview questions: Generate multiple questions in parallel

3. Parallel task execution: For question generation, multiple LLM nodes start at the same time, each creating a different question

This IF/ELSE structure lets Workflow flexibly run different parallel tasks based on current state and needs. This improves efficiency while keeping things orderly.

## Benefiting from Workflow parallelism

These four parallel methods (simple, nested, iterative, and conditional) boost Dify Workflow's performance. They support multi-model teamwork, simplify difficult tasks, and adjust execution paths dynamically. These upgrades increase efficiency and broaden applications, handling tough work situations better.
