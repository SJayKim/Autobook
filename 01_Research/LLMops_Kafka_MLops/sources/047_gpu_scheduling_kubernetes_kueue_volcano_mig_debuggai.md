---
source_id: 047
title: "Kubernetes GPU Scheduling in 2025: Practical Patterns for AI Workloads with Kueue, Volcano, and MIG"
url: "https://debugg.ai/resources/kubernetes-gpu-scheduling-2025-kueue-volcano-mig"
type: web
scraped_at: 2026-03-27
keywords: ["kw_030", "kw_004"]
content_length: 19500
---

# Kubernetes GPU Scheduling in 2025: Practical Patterns for AI Workloads with Kueue, Volcano, and MIG

AI infrastructure is GPU-bound, not pod-bound. In 2025, the clusters that ship models to production are those that schedule GPUs as a first-class resource across multi-tenant, bursty, heterogeneous fleets. This article covers how to combine device plugins, gang scheduling, queues and preemption, MIG/MPS partitioning, bin-packing, spot fallback, and orchestration via Kueue, Volcano, and Ray.

## Executive summary

- **Kueue:** Cluster-wide queues, quotas, cohort borrowing, and preemption that fit enterprise multi-tenant AI. Combined with the default scheduler and NVIDIA device plugin.
- **Volcano:** Most mature gang scheduler with rich batch plugins (PodGroup, priorities, preemption, rescheduling). Shines for HPC-like AI training.
- **MIG:** Turns a single GPU into multiple hardware-sliced instances with dedicated memory, cache, and compute. Use for packing small training and inference safely.
- **MPS:** Time-slices compute to boost throughput when latency and isolation constraints allow.

## Why GPU-bound beats pod-bound

Kubernetes has a pod-centric scheduler. AI workloads care about count, type, and topology of GPUs. You need to:
- Admit or reject entire jobs atomically (gang semantics)
- Enforce tenant-level quotas across clusters
- Shape GPU instances (full, MIG, or MPS) to match workload footprints
- Preempt cleanly and fairly
- Avoid GPU fragmentation

## NVIDIA GPU Operator and Device Plugin

The GPU Operator installs driver, nvidia-container-toolkit, DCGM, and device plugin. Supports MIG strategies:
- **none:** Expose full GPUs only
- **single:** Nodes run single MIG layout; stable and recommended for shared clusters
- **mixed:** Multiple MIG layouts per node; flexible but can increase fragmentation

Time-slicing: Enable for inference/experimentation. Combine with MPS to reduce context-switch overhead.

## Gang semantics: Kueue vs. Volcano

### Kueue: queue-based admission for batch

Workloads enqueued into LocalQueues bound to ClusterQueues with quotas by ResourceGroup and Flavors (e.g., A100 vs H100). Kueue simulates scheduling and either admits the entire workload (gang) or keeps it pending. Cohorts allow queues to borrow idle quota from peers.

Pros: Works with native controllers; strong multi-tenant controls; natural extension for batch autoscaling and preemption.

### Volcano: battle-tested batch scheduler

PodGroup CRD gives gang semantics; all pods scheduled once minAvailable satisfied. Rich preemption, rescheduling, and queue priorities. Integrations with MPI, TensorFlow, PyTorch operators.

### Choosing Kueue vs. Volcano

- Start with Kueue for enterprise multi-tenant controls without replacing kube-scheduler
- Choose Volcano for HPC-like batch training with strict gang semantics
- Combine for advanced patterns: Kueue for queueing/quota, Volcano for scheduling

## MIG and MPS: partitioning GPUs

### MIG profiles

A100 80GB: 1g.10gb, 2g.20gb, 3g.40gb, 7g.80gb. Keep a subset of nodes MIG-disabled for large training. Choose 2-3 layouts per GPU family and stick to them. Switching MIG layouts requires cordoning and draining nodes.

### MPS and time-slicing

MPS allows multiple CUDA contexts to share a GPU with improved concurrency. Boosts throughput for latency-tolerant inference, hyperparameter sweeps, lightweight fine-tuning/LoRA. Trade-offs: interference between jobs, fuzzier per-job utilization accounting.

Opinion: prefer MIG for SLO-bound inference. Use MPS/time-slicing when objective is raw throughput and jobs are resilient to interference.

## GPU bin-packing: minimize fragmentation

- Separate node pools by GPU family and MIG policy; expose as distinct Flavors
- Score nodes with bin-packing bias (NodeResourcesFit with MostAllocated) for full GPU jobs
- For MIG nodes, choose small set of layouts correlating with request patterns
- Prefer packing within NVSwitch domains over spreading across racks

KubeSchedulerConfiguration example with MostAllocated scoring:
- nvidia.com/gpu weight: 10, cpu weight: 1, memory weight: 1

## Spot fallback: cheaper GPUs without chaos

Spot instances cut costs 50-80% but demand resilience:
- Isolate spot nodes with taints
- Use PriorityClasses (spot jobs preempted first)
- Configure Cluster Autoscaler or Karpenter with separate provisioners
- Checkpoint frequently (every few minutes) to object storage
- PreStop hooks to save progress on SIGTERM

## Orchestrating with Ray

RayCluster CRD for long-lived clusters; per-job ephemeral clusters for batch. Use Kueue admission for RayJobs (entire cluster admitted as gang). Define per-group Pod templates requesting GPUs (full or MIG) pinned to flavors.

## Reference architecture

Node pools: pool-h100-full (MIG disabled, large training), pool-h100-mig (7x 1g.10gb, inference), pool-a100-mig (backfill), pool-gpu-spot (low priority).

ClusterQueues: prod (highest priority, can borrow), research (capped, can borrow from batch), batch (lowest, uses spot).

WorkloadPriorityClasses: critical (1000, preempt lower), batch (100, never preempt).

## Observability and SLOs

KPIs: GPU utilization (target 65-85% average), queue wait time (p95 under SLO), preemption rate (<5-10%), fragmentation metrics.

Tools: DCGM Exporter, Prometheus, Kueue metrics (admitted vs pending), Volcano metrics (queue lengths, PodGroup states).

## Common pitfalls

- Too many MIG layouts: operational thrash and stranded capacity
- MPS pretending to be isolation: it is not
- Ignoring CPU and memory: oversubscribed CPUs can throttle GPUs
- No gang semantics for Ray: partial startup frequently deadlocks actor sets
- Preemption without checkpoints: wasted GPU hours
- Spreading training pods across racks without reason: network bottleneck
