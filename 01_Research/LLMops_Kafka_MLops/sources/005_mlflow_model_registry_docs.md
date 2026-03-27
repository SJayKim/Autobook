---
source_id: 005
title: "ML Model Registry | MLflow AI Platform"
url: "https://mlflow.org/docs/latest/ml/model-registry/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_010", "kw_031"]
content_length: 4200
---

# ML Model Registry | MLflow AI Platform

The MLflow Model Registry is a centralized model store, set of APIs and a UI designed to collaboratively manage the full lifecycle of a machine learning model. It provides lineage (which MLflow experiment and run produced the model), versioning, aliasing, metadata tagging and annotation support.

## Why Model Registry?

As ML projects grow in complexity, managing models manually becomes error-prone and inefficient. Benefits:

- **Version Control**: Automatically tracks versions, allows comparing iterations, rolling back, managing multiple versions in parallel (staging vs production)
- **Model Lineage and Traceability**: Each version linked to the MLflow run, logged model or notebook that produced it. Full reproducibility.
- **Production-Ready Workflows**: Model aliases (e.g., @champion) and tags for managing deployment workflows, promoting models to experimental/staging/production.
- **Governance and Compliance**: Structured metadata, tagging, role-based access controls for enterprise-grade ML operations.

## Concepts

| Concept | Description |
| --- | --- |
| Model | Created with `mlflow.<model_flavor>.log_model()` or `mlflow.create_external_model()` API |
| Registered Model | Has unique name, contains versions, aliases, tags, and metadata |
| Model Version | Each registered model can have multiple versions. New models increment version number. Versions have tags. |
| Model URI | Format: `models:/<model-name>/<model-version>` |
| Model Alias | Mutable named reference to a particular version. E.g., `champion` alias for production. URI: `models:/MyModel@champion` |
| Tags | Key-value pairs for labeling and categorizing (e.g., `task:question-answering`, `validation_status:approved`) |
| Annotations | Markdown descriptions for top-level model and each version |

## Model Registry in Practice

### OSS MLflow
Provides UI and API for versioning and managing ML models.

Register a model:
```
# Option 1: during logging
mlflow.<flavor>.log_model(..., registered_model_name="<MODEL_NAME>")

# Option 2: after logging
mlflow.register_model(model_uri="<MODEL_URI>", name="<MODEL_NAME>")
```

Load a registered model:
```
mlflow.<flavor>.load_model("models:/<MODEL_NAME>/<VERSION>")
```

### Databricks Integration
Extends MLflow with Unity Catalog for:
- Enhanced governance with access policies and permission controls
- Cross-workspace access
- Model lineage tracking
- Discovery and reuse from shared catalog

## MLOps and GenAIOps

GenAIOps introduce extra capabilities that complement MLOps maturity levels rather than replace them: prompt lifecycle, retrieval augmentation, output safety, and token cost governance.
