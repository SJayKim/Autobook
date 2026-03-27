---
source_id: 029
title: "Kafka Consumer Offsets Guide - Basic Principles, Insights & Enhancements"
url: "https://www.confluent.io/blog/guide-to-consumer-offsets/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_026", "kw_045"]
content_length: 11500
---

# Kafka Consumer Offsets Guide

By Alieh Saeedi, Confluent. April 2025.

## Offsets

In Kafka, an offset represents the position of a message within a partition. A consumer uses offsets to track progress. When reading message at offset 25, offset 26 is committed (next offset to read, not last processed). Committed offsets stored in internal `__consumer_offsets` topic.

Auto-commit enabled by default (every 5 seconds via `auto.commit.interval.ms`). Can disable with `enable.auto.commit=false` for manual control via `commitSync()` or `commitAsync()`.

## Control Records vs Data Records

Kafka transactions provide exactly-once semantics (EOS). Control records mark end of transactions, advance offset (not visible to applications), written to same data logs as regular records.

## Leader Epoch

Each partition has a designated leader broker. Leader epoch is a monotonically increasing number representing continuous leadership period. When new leader is elected, leader epoch increments.

## Committing Leader Epoch

Consumer should commit leader epoch along with offset for consistency. Leader epoch stored in `__consumer_offsets` topic. Helps identify correct leader at commit time, especially during leader changes and rebalances.

Without leader epoch: zombie leader scenarios can cause OFFSET_OUT_OF_RANGE errors after rebalances. With leader epoch: consumers detect stale metadata and refresh.

## Committing Specific Offsets

- `commitSync()`: Blocks until acknowledged. Reliable but reduces throughput.
- `commitAsync()`: Non-blocking. Better throughput but risk of commit failures.
- Both commit offset from last poll call by default.

For EOS: Use `KafkaProducer.sendOffsetsToTransaction()` to commit offsets within ongoing transaction atomically.

## How to Know Which Offset to Commit

Challenge: Consumer poll returns only data records. Control records also advance offset. So last record's offset + 1 may point to a control record, not the next data record. This can cause non-zero lag when upstream producer stops.

`Consumer.position()` returns next offset but no leader epoch metadata. May also throw TimeoutException.

## KIP-1094 Solution (Kafka 4.0.0)

New `ConsumerRecords` constructor with `nextOffsets` parameter. Provides correct next offset and leader epoch as `OffsetAndMetadata`. Deprecates old constructor without nextOffsets.

```java
public ConsumerRecords(
  Map<TopicPartition, List<ConsumerRecord<K, V>>> records,
  Map<TopicPartition, OffsetAndMetadata> nextOffsets) {}

public Map<TopicPartition, OffsetAndMetadata> nextOffsets();
```

Enables more precise and reliable offset commits, reducing errors and improving consistency.
