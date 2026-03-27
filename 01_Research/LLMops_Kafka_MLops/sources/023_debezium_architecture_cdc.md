---
source_id: 023
title: "Debezium Architecture"
url: "https://debezium.io/documentation/reference/stable/architecture.html"
type: web
scraped_at: 2026-03-27
keywords: ["kw_018", "kw_003"]
content_length: 2100
---

# Debezium Architecture

Most commonly, Debezium is deployed by means of Apache Kafka Connect. Kafka Connect is a framework and runtime for implementing and operating:
- Source connectors such as Debezium that send records into Kafka
- Sink connectors that propagate records from Kafka topics to other systems

## CDC Pipeline Architecture

The Debezium connectors for MySQL and PostgreSQL are deployed to capture changes to these databases. Each Debezium connector establishes a connection to its source database:
- The MySQL connector uses a client library for accessing the binlog
- The PostgreSQL connector reads from a logical replication stream

Kafka Connect operates as a separate service besides the Kafka broker.

By default, changes from one database table are written to a Kafka topic whose name corresponds to the table name. Topic routing transformation allows:
- Routing records to a differently named topic
- Streaming change events for multiple tables into a single topic

After change event records are in Apache Kafka, different connectors in the Kafka Connect ecosystem can stream records to other systems: Elasticsearch, data warehouses, analytics systems, or caches such as Infinispan.

## Debezium Server

An alternative deployment: a configurable, ready-to-use application that streams change events from a source database to various messaging infrastructures. Change events can be serialized to JSON or Apache Avro and sent to Amazon Kinesis, Google Cloud Pub/Sub, or Apache Pulsar.

## Debezium Engine

Debezium connectors can run as a library embedded into custom Java applications (without full Kafka/Kafka Connect clusters). Useful for consuming change events within the application itself, or for streaming changes to alternative messaging brokers.
