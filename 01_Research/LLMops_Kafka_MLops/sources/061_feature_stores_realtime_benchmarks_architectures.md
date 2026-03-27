---
source_id: 061
title: "Feature Stores for Real-time AI/ML: Benchmarks, Architectures, and Case Studies"
url: "https://mlops.community/feature-stores-for-real-time-ai-ml-benchmarks-architectures-and-case-studies/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_005"]
content_length: 9200
---

# Feature Stores for Real-time AI/ML: Benchmarks, Architectures, and Case Studies

Real-time artificial intelligence/machine learning (AI/ML) use cases, such as fraud detection and recommendation, are on the rise, and feature stores play a key role in deploying them successfully to production. The most important characteristic of a feature store for real-time AI/ML is the feature serving speed from the online store to the ML model for online predictions or scoring. Successful feature stores can meet stringent latency requirements (measured in milliseconds), consistently (think p99) and at scale (up to millions of queries per second, with gigabytes to terabytes-sized datasets) while at the same time maintaining a low total cost of ownership and high accuracy.

The choice of an online feature store, as well as the architecture of the feature store, play important roles in determining how performant and cost-effective it is.

## Open Source Feast

Feast recently did a benchmark to compare its feature serving latency when using different online stores (Redis vs. Google Cloud DataStore vs. AWS DynamoDB). It also compared the speed of using different mechanisms for extracting the features (e.g. Java gRPC server, Python HTTP server, lambda function, etc.). The bottom line: Feast found it was by far the most performant using the Java gRPC server and with Redis as the online store.

Better.com implemented its lead scoring ranking system using the open-source Feast feature store. The features are materialized from the offline stores (S3, Snowflake, and Redshift) to the online store (Redis). In addition to that, features are also ingested into the online store from streaming sources (Kafka topics). Feast recently added support for streaming data sources (in addition to batch data sources) which is currently supported only for Redis. Supporting streaming data sources is very important for real-time AI/ML use cases as these use cases rely on fresh live data.

In a lead scoring use case for Better.com, new leads are being ingested continuously throughout the day. The features come from many different sources, and both the entities (the leads) and the features used to score them get updated all the time, thus, the leads get ranked and re-ranked. Better.com leads expire after 48 hours, and this is implemented in the Redis online store by simply setting time to live (TTL) to 48 hours.

Another interesting implementation of Feast is the Microsoft Azure Feature Store. It runs on the Azure cloud optimized for low latency real-time AI/ML use cases, supporting both batch and streaming sources, as well as integration into the Azure Data & AI ecosystem. The features are ingested in the online store from both batch sources (Azure Synapse Serverless SQL, Azure Storage / ADLS) and from streaming sources (Azure Event Hub).

## Wix DIY Feature Store

The Wix feature store is used for real-time use cases such as recommendations, churn and premium predictions, ranking, and spam classifiers. Wix serves over 200M registered users of which only a small fraction are 'active users' at any given time.

Over 90% of the data stored in the Wix feature store are clickstreams and the ML models are triggered per website or per user. For real-time use cases, latency is a big issue—for some of their production use cases, they need to extract the feature vectors within milliseconds.

The raw data is stored in Parquet files on AWS in an S3 bucket. In a daily build batch process using Spark, SQL (which takes minutes to hours) all the users' history features are extracted from S3, pivoted and aggregated by the user, and ingested into the offline store (Apache Hbase). Once the system detects that a user is currently active, a 'warmup' process is triggered and the features of that user are loaded into the online store (Redis) which is much smaller than the offline store since it holds only the user history of the active users. Features in the online feature store are continuously updated using fresh live real-time data directly from the streaming sources per each event coming from the user (using Apache Storm).

This type of architecture has a lower ratio of writes to reads compared to the Feast architecture, which is very efficient in terms of materialization and online storage since it only stores features for active users in the online store rather than those for all users.

## Commercial Feature Store Tecton

In addition to batch data sources and streaming data sources, Tecton also supports 'out-of-the-box' real-time data sources. These are also called 'real-time features' or 'real-time' transformations. Real-time features can be calculated only at the inference request. For example the difference between the size of the suspected transaction and the last transaction size. Like with Feast and the Wix feature stores, Tecton also defines the features in the registry so that the logical definition is defined once for both offline and online stores. This significantly reduces training-serving skew to ensure high accuracy of the ML model also in production.

With respect to the choice of offline store, online store, and benchmarking, for the offline feature store Tecton supports S3, for the online store Tecton now offers its customers a choice between DynamoDB and Redis Enterprise Cloud. Tecton's benchmarking showed that for high throughput use cases, Redis Enterprise was 3x faster and at the same time 14x less expensive compared to DynamoDB.

## Lightricks using Commercial Feature Store Qwak

Lightricks uses the commercial feature store Qwak for its recommendation system. The Qwak feature store supports three types of features sources: batch, streaming, and real-time features.

With the Qwak feature store, the materialization of features into the feature store is done directly from the raw data sources for both the offline store (using Parquet files on S3) and the online store (using Redis). This is different compared to the feature stores examples from Wix, Feast, or Tecton in which the materialization of the online store is done from the offline store to the online store for the batch sources. This has the advantage that not only the transformation logic of a feature is unified across training and serving flows, but also the actual transformation or feature computation is done uniformly, further decreasing training-serving skew.

## Summary

There are significant differences in the performance and cost of feature stores, depending on the architecture, supported type of features, and components selected.
