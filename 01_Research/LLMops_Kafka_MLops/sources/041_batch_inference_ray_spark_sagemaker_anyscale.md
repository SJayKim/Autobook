---
source_id: 041
title: "Offline Batch Inference: Comparing Ray, Apache Spark, and SageMaker"
url: "https://www.anyscale.com/blog/offline-batch-inference-comparing-ray-apache-spark-and-sagemaker"
type: web
scraped_at: 2026-03-27
keywords: ["kw_035", "kw_030"]
content_length: 9800
---

# Offline Batch Inference: Comparing Ray, Apache Spark, and SageMaker

As more companies use large scale machine learning (ML) models for training and evaluation, offline batch inference becomes an essential workload. A number of challenges come with it: managing compute infrastructure; optimizing use of all heterogeneous resources; and transferring data from storage to hardware accelerators. Addressing these challenges, Ray performs significantly better as it can coordinate clusters of diverse resources, allowing for better utilization of the specific resource requirements of the workload.

## Introduction

Offline batch inference is a critical workload for many AI products, especially with the growing usage of pre-trained foundation models. At its core, it seems like a simple problem: given a trained model and a dataset, get model predictions for each data point.

However, there are many challenges to doing this at scale:

1. **Challenge 1:** Managing compute infrastructure and cloud clusters, especially when needing to use heterogeneous clusters, consisting of different instance types to maximize throughput.
2. **Challenge 2:** Parallelizing data processing and utilizing all resources (CPUs & GPUs) in the cluster at any given point in time.
3. **Challenge 3:** Efficiently transferring data between cloud storage, CPU RAM for preprocessing, and GPU RAM for model inference, especially for unstructured data like images and text.
4. **Challenge 4:** A user experience that makes it easy to iterate and develop while working at scale.

## What does the industry recommend for offline batch inference?

Three categories of solutions attempt to address the above challenges:

1. **Batch Services:** Cloud providers such as AWS, GCP, and Azure provide batch services to manage compute infrastructure. They handle infrastructure management but have limitations such as lack of software libraries for optimization.
2. **Online Inference solutions:** Solutions like BentoML or Ray Serve provide APIs for performant inference code but are designed for online rather than offline batch inference.
3. **Distributed data systems:** These solutions are designed to handle large amounts of data. Examples include Apache Spark and Ray Data.

Ray Data is the best practical solution for offline batch inference for modern deep learning applications, both in terms of performance and user experience.

## Image Classification: SageMaker Batch Transform vs. Apache Spark vs. Ray Data

Using images from the ImageNet 2012 Dataset and a pre-trained PyTorch ResNet50 model, workload involved: Reading images from S3, Simple CPU preprocessing (resizing, cropping, normalization), Model inference on GPU.

When running with a 10 GB dataset on a single g4dn.12xlarge instance (48 CPUs, 4 GPUs), Ray Data achieves speeds up to 17x faster than SageMaker Batch Transform and 2x faster than Spark for offline image classification.

## SageMaker Batch Transform limitations

SageMaker Batch Transform uses the same architecture as for online serving systems under the hood. It starts an HTTP server, deploys the model as an endpoint, and sends a separate request for each image. SageMaker does not provide support for batching across multiple files, and the max payload per request is 100 MB.

## Comparing Spark and Ray for batch inference

Ray Data has 2x faster throughput than Spark. Key differences:

**Challenge #2: Hybrid CPU and GPU workload**
Deep learning workloads involve both CPU and GPU computation. Spark scheduling fuses all stages together regardless of resource requirements, limiting total parallelism by the number of GPUs. Ray Data can independently scale the CPU preprocessing and GPU inference steps, streaming data through these stages, increasing CPUs and GPUs utilization and reducing out-of-memory errors.

**Challenge #3: Large, multi-dimensional tensors**
Ray Data has Numpy batch format as a first-class citizen, and does not require Pandas, which leads to higher performance and more memory efficiency for deep learning workloads.

**Challenge #4: Ray is Python native**
Another fundamental difference is that Ray is Python native whereas Spark is not, which also impacts performance. A microbenchmark applying time.sleep(1) UDF takes 80 seconds on Spark vs under 5 seconds on Ray Data, likely due to JVM<>Pyarrow overhead.

## Scaling up Ray Data and maximizing performance

Testing scalability with 10 TB worth of images using a single cluster of 10 g4dn.12xlarge instances and 10 m5.16xlarge instances.

**Throughput: 11,580.958 img/sec**

Ray Data achieves over 90%+ GPU utilization throughout the workload run. The ability to scale to many GPUs and large data sizes without needing to rewrite code and not sacrificing on throughput is what sets Ray Data apart.

## Conclusion

Ray Data best meets all four challenges: abstracts away compute infrastructure management with heterogeneous cluster support, streams data from cloud storage to CPU to GPU ensuring full utilization, has native support for multi-dimensional tensors, and is Python native. Ray Data significantly outperforms SageMaker Batch Transform (by 17x) and Spark (by 2x and 3x) while linearly scaling to TB level data sizes.
