---
source_id: 065
title: "Why data quality is key to successful ML Ops"
url: "https://greatexpectations.io/blog/ml-ops-data-quality/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_040"]
content_length: 5800
---

# Why data quality is key to successful ML Ops

Machine learning has been, and will continue to be, one of the biggest topics in data for the foreseeable future. And while we in the data community are all still riding the high of discovering and tuning predictive algorithms, we're also beginning to realize that ML isn't just a magic wand you can wave at a pile of data to quickly get insightful, reliable results.

Instead, we are starting to treat ML like other software engineering disciplines that require processes and tooling to ensure seamless workflows and reliable outputs. Data quality, in particular, has been a consistent focus, as it often leads to issues that can go unnoticed for a long time, bring entire pipelines to a halt, and erode the trust of stakeholders in the reliability of their analytical insights.

"Poor data quality is Enemy #1 to the widespread, profitable use of machine learning, and for this reason, the growth of machine learning increases the importance of data cleansing and preparation. The quality demands of machine learning are steep, and bad data can backfire twice -- first when training predictive models and second in the new data used by that model to inform future decisions."

## What is ML Ops?

The term ML Ops evolved from the better-known concept of "DevOps", which generally refers to the set of tools and practices that combines software development and IT operations. The goal of DevOps is to accelerate software development and deployment throughout the entire development lifecycle while ensuring the quality of software.

When applied to a machine learning context, the goals of ML Ops are very similar: to accelerate the development and production deployment of machine learning models while ensuring the quality of model outputs. However, unlike with software development, ML deals with both code and data:

1. Machine learning starts with data that's being ingested from various sources, cleaned, transformed, and stored using code.
2. That data is then made available to data scientists who write code to engineer features, develop, train and test machine learning models, which are eventually deployed to a production environment.
3. In production, ML models exist as code that takes input data from various sources and creates output data that's used to feed into products and business processes.

ML Ops incorporates tasks such as:
- Version control of any code used for data transformations and model definitions
- Automated testing of the ingested data and model code before going into production
- Deployment of the model in production in a stable and scalable environment
- Monitoring of the model performance and output

## How does data testing and documentation fit into ML Ops?

Data testing and documentation are absolutely essential to accomplishing the key goals of acceleration and quality at various stages in the ML workflow:

- On the stakeholder side, poor data quality affects the trust stakeholders have in a system, which negatively impacts the ability to make decisions based on it.
- On the engineering side, scrambling to fix data quality problems that were noticed by downstream consumers is one of the number one issues that cost teams time and slowly erodes team productivity and morale.
- Data documentation is essential for all stakeholders to communicate about the data and establish data contracts.

### At the data ingestion stage

Even at the earliest stages of working with a data set, establishing quality checks around your data and documenting those can immensely speed up operations in the long run. Solid data testing gives engineers confidence that they can safely make changes to ingestion pipelines without causing unwanted problems. When ingesting data from internal and external upstream sources, data validation at the ingestion stage is absolutely critical to ensure that there are no unexpected changes to the data that go unnoticed.

### When developing a model

For the model development process (feature engineering, model training, and model testing), guardrails around the data transformation code and model output support data scientists so they can make changes in one place without potentially breaking things in others. In classic DevOps tradition, continuous testing via CI/CD workflows quickly elicits any issues introduced by modifications to code. Running tests as well as writing new tests should be part of the ML model development process.

### When running a model in production

A model running in production depends on both the code and the data it is fed in order to produce reliable results. We need to secure the data input in order to avoid any unwanted issues stemming from either code changes or changes in the actual data. At the same time, we should also have some testing around the model output to ensure that it continues to meet our expectations. Especially in an environment with black box ML models, establishing and maintaining standards for quality is crucial in order to trust the model output.

Data testing and documentation are going to become one of the key focus areas of ML Ops in the near future, with teams moving away from "homegrown" data testing solutions to off-the-shelf packages and platforms that provide sufficient expressivity and connectivity to meet their specific needs and environments. Great Expectations is one such data validation and documentation framework that lets users specify what they expect from their data in simple, declarative statements.
