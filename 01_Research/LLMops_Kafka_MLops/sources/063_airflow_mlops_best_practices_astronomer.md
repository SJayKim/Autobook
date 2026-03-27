---
source_id: 063
title: "Best practices for orchestrating MLOps pipelines with Airflow"
url: "https://www.astronomer.io/docs/learn/airflow-mlops"
type: web
scraped_at: 2026-03-27
keywords: ["kw_037", "kw_007"]
content_length: 12500
---

# Best practices for orchestrating MLOps pipelines with Airflow

Machine Learning Operations (MLOps) is a broad term encompassing everything needed to run machine learning models in production. Apache Airflow sits at the heart of the modern MLOps stack. Because it is tool agnostic, Airflow can orchestrate all actions in any MLOps tool that has an API. Combined with already being the de-facto standard for orchestrating data pipelines, Airflow is the perfect tool for data engineers and machine learning engineers to standardize their workflows and collaborate on pipelines.

## Why use Airflow for MLOps?

The benefits of using Airflow for MLOps are:

- Python native: You use Python code to define Airflow pipelines, which makes it easy to integrate the most popular machine learning tools and embed your ML operations in a best practice CI/CD workflow. By using the decorators of the TaskFlow API you can turn existing scripts into Airflow tasks.
- Extensible: Airflow itself is written in Python, which makes it extensible with custom modules and Airflow plugins.
- Monitoring and alerting: Airflow comes with production-ready monitoring and alerting modules like Airflow notifiers, extensive logging features, and Airflow listeners. They enable you to have fine-grained control over how you monitor your ML operations and how Airflow alerts you if something goes wrong.
- Pluggable compute: When using Airflow you can pick and choose the compute you want to use for each task. This allows you to use the perfect environment and resources for every single action in your ML pipeline.
- Data agnostic: Airflow is data agnostic, which means it can be used to orchestrate any data pipeline, regardless of the data format or storage solution.
- Incremental and idempotent pipelines: Airflow allows you to define pipelines that operate on data collected in a specified timeframe and to perform backfills and reruns of a set of idempotent tasks. This lends itself well to creating feature stores, especially for time-dimensioned features.
- Ready for day 2 Ops: Airflow is a mature orchestrator, coming with built-in functionality such as automatic retries, complex dependencies and branching logic, as well as the option to make pipelines dynamic.
- Integrations: Airflow has a large ecosystem of integrations, including many popular MLOps tools.
- Shared platform: Both data engineers and ML engineers use Airflow, which allows teams to create direct dependencies between their pipelines, such as using Airflow Datasets.

## Why use Airflow for LLMOps?

Large Language Model Operations (LLMOps) is a subset of MLOps that describes interactions with large language models (LLMs). The three main techniques for LLMOps are:

- Prompt engineering: creating a pipeline that ingests user prompts and modifies them according to your needs, before sending them to the LLM inference endpoint.
- Retrieval augmented generation (RAG): RAG pipelines retrieve relevant context from domain-specific and often proprietary data to improve the output of an LLM.
- Fine-tuning: Fine-tuning LLMs typically involves retraining the final layers of an LLM on a specific dataset.

## Components of MLOps

MLOps consists of four main components:

- BusinessOps: the processes and activities in an organization that are needed to deliver any outcome, including successful MLOps workflows.
- DevOps: the software development and IT operations practices needed for the delivery of high quality software.
- DataOps: the practices and tools surrounding data engineering and data analytics to build the foundation for machine learning implementations.
- ModelOps: automated governance, management and monitoring of machine learning models in production.

### DataOps

There is no MLOps without data. You need to have robust data engineering workflows in place in order to confidently train, test, and deploy ML models in production. Give special considerations to:

- Data quality and data cleaning. Astronomer recommends incorporating data quality checks and data cleaning steps into your data pipelines. Airflow supports integration with data quality tools like Great Expectations and Soda Core.
- Data preprocessing and feature engineering. Data commonly undergoes transformation steps before it is ready to be used as input for an ML model, including scaling, one-hot-encoding, imputation of missing values, feature selection, dimensionality reduction, or feature extraction.
- Data storage. Training and testing data, model artifacts (model parameters, hyperparameters, and other metadata) — Airflow integrates with specialized version control systems such as MLFlow or Weights and Biases.

### ModelOps

With Airflow you can use the ML tools and compute locations of your choice:

- External Kubernetes clusters with the KubernetesPodOperator
- Databricks with the Astro Databricks provider
- Spark with modules from the Spark Airflow provider
- External compute in AWS, Azure and Google Cloud

## Airflow features for MLOps

- Data driven scheduling: With Airflow datasets, you can schedule DAGs to run after a specific dataset is updated by any task. For example, schedule your model training DAG to run after the training dataset is updated by the data engineering DAG.
- Dynamic task mapping: You can map tasks and task groups dynamically at runtime, for example running a set of model training tasks in parallel, each with different hyperparameters.
- Setup and teardown: Define setup and teardown tasks which create and remove resources used for machine learning, making the exact state of your environment reproducible.
- Branching: Branch your DAG based on the outcome of a task, for example deploy the model only if it performs above a certain threshold.
- Alerts and Notifications: Set up alerts for critical events in your ML pipelines, such as a drop in model performance or a data quality check failure.
- Automatic retries: Configure tasks to automatically retry if they fail according to custom set delays. Critical to protect your pipeline against outages of external tools or rate limits.
- Backfills and Reruns: Rerun previous DAG runs and create backfill DAG runs for any historical period. A key pattern for creating feature stores containing time-dimensioned features.

## Airflow integrations for MLOps

With Airflow, you can orchestrate actions in any MLOps tool that has an API. Integrations include:
- AWS SageMaker, Databricks, Cohere, OpenAI, Weights & Biases, Weaviate, OpenSearch, Pgvector, Pinecone, Snowpark, Azure ML.
- Cloud provider packages for AWS, Azure, and Google Cloud.
