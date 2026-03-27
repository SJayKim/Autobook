---
source_id: 045
title: "Deploying LLMs on Kubernetes: vLLM, Ray Serve & GPU Scheduling Guide (2026)"
url: "https://blog.premai.io/deploying-llms-on-kubernetes-vllm-ray-serve-gpu-scheduling-guide-2026/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_004", "kw_030", "kw_019", "kw_036"]
content_length: 18500
---

# Deploying LLMs on Kubernetes: vLLM, Ray Serve & GPU Scheduling Guide (2026)

This guide covers the full stack: vLLM and Ray Serve deployment, GPU scheduling with MIG and topology awareness, autoscaling on queue depth and KV cache utilization, Prometheus/Grafana monitoring, and production patterns like canary rollouts and graceful shutdown. Configurations verified against vLLM v0.17.0 and Ray 2.54.0.

## Why Kubernetes for LLM Inference

The NVIDIA GPU Operator (v25.10.1) gives automatic GPU discovery, MIG partitioning, and time-slicing from a single Helm install. GPU Feature Discovery auto-labels nodes with hardware metadata (model, memory, CUDA version).

Kubernetes HPA with custom metrics lets you scale on inference-specific signals like queue depth and KV cache utilization instead of CPU. The Gateway API Inference Extension (GA as of February 2026, v1.3.1) adds model-aware routing, KV-cache-aware scheduling, and traffic splitting by model name for A/B testing.

## Choosing Your Serving Engine

| Feature | vLLM (standalone) | Ray Serve + vLLM | llm-d |
|---------|-------------------|------------------|-------|
| Best for | Single-node, single-model | Multi-node, multi-model | Disaggregated serving at scale |
| Multi-node inference | Manual setup | Automatic placement groups | Native with NIXL KV transfer |
| Autoscaling | External (HPA/KEDA) | Built-in (replica + cluster + infra) | Workload-variant autoscaler |
| K8s integration | Raw manifests or Helm | KubeRay operator (RayService CRD) | Helm + K8s Inference Gateway |

If your model fits on one node's GPUs, start with standalone vLLM. When you need multi-node inference or want to serve multiple models from one cluster, move to Ray Serve. For disaggregated prefill/decode at massive scale, consider llm-d (~3.1k tokens/sec per B200 decode GPU).

Higher-level operators: vLLM Production Stack (2.2k stars), AIBrix (4.7k stars), KubeAI (1.2k stars).

## GPU Scheduling for LLM Workloads

### NVIDIA GPU Stack Setup

Install GPU Operator via Helm. Deploys device plugin (exposes nvidia.com/gpu resources), GPU Feature Discovery (auto-labels nodes), and DCGM Exporter (GPU metrics for Prometheus).

### Node Affinity and Taints

Isolate GPU nodes from non-GPU workloads with taints. Add tolerations to LLM pods. For multi-GPU-type clusters, use node affinity with GPU Feature Discovery labels.

### GPU Sharing: MIG and Time-Slicing

**MIG:** Partitions A100/H100 GPUs into hardware-isolated instances with dedicated memory and compute. A single A100 80GB can run up to seven 1g.10gb instances.

**Time-slicing:** Shares a GPU across multiple workloads without hardware isolation. Use MIG for production multi-tenant workloads; time-slicing for development/testing.

### Topology-Aware Scheduling

Configure Topology Manager (kubelet) to keep GPU and CPU on the same NUMA node. For multi-GPU tensor parallelism, Volcano (v1.12.0) provides gang scheduling.

## Deploying vLLM on Kubernetes

Key production considerations:
1. **Shared memory volume:** emptyDir with medium: Memory at /dev/shm required for tensor parallel inference
2. **terminationGracePeriodSeconds: 300** -- default 30 seconds kills in-flight inference requests
3. **initialDelaySeconds: 120** -- 7B model takes 30-60 seconds to load into GPU memory

### vLLM Helm Chart

```
helm install vllm oci://ghcr.io/vllm-project/vllm-chart \
  --set model=mistralai/Mistral-7B-Instruct-v0.3 \
  --set gpu=1 --namespace llm-inference --create-namespace
```

vLLM Production Stack (v0.1.10) adds KV-cache-aware request router and bundled Prometheus/Grafana.

## Deploying with Ray Serve on Kubernetes

Install KubeRay. Provides three CRDs: RayCluster, RayJob, RayService. Ray Serve autoscaling works at three levels simultaneously: application autoscaler (model replicas), Ray Autoscaler (worker pods), Kubernetes Cluster Autoscaler (GPU nodes).

Multi-model serving: Pass multiple LLMConfig objects. Each model gets independent autoscaling. Clients select via the model field in the request body (OpenAI API compatible).

## Autoscaling LLM Inference on Kubernetes

### Why CPU and Memory Metrics Don't Work

Standard HPA scales on CPU utilization, but LLM inference is GPU-bound. CPU can sit at 5% while inference queue backs up with 50 waiting requests. GPU utilization is a duty cycle measurement and won't differentiate between processing 10 or 100 requests. GPU memory is pre-allocated by vLLM for KV cache and stays constant.

### Scale on queue depth and batch size

| Metric | vLLM Prometheus Name | Best For | Starting Threshold |
|--------|---------------------|----------|-------------------|
| Queue depth | vllm:num_requests_waiting | Maximizing throughput | 3-5 requests |
| Batch size | vllm:num_requests_running | Latency-sensitive | Below max batch |
| KV cache util | vllm:gpu_cache_usage_perc | Memory pressure | 0.85 (85%) |
| TTFT p99 | vllm:time_to_first_token_seconds | User experience SLOs | App-specific |

### Scale-to-Zero with KEDA

Standard HPA can't scale to zero. KEDA (v2.19) adds this. Tradeoff: cold start time (30-60 seconds for 7B model with cached weights).

### GPU Node Autoscaling with Karpenter

Karpenter provisions GPU nodes automatically. consolidationPolicy: WhenEmptyOrUnderutilized bin-packs GPU workloads. Including both on-demand and spot lets Karpenter fall back to on-demand when spot GPU instances are unavailable.

## Monitoring LLM Inference with Prometheus and Grafana

Essential PromQL queries:
- Time to First Token (P95): histogram_quantile(0.95, rate(vllm:time_to_first_token_seconds_bucket[5m]))
- Generation Tokens Per Second: rate(vllm:generation_tokens_total[1m])
- KV Cache Utilization: vllm:gpu_cache_usage_perc
- Request Queue Depth: vllm:num_requests_waiting

Alert rules for production: HighKVCacheUsage (>90%, 5m), HighQueueDepth (>10, 2m), HighTTFT (p99 >5s, 5m).

## Production Patterns

### Graceful Shutdown

Increase terminationGracePeriodSeconds (300+) and add preStop hook. For streaming workloads, 600+ seconds is more appropriate.

### Canary Deployments for Model Updates

Use Argo Rollouts (v1.8.4) or Gateway API Inference Extension for traffic splitting by model name. Route 10% to new model version, watch quality metrics, promote incrementally.

### Security Hardening

Apply Baseline Pod Security Standard. Use External Secrets Operator (v2.1.0) for secret management. Create NetworkPolicies restricting traffic to inference namespace.

## Common Pitfalls

- OOMKilled: Missing shared memory volume or model too large for GPU VRAM
- Slow cold starts: Model download takes 5-10 min (7B) or 20+ min (70B); use PVC caching
- CUDA version mismatch: Use official vllm/vllm-openai Docker image
- Pods stuck Pending: NVIDIA device plugin DaemonSet not running
- Autoscaling not working: Scaling on CPU instead of queue depth

## FAQ Highlights

- 70B model needs ~140GB VRAM in FP16; ~35GB with INT4 quantization
- Multiple models on same GPU: Use MIG (hardware isolation) or time-slicing (no isolation)
- Cold start times: 30-60s for 7B (cached), 2-5 min for 70B
- Kubernetes version: 1.26+ for stable GPU scheduling; 1.31+ for Image Volume
