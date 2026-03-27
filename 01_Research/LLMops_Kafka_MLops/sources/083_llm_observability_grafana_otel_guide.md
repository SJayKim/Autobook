---
source_id: 083
title: "A Complete Guide to LLM Observability with OpenTelemetry and Grafana Cloud"
url: "https://grafana.com/blog/a-complete-guide-to-llm-observability-with-opentelemetry-and-grafana-cloud/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_028", "kw_006"]
content_length: 9200
---

# A Complete Guide to LLM Observability with OpenTelemetry and Grafana Cloud

By Ishan Jain, Kamel Djoudi | 2024-07-19

In the fast-paced world of technology, change is constant -- and nowhere is that more evident today than in the flood of new features and advancements involving large language models (LLMs). They power various applications, from chat bots to advanced copilots. And as these LLMs and applications become more sophisticated, it will be vital that they work well and reliably. This is where observability, with the help of OpenTelemetry (using OpenLIT), plays an essential role.

## How does an LLM application work?

Imagine an application like ChatGPT, which is a chatbot powered by an LLM (e.g., GPT-3.5). When you ask ChatGPT a question, it processes your input and responds accordingly.

Here's a simplified breakdown of what's happening behind the scenes:

- **User input**: The user types a prompt or question.
- **Processing**: The backend application (typically written in Python) sends this request to the language model.
- **Response**: The model processes the input and sends back a response.
- **Display**: The response is displayed to the user in the chat interface.

## Why observability matters for LLM applications

Observability helps you understand what's happening inside your LLM application. Here are some crucial questions it can help answer:

1. How often are requests made to the LLM provider (e.g., OpenAI)? -- Tracking request frequency helps manage usage and avoid unexpected costs.
2. How long does it take to get a response? -- Monitoring response times ensures the application runs efficiently and helps identify any latency issues.
3. Will the requests to the LLM provider cause rate-limiting issues? -- Observing request rates can prevent disruptions caused by exceeding rate limits.
4. Is the support bot providing helpful and accurate responses? -- Evaluating response quality helps improve user satisfaction and identifies model performance issues.
5. How much does it cost to run the LLM feature in production? -- Tracking costs aids in budget management and decision-making for scaling the application.
6. When did the LLM start giving irrelevant or incorrect responses (hallucinations)? -- Detecting anomalies early allows you to address issues promptly.
7. What are users asking the support bot? -- Analyzing user queries helps understand user needs and enhance the bot's responses.

## Why OpenTelemetry (and Grafana Cloud) is the right choice

OpenTelemetry is an open source framework for observability. It collects and exports monitoring data in a vendor-neutral way, setting standards for data collection and processing. It's particularly well-suited for LLM applications because it works with many monitoring tools, like Grafana Cloud.

For LLM applications, tracking the sequence of operations (traces) is critical. This is especially true when using orchestration frameworks like LangChain or LlamaIndex. Tracing helps understand the workflow, making debugging and root cause analysis more straightforward and effective.

Grafana Cloud is also built on an open source framework, and it includes a large ecosystem of data sources and integrations -- including OpenTelemetry -- you can use to unify and correlate disparate LLM data.

## What to track: key signals to monitor

LLMs are different from traditional machine learning models, often accessed through external API calls. Capturing the sequence of events through traces is crucial, especially in a RAG-based application where events can occur before and after the use of LLMs.

### Traces

#### Request metadata
- **Temperature**: Measures how creative or random the output should be
- **Top_p**: Controls how selective the model is with its output choices
- **Model name or version**: Tracks performance changes with updates
- **Prompt details**: The inputs sent to the LLM, which can vary widely

#### Response metadata
- **Tokens**: Impacts cost and measures response length
- **Cost**: Important for budgeting and managing expenses
- **Response details**: Characteristics of model outputs and potential inefficiencies

### Metrics
- **Request volume**: Total number of requests to understand usage patterns.
- **Request duration**: Time taken to process each request, including network latency and response generation time.
- **Costs and tokens counters**: Tracking costs and tokens over time for budgeting and cost optimization.

### Why this isn't just plain API monitoring

While LLM observability does involve monitoring external API calls to LLMs, it goes much further than traditional API monitoring. In standard API monitoring, the focus is primarily on request and error tracking. However, LLM observability captures detailed and valuable information, such as prompts, responses, associated costs, and token usage.

This rich data set offers a more comprehensive view of the application's performance, giving you deeper insights into areas like prompt evaluation, model performance, and more.

## Tutorial: Automatic instrumentation for LLMs applications with OpenLIT

OpenLIT offers a simple path to automated instrumentation. With the OpenLIT SDK, developers can capture essential telemetry data automatically.

**1. Install OpenLIT SDK:**

```
pip install openlit
```

**2. Get your Grafana Cloud credentials:**

1. Log in to Grafana Cloud and select your Grafana Cloud Stack.
2. Click on the OpenTelemetry card
3. Under the "Password / API Token" section, click Generate an API token.
4. Enter a name for the token and click Create.
5. Copy and save the values for `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_HEADERS`.

**3. Set the OTEL endpoint and headers as ENV:**

```
export OTEL_EXPORTER_OTLP_ENDPOINT="YOUR_GRAFANA_OTEL_GATEWAY_URL"
export OTEL_EXPORTER_OTLP_HEADERS="YOUR_GRAFANA_OTEL_GATEWAY_AUTH"
```

**4. Initialize the SDK:**

```python
import openlit
openlit.init()
```

You can also customize the application name and environment:

```python
openlit.init(application_name="YourAppName", environment="Production")
```

## Visualize time series using a Grafana dashboard

Once your LLM application is instrumented with OpenTelemetry, the next step is to visualize and analyze the data. The OpenLIT dashboard can be imported to quickly get started.

### Breakdown of panels and their benefits

The OpenLIT dashboard offers a comprehensive view of your application's performance, helping you enhance efficiency, manage costs, and ensure the reliability of your LLM application.

For example, it tracks successful requests, providing insights into usage patterns and potential issues while detailing request durations to identify latency problems and optimization opportunities in external LLM API calls. By monitoring request rates, you can avoid exceeding the limits set by LLM providers.

Cost management is also streamlined with total and average usage cost insights, aiding in budget planning and evaluating cost-effectiveness. The dashboard also identifies the most frequently used GenAI models, enabling you to prioritize resources and assess model performance. Detailed segmentation by platform, request type, and environment ensures a granular understanding of usage.
