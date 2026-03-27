---
source_id: 044
title: "Pruning and Distilling LLMs Using NVIDIA TensorRT Model Optimizer"
url: "https://developer.nvidia.com/blog/pruning-and-distilling-llms-using-nvidia-tensorrt-model-optimizer/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_046"]
content_length: 10200
---

# Pruning and Distilling LLMs Using NVIDIA TensorRT Model Optimizer

Large language models (LLMs) have set a high bar in natural language processing tasks such as coding, reasoning, and math. However, their deployment remains resource-intensive, motivating a growing interest in small language models (SLMs) that offer strong performance at a fraction of the cost. NVIDIA researchers have demonstrated a method combining structured weight pruning with knowledge distillation, a powerful strategy for compressing large models into smaller, efficient variants without significant loss in quality.

## What is model pruning?

Pruning is a model optimization technique that leverages the common over-parameterization of neural networks. Pruning systematically identifies and removes unimportant parameters such as weights, neurons, or even layers from a trained model. This can often eliminate large amounts of a model's weights with minimal impact on accuracy, directly translating to a more compact model with accelerated inference speeds and lower computational cost.

### Depth pruning

Depth pruning removes entire layers from the neural network, reducing the overall depth and complexity.

### Width pruning

Width pruning eliminates internal structures such as individual neurons, attention heads, or embedding channels, slimming down the model's width.

### Importance assessment methods

- **Magnitude pruning:** Sets weights with small absolute values close to zero.
- **Activation-based pruning:** Uses a calibration dataset to estimate importance based on activations.
- **Structural pruning:** Removes entire structures, like layers or attention heads.

Research shows that width pruning typically achieves better accuracy than depth pruning, though depth pruning often reduces inference latency more at the same number of parameters. The choice depends on desired balance between accuracy and latency.

## What is knowledge distillation?

Knowledge distillation is a model compression technique that transfers knowledge from a larger "teacher" model to a smaller and more efficient "student" model. The goal is to create a compact model that retains the high performance of the larger model.

### Response-based knowledge distillation

Transfers a teacher model's knowledge to a student by training the student to match the teacher's soft output probabilities rather than only hard labels. These soft targets convey inter-class similarities. The student is optimized to align with them using KL divergence.

### Feature-based knowledge distillation

Transfers a teacher's intermediate representations (hidden activations or feature maps) to guide a student toward learning similar internal structure, not just similar outputs. During training, selected teacher and student layers are paired and aligned.

## How to prune a model using TensorRT Model Optimizer

### Depth pruning example

Trimming the Qwen3 8B model from 36 to 24 layers (about 6B parameters) by automatically selecting the best 24 layers using a small calibration dataset of 1,024 samples:

```
torchrun --nproc_per_node 2 /opt/NeMo/scripts/llm/gpt_prune.py \
  --devices 2 --pp_size 2 \
  --restore_path Qwen3-8B-nemo \
  --save_path Qwen3-8B-nemo-depth-pruned \
  --seq_length 4096 --num_train_samples 1024 --mbs 4 \
  --data_paths wikitext-data/wikitext-train_text_document \
  --target_num_layers 24
```

### Width pruning example

Shrinking key architectural components: MLP intermediate (ffn_hidden_size) reduced from 12,288 to 9,216, and Embedding (hidden_size) from 4,096 to 3,584, resulting in a 6B model:

```
torchrun --nproc_per_node 2 /opt/NeMo/scripts/llm/gpt_prune.py \
  --devices 2 --pp_size 2 \
  --restore_path Qwen3-8B-nemo \
  --save_path Qwen3-8B-nemo-width-pruned \
  --seq_length 4096 --num_train_samples 1024 --mbs 4 \
  --data_paths wikitext-data/wikitext-train_text_document \
  --target_ffn_hidden_size 9216 --target_hidden_size 3584
```

## How to use TensorRT Model Optimizer for distillation

Distilling from teacher to depth-pruned model using single-node eight-GPU Tensor Parallel:

```
torchrun --nproc_per_node 8 /opt/NeMo/scripts/llm/gpt_train.py \
  --name Qwen3-8B-nemo-depth-pruned-distill \
  --devices 8 --num_nodes 1 --tp_size 8 \
  --model_path Qwen3-8B-nemo-depth-pruned \
  --teacher_path Qwen3-8B-nemo \
  --max_steps 40 --warmup_steps 1 --gbs 768 --mbs 8 \
  --lr 1e-4 --min_lr 1e-5 --seq_length 4096
```

## Performance results

The Qwen3 Depth Pruned 6B model is 30% faster than the Qwen3 4B model, and also performs better on MMLU benchmark (72.5 versus 70.0). All models quantized to FP8 precision and run with TensorRT-LLM.

The pruned model was distilled from Qwen3-8B using the ClimbMix dataset (~90B tokens, 25% of data). Distillation takes 8 hours with 96 nodes x 8 H100 GPUs (6K GPU hours).

## Key takeaway

Pruning and knowledge distillation are highly cost-effective methods to progressively shrink LLMs while matching or exceeding baseline accuracy across domains. They're typically more data-efficient than either synthetic-data fine-tuning or full pretraining.
