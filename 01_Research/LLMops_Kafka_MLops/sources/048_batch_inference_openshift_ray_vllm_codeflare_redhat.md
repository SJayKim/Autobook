---
source_id: 048
title: "Batch inference on OpenShift AI with Ray Data, vLLM, and CodeFlare"
url: "https://developers.redhat.com/articles/2025/08/07/batch-inference-openshift-ai-ray-data-vllm-and-codeflare"
type: web
scraped_at: 2026-03-27
keywords: ["kw_035", "kw_004", "kw_030"]
content_length: 5800
---

# Batch inference on OpenShift AI with Ray Data, vLLM, and CodeFlare

Inference is the process of using a trained model to make predictions on new, unseen data. While running a prediction on a single row in a Jupyter notebook is straightforward, this approach doesn't scale to the millions of rows found in large datasets. This blog demonstrates how both platform engineers and data scientists can solve this challenge using the CodeFlare SDK with Ray Data and vLLM on OpenShift AI.

## Online versus offline inference

- **Online inference:** Designed for immediate, single-request predictions where low latency is essential. Powers interactive AI applications -- when you send a prompt to an LLM, your request hits an API endpoint and the model performs inference in real time.
- **Offline (batch) inference:** Used to process a large volume of data at once. Overall completion time is more important than the latency of any single prediction. Ideal for generating reports, analyzing a month's worth of sensor data, or classifying large image collections.

## Connecting to a Ray cluster via the CodeFlare SDK

The CodeFlare SDK acts as the bridge between your Python environment and the Ray cluster. Connect via RayJobClient with dashboard URL and authentication token:

```python
from codeflare_sdk import RayJobClient
auth_token = "replace-me"
header = {'Authorization': f'Bearer {auth_token}'}
ray_dashboard = "replace-me"
client = RayJobClient(address=ray_dashboard, headers=header, verify=True)
```

## Building your remote batch inference job

### Configuring the vLLM inference engine

At the heart is the vLLMEngineProcessorConfig from Ray Data. Model sourcing options:

1. **From Hugging Face Hub:** Provide the model's HF repository ID. For private/gated models, provide HF_TOKEN via runtime_env.
2. **From cloud storage (S3, GCS):** Cache model in own storage for production stability. Use runai_streamer format for optimized loading.
3. **From local path on cluster:** If model is already on cluster's filesystem.

### Tuning for performance

- `concurrency`: Number of parallel vLLM workers. Set to number of available GPUs.
- `batch_size`: Rows grouped per worker. Larger batches improve GPU utilization.
- `tensor_parallel_size`: For large models that don't fit on a single GPU (model parallelism).

Example configuration:
```python
processor_config = vLLMEngineProcessorConfig(
    model_source="unsloth/Llama-3.1-8B-Instruct",
    batch_size=32,
    concurrency=4,  # 4 GPUs
    engine_kwargs={
        "dtype": "half",
        "max_model_len": 4096,
        "tensor_parallel_size": 4,
    },
)
```

### Defining the processing logic

Use build_llm_processor to create the full inference pipeline:
- `preprocess`: Transform input row to LLM-expected format (OpenAI chat message format)
- `postprocess`: Clean up LLM output

```python
processor = build_llm_processor(
    processor_config,
    preprocess=lambda row: dict(
        messages=[
            {"role": "system", "content": "You are a calculator..."},
            {"role": "user", "content": f"{row['id']} ** 3 = ?"},
        ],
        sampling_params=dict(temperature=0.3, max_tokens=20),
    ),
    postprocess=lambda row: {"resp": row["generated_text"]},
)
ds = ray.data.range(100)
ds = processor(ds)
ds = ds.materialize()
```

### Submitting and monitoring the job

Use RayJobClient to submit with entrypoint_command and runtime_env:

```python
submission_id = client.submit_job(
    entrypoint="python batch_inference.py",
    runtime_env={
        "pip": ["vllm==0.9.1", "s3fs"],
        "env_vars": {
            "HF_TOKEN": "your-token",
            "AWS_ACCESS_KEY_ID": "your_key",
        }
    }
)
client.get_job_status(submission_id)
client.get_job_logs(submission_id)
```

## Conclusion

By defining model configuration and processing logic in a simple Python script, you can use the RayJobClient to send that workload to a remote Ray cluster. This workflow allows full power of distributed computing and modern inference engines like vLLM without ever leaving the Python environment.
