---
source_id: 031
title: "Confluent Platform Overview"
url: "https://docs.confluent.io/platform/current/get-started/platform.html"
type: web
scraped_at: 2026-03-27
keywords: ["kw_034", "kw_003"]
content_length: 8900
---

# Confluent Platform Overview

Confluent Platform is a full-scale streaming platform built by the original creators of Apache Kafka. Enterprise-ready with advanced capabilities for application development and connectivity.

## Kafka Use Cases

Financial services, omnichannel retail, autonomous cars, fraud detection, microservices, IoT. Collects user activity, system logs, application metrics, stock ticker data, device instrumentation signals.

## Platform Features

At core: Apache Kafka (publish/subscribe, fault-tolerant storage, stream processing).

Each release includes latest Kafka plus additional tools:
- **Schema Registry**: Centralized repository for managing/validating schemas. Supports Avro, JSON Schema, Protobuf. Tracks versions, enforces compatibility settings.
- **Cluster Linking**: Directly connect clusters and mirror topics between clusters.
- **REST Proxy**: RESTful HTTP service for interacting with Kafka from any language. Integrates with Schema Registry.
- **Confluent Platform for Apache Flink**: Support for Flink stream processing. Deployed in Kubernetes via Confluent Management Framework (CMF).
- **100+ pre-built Kafka connectors**: Both commercial and community licensed.
- **ksqlDB**: Streaming SQL engine. Interactive SQL interface for stream processing without coding.

## Kafka Capabilities

- **Broker**: Stores data durably, consumed by clients.
- **Security**: SSL/TLS encryption, SASL authentication, ACL authorization.
- **APIs**: Producer, Consumer, Kafka Connect, Streams API, Admin API.

## Development and Connectivity

- Connectors for databases, key-value stores, search indexes, file systems.
- Non-Java clients: C/C++, Python, Go, .NET, JavaScript.
- CLI tools plus Confluent CLI.

## Management and Monitoring

- **Confluent Control Center**: Web-based management and monitoring.
- **Unified Stream Manager (USM)**: Monitor both on-premises and cloud clusters from single console.
- **Health+**: Intelligent alerts, monitoring, proactive support.
- Metrics reporter producing to Kafka topics.

## Performance and Scalability

- **Tiered Storage**: Auto-tier data to object storage. Scale brokers only for compute.
- **Self-Balancing Clusters**: Automated load balancing, failure detection, self-healing. No manual tuning.
- Deployment: Ansible Playbooks, Confluent for Kubernetes.

## Security and Resilience

- **RBAC**: Role-based access control.
- **SSO**: Single Sign On with OIDC providers.
- **Audit logs**: Capture authorization activity.
- **Cluster Linking**: Multi-datacenter, multi-region, hybrid cloud.
- **Confluent Replicator**: Multi-datacenter replication for active geo-localized deployments, centralized analytics, cloud migration.
