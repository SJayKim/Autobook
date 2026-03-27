---
source_id: 067
title: "Implement CDC & Streaming Analytics Using Kafka & Debezium"
url: "https://www.confluent.io/blog/cdc-and-streaming-analytics-using-debezium-kafka/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_042"]
content_length: 7800
---

# Implement CDC & Streaming Analytics Using Kafka & Debezium

Change Data Capture (CDC) is an excellent way to introduce streaming analytics into your existing database, and using Debezium enables you to send your change data through Apache Kafka. Although most CDC systems give you two versions of a record, as it was before and as it is after the change, it can be difficult to work with if you're maintaining a replica somewhere else. The Debezium MongoDB CDC Connector gives you just the record-by-record changes that allow you to do exactly what you desire, especially if the change delta itself is of analytical value.

## Change Data Capture with Debezium

Debezium is a collection of Kafka Connect connectors for different databases. As a Kafka Connect plugin, Debezium requires downloading the connector and adding it to Connect's plugin.path. Once the plugin is present, you can configure a connector for a MongoDB collection.

The connector will get to work and start sending documents to a topic it has created. If you take a look at the new topic, you can see the document inside Debezium's transport envelope. The envelope consists of a schema and a payload. You can see an after property in the payload that contains the complete document as a string.

When you encounter your first change (update), unlike the Debezium CDC connectors for other databases, with MongoDB you only get a patch. While you could write your consumers to handle this, it would have two negative consequences: every consumer would need to read the whole topic in order to get the initial complete version of the document and all changes, and you'd have duplicate logic handling the merge of the sequence of patches.

## Streams and Tables with Kafka Streams

At its core, Kafka Streams provides two different abstractions on top of regular Kafka topics: streams and tables. A stream is a sequence of events that typically needs to be processed in a certain order, representing an element-by-element evolution of the whole dataset. A table, on the other hand, is a snapshot of the whole dataset at a particular point in time.

There is an interesting interplay between streams and tables: Processing one produces the other. If you accumulate all the events up to a point in time, you produce a table. Should you then emit each change of this table, you produce a new stream.

Using Debezium, changes to the MongoDB table are emitted into a topic representing a stream of changes. With Kafka Streams, you accumulate these into a table by applying each patch as they arrive, and as the table changes, it will emit the complete record as a new stream. This means new consumers can begin reading the merged stream at any point as it will always contain complete records.

## Implementing Kafka Streams for Debezium

Writing a Kafka Streams application involves:

1. Configuration: specifying where Kafka can be found, using a StreamsBuilder to create the stream (KStream) and table (KTable).
2. Stream processing: Using SQL-like syntax with leftJoin, groupByKey, reduce, and toStream operations.

The core logic:
- Take the KStream (cdc), perform a left join with the KTable (table), and apply a merge function for each joined row.
- A left join is required as you will receive new documents that do not yet exist in the table.
- Group the data by key for partitioning purposes and reduce the group to materialize the stream as a table.

The merge function handles Debezium's operations:
- "c" (create) and "r" (read): handled as new, complete documents contained in the "after" element
- "d" (delete): return null to remove the document
- "u" (update): apply the patch to the existing document using $set and $unset operations

You can extend the merge logic to emit before/after versions (typical for CDC systems) and even a delta version showing the difference between the two states, including type-specific handling (e.g., numeric differences, duration calculations for timestamps).

## Summary

By combining Debezium and Kafka Streams, you can enrich the change-only data from MongoDB with the historic document state to output complete documents for further consumption. Using Debezium's envelope metadata, you're able to access the typical before and after versions that other CDC systems generate as well as the delta version, which in some scenarios may be all you need.
