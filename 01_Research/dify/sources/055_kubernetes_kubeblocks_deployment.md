---
source_id: "055"
title: "Deploy Production-Ready AIGC Applications on Kubernetes using KubeBlocks and Dify"
url: "https://kubeblocks.io/blog/dify-on-kb"
type: "tutorial"
scraped_at: "2026-03-27"
keywords: ["Dify Kubernetes deployment", "Dify K8s production", "Dify self-hosting"]
content_length: 8950
---

# Deploy Production-Ready AIGC Applications on Kubernetes using KubeBlocks and Dify

## Introduction

Dify is an open-source large language model (LLM) application development platform that integrates Backend as Service and LLMOps concepts. It provides a range of LLMs, prompt design tools, an agent framework, and flexible process orchestration capabilities.

AIGC applications typically use various databases:
- **PostgreSQL**: Relational database for application metadata
- **Redis**: In-memory database for conversation history
- **Qdrant** (or other vector DB): Vector database for RAG recall

KubeBlocks is a data infrastructure management platform based on Kubernetes that provides a complete solution to help automate the management and scheduling of data infrastructure. It supports multi-cloud environments, offering one-click deployment, seamless scaling, and automatic fault recovery.

## Requirements

- Kubernetes cluster, version >= 1.21
- Kubernetes cluster with an Ingress Controller installed

## Deployment Steps

### Install KubeBlocks

1. Install the latest version of kbcli (KubeBlocks CLI):

```bash
curl -fsSL https://kubeblocks.io/installer/install_cli.sh
```

2. Install the latest version of KubeBlocks:

```bash
kbcli kubeblocks install
```

3. Enable the Qdrant addon (not enabled by default):

```bash
kbcli addon enable qdrant
```

### Create a PostgreSQL Cluster for Metadata

Create a PostgreSQL Replication cluster with two replicas, each provisioned with 1C2G and 20 GiB of storage:

```bash
kbcli cluster create postgresql postgresql --cpu=1 --memory=2 --storage=20 --mode=replication --version=postgresql-14.8.0
# or kubectl
kubectl apply -f https://kubeblocks.io/yamls/dify/postgresql.yaml
```

### Create a Qdrant Cluster for Vectors

Create a Qdrant cluster with three replicas, each provisioned with 1C2G and 20 GiB of storage:

```bash
kbcli cluster create qdrant --cluster-definition=qdrant --cluster-version=qdrant-1.8.4 --set cpu=1,memory=2Gi,storage=20Gi,replicas=3
```

### Create a Redis Cluster for Storage

Create a high-availability Redis cluster with Redis (2 replicas: 1 primary + 1 replica, 2C/1G/20Gi) and Sentinel (3 replicas: 0.2C/0.2G/20Gi):

```bash
kbcli cluster create redis redis --version=redis-7.0.6 --mode=replication --cpu=2 --memory=1 --storage=20 --replicas=2 --sentinel.cpu=0.2 --sentinel.memory=0.2 --sentinel.replicas=3 --sentinel.storage=20
```

### Deploy Dify on Kubernetes

Before deploying Dify, wait for PostgreSQL, Redis, and Qdrant clusters to all be "Running".

1. Initialize Dify metadata by connecting to PostgreSQL and creating the `dify` database.
2. Get the Redis password from the Kubernetes secret.
3. Add the Helm repository:

```bash
helm repo add douban https://douban.github.io/charts/
```

4. Configure values.yaml with database connection info:

Key configuration points in values.yaml:
- `global.host`: Domain name for accessing Dify
- PostgreSQL credentials via Kubernetes secrets (auto-referenced)
- Redis connection with actual password
- `VECTOR_STORE: "qdrant"` with Qdrant URL
- `SECRET_KEY`: Generate with `openssl rand -base64 42`
- `ingress.className`: Match actual ingress class
- `MIGRATION_ENABLED: "true"` for API component

5. Deploy with Helm:

```bash
helm upgrade -i dify douban/dify -f values.yaml
```

6. Verify all pods are Running:

```bash
kubectl get pods -l app.kubernetes.io/name=dify
```

Expected pods: dify-worker, dify-sandbox, dify-frontend, dify-api

### Access Dify

Confirm the Ingress address, configure DNS/static resolution if needed, then access `http://mydify.example.com`.

## Infrastructure Operations with KubeBlocks

### Vertical Scaling

```bash
kbcli cluster vscale qdrant --components qdrant --cpu 8 --memory 32Gi
```

### Horizontal Scaling

```bash
kbcli cluster hscale qdrant --replicas 5
```

### Volume Expansion

```bash
kbcli cluster volume-expand postgresql --components postgresql --storage=50Gi --volume-claim-templates=data
```

### Restart

```bash
kbcli cluster restart postgresql
```

## Summary

The combination of KubeBlocks for data infrastructure management and Dify for AIGC application development significantly improves efficiency with a highly flexible architecture that offers strong scalability and reduces operational complexity in production environments.
