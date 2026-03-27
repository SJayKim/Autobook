---
source_id: 123
title: "Improving Automated Retraining of Machine-Learning Models"
url: "https://www.sei.cmu.edu/blog/improving-automated-retraining-of-machine-learning-models/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_033"]
content_length: 5500
---

# Improving Automated Retraining of Machine-Learning Models

By Rachel Brower-Sinning, SEI/CMU. Published May 2, 2022.

Machine learning (ML) models are increasingly used to support mission and business goals, ranging from determining reorder points for supplies, to event triaging, to suggesting courses of action. However, ML models degrade in performance after being put into production, and must be retrained, either automatically or manually, to account for changes in operational data with respect to training data. Manual retraining is effective, but costly, time consuming, and dependent on the availability of trained data scientists.

Current industry practice offers MLOps as a potential solution to achieve automatic retraining. These industry MLOps pipelines do achieve faster retraining time, but pose a greater range of future prediction errors because they simply offer a refitting of the old model to new data instead of analyzing for changes in the data.

## Proposed Improvements to Current Practice

Current practice for refitting of an old model to new data has several limitations:
- It assumes that new training data should be treated the same as the initial training data
- Model parameters are assumed constant and should be the same as those identified with the initial training data
- Refitting is not based on any information about why the model was performing poorly
- There is no informed procedure for how to combine the operational dataset with the original training dataset

An MLOps process that relies on automatic retraining based on these assumptions cannot guarantee that the new retrained model will perform well. The consequence is potentially poor model performance, which may lead to reduced trust in the model or system.

The automated data-analysis tasks developed at SEI are analogous to manual tests and analyses done by data scientists during model retraining. Specifically, the goal was to automate Steps 1 to 3 -- analyze, audit, select -- which is where data scientists spend much of their time. A model operational analysis step was built that executes after the monitor model step of an MLOps pipeline signals a need for retraining.

## Approach for Retraining in MLOps Pipelines

The goal was to develop a model operational analysis module to automate and inform retraining in MLOps pipelines. Research questions addressed:

1. What data must be extracted from the production system to automate "analyze, audit, and select"?
2. What is the best way to store this data?
3. What statistical tests, analyses, and adaptations on this data best serve as input for automated or semi-automated retraining?
4. In what order must tests be run to minimize the number of tests to execute?

The iterative and experimental process included:

**Model and dataset generation** -- Developed datasets and models for inducing common retraining triggers, such as general data drift and emergence of new data classes. Used a simple color dataset (continuous data) with models such as decision trees and k-means, and the public Fashion MNIST dataset (image data) with deep neural-network models.

**Identification of statistical tests and analyses** -- Determined the statistical tests and analyses required to collect the information for automated retraining. Created a testing pipeline to determine: (1) differences between development and operational datasets, (2) where the deployed ML model was lacking in performance, and (3) what data should be used for retraining.

**Implementation of model operational analysis module** -- Developed and automated: (1) data collection and storage, (2) identified tests and analyses, and (3) generation of results and recommendations to inform the next retraining steps.

**Integration into an MLOps pipeline** -- Integrated the module into an MLOps pipeline to observe and validate the end-to-end process from the retraining trigger to the generation of recommendations for retraining to the deployment of the retrained model.

## Outputs

- Statistical tests and analyses that inform the automated retraining process with respect to operational data changes
- Prototype implementation of tests and analyses in a model operational analysis module
- Extension of an MLOps pipeline with model operational analysis

The key insight: improved MLOps pipelines can reduce manual model retraining time and cost by automating initial steps of the retraining process, and provide immediate, repeatable input to later steps so that data scientists can focus on tasks more critical to improving model performance.
