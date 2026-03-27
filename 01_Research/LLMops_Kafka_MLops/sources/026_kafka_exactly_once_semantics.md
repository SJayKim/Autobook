---
source_id: 026
title: "Exactly-once Semantics is Possible: Here's How Apache Kafka Does it"
url: "https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_045", "kw_003"]
content_length: 15200
---

# Exactly-once Semantics is Possible: Here's How Apache Kafka Does it

By Neha Narkhede, Guozhang Wang (Confluent). Originally published 2017, updated March 2025.

## Messaging Semantics Explained

- **At-least-once**: Producer retries on ack timeout/error. May cause duplicate writes if broker wrote but failed before ack.
- **At-most-once**: Producer doesn't retry. Message might not be written. No duplicates but possible loss.
- **Exactly-once**: Even with retries, message delivered exactly once to end consumer. Requires cooperation between messaging system and application.

## Failures That Must Be Handled

1. **Broker failure**: Kafka tolerates n-1 broker failures via replication. ISR takes over leadership seamlessly.
2. **Producer-to-broker RPC failure**: Broker can crash after writing but before ack. Producer forced to retry, potentially causing duplicates.
3. **Client failure**: Must distinguish permanent vs. temporary failure. Broker should discard zombie producer messages. Consumer must recover from safe point.

## Exactly-Once Semantics in Apache Kafka

### Idempotence: Exactly-Once per Partition

Producer send is idempotent. Same message sent multiple times only written once to Kafka log. Each batch contains a sequence number; broker deduplicates. Sequence number persisted to replicated log (unlike TCP's transient in-memory connection).

Configuration: `enable.idempotence=true`. Kafka 3.0+ enables by default.

### Transactions: Atomic Writes Across Multiple Partitions

Producer can send batch of messages to multiple partitions atomically - either all visible or none visible to consumers.

Consumer isolation levels:
- `read_committed`: Read transactional messages only after commit.
- `read_uncommitted`: Read all messages (default Kafka behavior).

Configuration: Set `transactional.id` on producer for continuity across restarts.

### Exactly-Once Stream Processing

Set `processing.guarantee=exactly_once` in Kafka Streams. All processing and materialized state written back to Kafka exactly once.

Guarantee: For each received record, processed results reflected once, even under failures. The output of read-process-write operation would be same as if no failure occurred.

## Design and Testing

- 60-page design document with 9-month public review.
- Transaction log is a Kafka topic (inherits durability).
- Transaction coordinator runs within broker (leverages Kafka leader election).
- 15,000+ LOC of tests including distributed chaos tests.

## Performance

- Idempotent producer: negligible overhead.
- Transactional producer: only 3% throughput decline vs. at-least-once (acks=all).
- New message format (v2): 20% improvement in producer throughput, 50% in consumer throughput for small messages (available to all Kafka 0.11+ users).
- Kafka Streams with 100ms commit interval: 15-30% throughput degradation. With 30s interval: no overhead for 1KB+ messages.
