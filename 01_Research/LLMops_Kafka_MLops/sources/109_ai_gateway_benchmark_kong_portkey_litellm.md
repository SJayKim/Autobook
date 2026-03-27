---
source_id: 109
title: "AI Gateway Benchmark: Kong AI Gateway, Portkey, and LiteLLM"
url: "https://konghq.com/blog/engineering/ai-gateway-benchmark-kong-ai-gateway-portkey-litellm"
type: web
scraped_at: 2026-03-27
keywords: ["kw_043"]
content_length: 7500
---

# AI Gateway Benchmark: Kong AI Gateway, Portkey, and LiteLLM

In February 2024, Kong became the first API platform to launch a dedicated AI gateway, designed to bring production-grade performance, observability, and policy enforcement to GenAI workloads.

Kong's AI Gateway provides a universal API to enable platform teams to centrally secure and govern traffic to LLMs, AI agents, and MCP servers. Teams can keep AI costs in check with token rate limiting per consumer, caching responses to redundant prompts, and automatically routing requests to the best model for the prompt.

## From playground to production

Experimenting with AI is easy, but safely and efficiently rolling out AI projects into production is a far greater challenge. Many new AI gateways can handle basic GenAI use cases, but most have never been tested under demanding, high-throughput enterprise conditions.

Kong AI Gateway is built on the same highly performant runtime - Kong Gateway - that already supports mission-critical APIs across the world's largest organizations.

## Benchmark Architecture

Tests executed in AWS on Amazon EKS cluster 1.32. A mocked LLM with WireMock exposed OpenAI-based endpoints to remove native LLM infrastructure variables. AI Gateways exposed through Network Load Balancer (NLB). Gateways and WireMock ran in own EKS Nodes based on c5.4xlarge (16 vCPUs, 32GiB memory). K6 as load generator on EC2 in same VPC.

Versions tested: Kong Gateway 3.10, Portkey OSS 1.9.19, LiteLLM 1.63.7.

### Baseline (WireMock)
- 29005.51 RPS
- P95: 24.07ms
- P99: 30.35ms

### Configuration
All gateways allocated 12 CPUs maximum. Configured as proxy only (no policies like caching or authentication). K6 ran 3 minutes with 400 VUs sending requests with 1000 prompt tokens.

## Results

### Requests Per Second
Kong Konnect Data Planes showed a performance increase of over 200% compared to Portkey, and over 800% against LiteLLM.

### Latency (p95 and p99)
Kong had 65% lower latency compared to Portkey and 86% lower latency than LiteLLM.

### Resource Consumption
Kong was not just able to consume the hardware resources provided, but was also capable of stressing the LLM layer (WireMock). The same behaviour was not observed with LiteLLM or Portkey. All gateways showed 70-80% CPU usage at the 12 CPU allocation.

## Conclusion

With all AI Gateways allocating the same 12 CPUs, Kong Konnect Data Planes were over 228% faster than Portkey and 859% faster than LiteLLM. At the same time, Kong had 65% lower latency compared to Portkey and 86% lower latency than LiteLLM.

This was a basic comparison where AI Gateway played the proxy role only, with no policies defined for Rate Limiting or Authentication.

Kong unifies API and AI management in a single platform, giving platform teams control, visibility, and automation to scale AI-driven workloads. With 100+ enterprise-grade capabilities, teams can apply authentication, token quotas, and observability to LLM traffic. Architectural flexibility enables fully self-hosted, hybrid, dedicated cloud, or serverless gateway deployments across monolithic, microservices, Kubernetes, or multi-cloud environments.
