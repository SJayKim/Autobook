---
source_id: 027
title: "Kafka topic partitioning: Strategies and best practices"
url: "https://newrelic.com/blog/observability/effective-strategies-kafka-topic-partitioning"
type: web
scraped_at: 2026-03-27
keywords: ["kw_048", "kw_003"]
content_length: 8600
---

# Kafka topic partitioning: Strategies and best practices

By Amy Boyle, New Relic Events Pipeline team.

## What Are Kafka Topics and Partitions?

Topics are data categories to which records are published. For scalability, topics are divided into partitions allowing parallel data processing and fault tolerance. Partitions enable multiple consumers to read concurrently and are replicated across nodes.

A partition is the storage unit that allows a topic log to be separated into multiple logs and distributed over the cluster.

## Why Partition Your Data?

If you have so much load that you need more than a single instance, you need to partition. How you partition serves as load balancing for downstream applications. Producer clients decide which partition, but what consumers do with data drives the decision.

## Partitioning Strategies

### Random Partitioning
Evenest spread of load for consumers. Best for stateless or "embarrassingly parallel" services. Default partitioner (from Kafka 2.4) uses "sticky" algorithm grouping messages to same random partition per batch.

### Partition by Aggregate (Key-Based)
Partition by query/entity identifier when consumers need to aggregate by attribute or require ordering guarantee. All events for same key on same partition.

**Hot spots warning**: New Relic found top 1.5% of queries accounted for ~90% of events, causing bad hot spots. Solution: break aggregation into two stages (partial aggregate randomly, then aggregate by key), condensing larger streams at first stage.

### Ordering Guarantee
Partition final results by identifier when clients expect windows provided in order.

### Resource Bottleneck
Partition topic according to database shard splits. Each consumer depends only on its linked database shard.

### Storage Efficiency
Partition by customer account to concentrate data into as few nodes as possible.

## Consumer Partition Assignment

- **Default (Eager)**: All consumers drop partitions and are reassigned on rebalance.
- **StickyAssignor**: Keeps partition numbers assigned to same instance where possible.
- **CooperativeStickyAssignor** (Kafka 2.4+): Only revokes difference in partitions. Can keep consuming during cooperative rebalance.
- **Static membership** (Kafka 2.3+): Avoid triggering rebalance if clients consistently ID as same member.

## Best Practices

1. Understand data access patterns (read/write patterns)
2. Choose appropriate number of partitions (match parallelism, avoid over/under-partitioning)
3. Use key-based partitioning when ordering/grouping is crucial
4. Consider data skew and load balancing
5. Plan for scalability
6. Set appropriate replication factor
7. Avoid frequent partition changes
8. Monitor and tune as needed
