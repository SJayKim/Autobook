---
source_id: 024
title: "A Guide to Stream Processing and ksqlDB Fundamentals"
url: "https://www.confluent.io/blog/guide-to-stream-processing-and-ksqldb-fundamentals/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_021", "kw_013", "kw_014"]
content_length: 6800
---

# A Guide to Stream Processing and ksqlDB Fundamentals

## Introduction to ksqlDB

ksqlDB is a database purpose-built for data in motion. It allows building and deploying streaming applications using familiar SQL syntax. It splits its distributed compute layer and distributed storage layer, enabling rich streaming applications backed by Apache Kafka.

## Interacting with ksqlDB

Options: Confluent Cloud Console (graphical editor), CLI (command-line interface), native Java client, and REST API.

## Creating, Importing, and Exporting Data

Create new streams and tables (ksqlDB creates backing Kafka topics), create streams/tables based on existing topics, insert data via SQL INSERT, or use ksqlDB's Kafka Connect integration to pull/push data from/to external systems.

## Filtering Events

Simple SQL WHERE clause: `SELECT * FROM stream WHERE field = 'value'`. Can create new streams with backing Kafka topics: `CREATE STREAM filtered AS SELECT * FROM unfiltered WHERE field = 'value'`.

## Lookups and Joins

Load data into a ksqlDB table and enrich event streams using SQL JOIN syntax. Join multiple streams and tables to derive exact data needed.

## Transforming Data

Derive new streams from existing ones. Drop fields, combine with CONCAT, rename with AS, change types with CAST. Many built-in functions available.

## Converting Data Formats

Not limited to source stream format. Using VALUE_FORMAT property, specify format for any new stream/table (e.g., convert JSON to AVRO).

## Merging and Splitting Streams

Merge: `CREATE STREAM ... AS SELECT` + `INSERT INTO ... SELECT` for each stream to merge.
Split: Series of `CREATE STREAM ... AS SELECT ... WHERE` queries.

## Streams and Tables

Streams: unbounded series of events, map closely to underlying topic. Events may or may not have a key.
Tables: require a key, represent most recent value for each key. Updated as new events land.

## Stateful Aggregations

SQL aggregation (COUNT, SUM, etc.) results in a table. `CREATE TABLE AS` turns aggregation into persistent table with latest results. Key = GROUP BY field(s).

## Push and Pull Queries

Pull query: returns current value for a given key (like relational DB).
Push query: returns continuous stream of results via `EMIT CHANGES` clause.

## Architecture

Built on Kafka Streams under the covers. ksqlDB can run pre-built Kafka Connect connectors directly on its servers.

## Code Lifecycle

ksql-migrations: scriptable command-line tool for managing ksqlDB streams and tables.
