---
source_id: 043
title: "Demystifying Quantizations: Guide to Quantization Methods for LLMs"
url: "https://cast.ai/blog/demystifying-quantizations-llms/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_046", "kw_036"]
content_length: 11500
---

# Demystifying Quantizations: Guide to Quantization Methods for LLMs

Quantization is key to running large language models efficiently, balancing accuracy, memory, and cost. This guide explains quantization from its early use in neural networks to today's LLM-specific techniques like GPTQ, SmoothQuant, AWQ, and GGUF.

## Why quantization? Recap of data types used in LLMs

To understand quantization, it helps to start with the data types involved. When an open-source model is downloaded, the artificial neural network inside is essentially a collection of numbers stored across multiple files, along with some accompanying metadata.

### Data type formats

**Integers:** Most basic data type, represented as a sequence of bits. Efficient and inexpensive to compute with, but sacrifice precision.

**Floating-point number representation (IEEE 754):**
- Single precision (FP32): 1 sign bit, 8 exponent bits, 23 mantissa bits. The most used precision in industry while training neural networks.
- Half precision (FP16): 16-bit format.
- bfloat16: Google invented "brain floating point" which is the standard used today when publishing unquantized models. Same dynamic range as fp32 but sacrifices precision.

**4-bit numbers:** In practice, 4-bit precision is generally the lowest useful level applied in post-training quantization. int4 and fp4 formats present their own trade-offs.

### Memory impact

For a Qwen3-32B model, moving from BF16 to INT4 would mean around 45 GB less memory needed to store the model. This directly affects which GPUs are compatible and how expensive the inference workload becomes.

### Energy per operation

The choice of number format significantly impacts efficiency. Integer operations are drastically cheaper than floating-point. INT8 multiply is 30x more energy-efficient than FP32 multiply.

## Quantization: a short history

Before 2017, quantization for neural networks was mostly an academic topic. The paper "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference" made all the difference, implemented in TensorFlow Lite.

### K-means-based quantization

Weights in any given layer are typically normally distributed. This method clusters numbers around centroids. For input numbers you want to quantize, apply K-means clustering and find 2^n different centroids to map continuous values to discrete values.

### Linear quantization

Linear quantization is an affine mapping of integers to real numbers. Two modes: symmetric and asymmetric. The goal is to map the continuous floating-point range to few discrete integer points. Key parameters: scaling parameter (S) and zero point (Z).

## Quantization in the LLM era

Why traditional methods are insufficient for LLMs: at around 6.7B parameters, some features emerge that prevent easy quantization. Large outlier values appear in activations (e.g., [-60, -45, -51, -35, -20, -67]). These outliers cause traditional methods to squish and lose too much knowledge.

## Quantization methods for LLMs

### GPTQ

GPTQ was the first quantization method to compress LLMs down to the 4-bit range while maintaining accuracy. Used Hessian-based optimization. When written, the method didn't provide speedups as hardware didn't support it. At the time of writing (2025), GPTQ speedups are available on some hardware. GPTQ did not do any compression on activations.

### SmoothQuant

SmoothQuant quantizes both weights and activations to 8 bits (W8A8). Also speeds up mathematical operations on hardware. Main idea: activations are much more outlierish than weights. By transferring some outlier magnitude to weights, the quantization process is smoothed. Useful for batch workloads regarding speedups and compression. A 530B model could be served on just one node.

### Activation aware quantization (AWQ)

AWQ quantizes the weights with respect to the activations. Compresses only weights to 4 bits and leaves activations untouched in 16 bits (W4A16). By protecting salient weights based on activation patterns, it reduces quantization errors in critical channels. AWQ was presented as SOTA method when published.

### GGUF

GGUF is a file format for storing models for inference, not a quantization method per se. Originated from the GGML library. Three types of quants in GGML:
- Legacy quants (Q4_0 etc.) - not commonly used
- k-quants (Q3_K_S etc.) - older, still used but not recommended
- i-quants (IQ3_S etc.) - state of the art in GGML/llama.cpp, recommended

All are block-based quants: scaling is applied and statistics determined based on blocks of the tensor.

### Hardware considerations

Each specific data type needs custom implementation on hardware. The hardware at your disposal influences quantization choices, dictating speedup and improvements.

## Conclusion

Quantization is essential for scaling LLMs efficiently. GPTQ provides significant memory savings, SmoothQuant enables W8A8 for batch workloads, AWQ offers best accuracy at 4-bit on GPU for production serving, and GGUF/GGML provides flexible quantization options optimized for CPU/edge deployment.
