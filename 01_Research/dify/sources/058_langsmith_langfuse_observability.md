---
source_id: "058"
title: "Enhance LLM Application observability on Dify with LangSmith and Langfuse"
url: "https://dify.ai/blog/dify-integrates-langsmith-langfuse"
type: "blog"
scraped_at: "2026-03-27"
keywords: ["Dify observability", "Dify LangSmith integration", "Dify Langfuse integration"]
content_length: 4120
---

# Enhance LLM Application observability on Dify with LangSmith and Langfuse

In our ongoing effort to foster a more open and robust LLM ecosystem, Dify version 0.6.12 has integrated LangSmith and Langfuse, two powerful LLM application observability tools. With simple configuration, you can now access detailed application data, making it easier to evaluate the cost, latency, and quality of LLM applications created on Dify.

## What is LLMOps?

While LLMs exhibit remarkable inference and text generation capabilities, their internal workings remain a black box, presenting challenges in LLM-based application development. LLM applications created with Dify Workflow often involve multiple nodes and high complexity, making operational monitoring crucial - see what's happening with your application, so you can take action when needed.

In our latest integration, Dify leverages LangSmith and Langfuse to provide comprehensive LLMOps support, including:

1. **Selecting suitable models:** Dify supports mainstream LLMs, allowing you to choose the most appropriate model for your specific needs.

2. **Creating effective prompts:** Dify offers an intuitive prompt editing interface, which, combined with LangSmith and Langfuse, enables detailed tracking and analysis of prompt effectiveness.

3. **Monitoring performance:** Through LangSmith and Langfuse, you can comprehensively monitor LLM applications created on Dify, tracking accuracy, latency, and resource utilization.

4. **Continuous improvement:** LangSmith and Langfuse offer detailed monitoring metrics. These metrics, combined with manual annotation of LLM responses, allow you to continuously optimize your applications and enhance user experience.

5. **Cost optimization:** Dify provides basic resource usage statistics, while LangSmith and Langfuse complement this with detailed cost and token usage analysis, helping you optimize resource allocation efficiently.

## Why LangSmith and Langfuse?

LangSmith and Langfuse are two advanced LLM application performance monitoring tools that offer comprehensive support for Dify users in developing and optimizing LLM applications.

**LangSmith**, developed by the LangChain team, provides extensive tracing capabilities and in-depth evaluations, helping teams monitor LLM complex applications as they scale. LangSmith provides rich evaluation features that can be run directly from prompts, including:
- Pairwise and regression testing
- LLM-as-a-judge (i.e. using an LLM to score outputs) for fine-tuning, including off-the-shelf RAG evaluators
- Custom evaluators for tasks like code generation

**Langfuse**, as an open-source platform, offers low performance overhead and excellent support for complex use cases. Key features include:
- Open-source and self-hostable architecture with easy deployment
- Fully-featured API and data exports that allow to build downstream use cases
- Framework agnostic tracing and analytics
- Automated evaluation, custom eval pipelines, and human annotation workflows
- Datasets for benchmarking different experiments, collecting few-shot examples, and fine-tuning

Notably, Langfuse is open source (MIT-licensed) and supports self-hosting through a containerized deployment. It can be deployed freely and through a single container which makes it attractive for users that have security requirements or simply prefer to run on their own infrastructure.

## How do they work with Dify?

Using LangSmith and Langfuse in Dify is straightforward. After creating an application, you can enable these tools with just one-click configuration on the overview page.

Once configured, usage data from your Dify-created applications will be automatically transmitted to these platforms. In the project management interfaces of LangSmith and Langfuse, you can view detailed performance metrics, cost data, and usage information to optimize your applications on Dify.

## Looking Ahead

With the integration of LangSmith and Langfuse, Dify 0.6.12 sets a new standard for transparent and efficient LLM application development. The mission is to continually push the boundaries of what's possible in LLMOps, empowering developers to harness the full potential of LLM.
