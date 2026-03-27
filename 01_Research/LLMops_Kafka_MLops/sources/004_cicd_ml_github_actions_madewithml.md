---
source_id: 004
title: "CI/CD for Machine Learning - Made With ML"
url: "https://madewithml.com/courses/mlops/cicd/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_009"]
content_length: 4800
---

# CI/CD for Machine Learning

Using workflows to establish continuous integration and delivery pipelines to reliably iterate on ML applications.

## Intuition

We want to automatically execute ML workloads when certain events occur (new data, performance regressions, elapsed time, etc.) to ensure that models are always up to date and increasing in quality.

## GitHub Actions

GitHub Actions allow us to define workflows that are triggered by events (pull request, push, etc.) and execute a series of actions.

Workflows are defined under the repository's `.github/workflows` directory with separate workflows for:
- Documentation (`documentation.yaml`)
- Workloads (`workloads.yaml`) -- train/validate a model
- Serving (`serve.yaml`) -- deploy the model

### Events
Workflows are triggered by events: push, pull request, cron schedule, manually, and many more.

Example: `workloads` workflow triggered on pull request to main; `serve` and `documentation` workflows triggered on push to main.

### Jobs
Once event is triggered, jobs run on a runner (GitHub infrastructure or self-hosted). Jobs run in parallel by default; use `needs` keyword for dependent jobs.

### Steps
Each job contains a series of steps executed in order. Each step has a name, actions from GitHub Action marketplace and/or commands.

## Workflow: Workloads

Triggered on pull request to main:
1. Configure AWS credentials (for S3 model registry access)
2. Checkout repository code and install Python dependencies
3. Run Anyscale Job with credentials from repository secrets
4. Read results from S3 and convert JSON to markdown tables
5. Comment training and evaluation results on PR

This enables collaborative analysis of model performance before merging.

## Workflow: Serve

Triggered on push to main (after PR merge):
1. Configure AWS credentials
2. Checkout and install dependencies
3. Run Anyscale Service deployment (`anyscale service rollout`)

The rollout command updates existing service without changing SECRET_TOKEN or SERVICE_ENDPOINT, so downstream applications continue working.

## Workflow: Documentation

Also triggered on push to main:
1. Checkout and install dependencies (mkdocs)
2. Deploy documentation with `mkdocs gh-deploy --force`

## Continual Learning

The CI/CD pipeline creates an ideal workflow:
1. Make code changes and submit PR to main branch
2. Workloads workflow triggers model training/evaluation
3. If performance is better, merge PR
4. Serve workflow deploys to production (with documentation update)

Can be extended to include other triggers (new data, performance regressions) and integrate with orchestration tools (Prefect, Kubeflow) and monitoring.
