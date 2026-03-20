# Overview
Rather than fine-tuning all parameters of a model, LoRA updates only a small subset by introducing low-rank matrices into each layer of the Transformer architecture.
-  By freezing the pre-trained model weights and adding trainable rank-decomposition matrices, LoRA significantly decreases the number of trainable parameters required for downstream tasks, making it particularly effective for scenarios with limited computational resources.

![[Pasted image 20260223171058.png]]
- To address the tasks of [[Pathology Prediction]] and [[Differential Diagnosis (DDx)]], we design a sequence classification pipeline by appending additional linear heads to the end of the [[LLaMa-v3]] model.
- Designed a sequence classification pipeline by appending additional linear heads to the end of the [[LLaMA-v3]] model
- The approach focuses on adapting [[LoRA]] specifically for the self-attention modules in each block, leaving the MLP modules unchanged
# See also
- [[LLM Fine-tuning]]
- [[LLaMa-v3]]
- [[Pathology Prediction]]
- [[Differential Diagnosis (DDx)]]
# Source
- https://arxiv.org/abs/2506.19702