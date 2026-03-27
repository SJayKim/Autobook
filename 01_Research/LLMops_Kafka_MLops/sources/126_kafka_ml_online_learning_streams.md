---
source_id: 126
title: "Online learning and continuous model upgrading with data streams through the Kafka-ML framework"
url: "https://www.sciencedirect.com/science/article/pii/S0167739X24002930"
type: web
scraped_at: 2026-03-27
keywords: ["kw_025", "kw_033"]
content_length: 2800
---

# Online learning and continuous model upgrading with data streams through the Kafka-ML framework

Authors: Alejandro Carnero, Cristian Martin, Gwanggil Jeon, Manuel Diaz.
Published in: Future Generation Computer Systems, Volume 160, November 2024, Pages 251-263.
DOI: 10.1016/j.future.2024.06.001 (Open Access, Creative Commons)

## Highlights

- Online learning with continuous data streams through Kafka-ML.
- Managing and deploying single and distributed models for online training.
- Flexible and automatic deployments for inference according to incremental learning.

## Abstract

A pipeline of constant data streams is being built by the Internet of Things (IoT) to monitor information about the physical environment. In parallel, Artificial Intelligence (AI) is constantly developing and enhancing industrial, economic, and academic endeavors as well as quality of life thanks to these IoT data. In streaming contexts, Kafka-ML is our open-source framework that enables the management of Machine Learning (ML) and AI pipelines over data streams. Accordingly, it simplifies the deployment of Deep Neural Networks (DNNs) in practical applications.

Nonetheless, this framework did not support the possibility of carrying out an Online Learning (OL) process, which is needed when new data are continuously arriving, and the models need to adapt to them on the fly. In this work, we have extended our previous work, the Kafka-ML framework, to enhance the management of ML/AI pipelines with OL features to enable both ML/AI distributed and centralized models to learn indefinitely over time.

These models are continuously upgraded thanks to a process where automatic and flexible inference is carried out when improvements in the model performance are achieved. This opens up a large number of new possibilities within different fields of application, development, and work under the premise of incremental learning with ML models such as Electrical Vehicles and Industry 5.0.

We have validated these new features by adapting and deploying state-of-the-art DNN models in different online scenarios, for both single and distributed configurations. The results show the capability of Kafka-ML to execute effective online training processes for ML models, improving their performance over time as new data becomes available.

## Keywords

Artificial Intelligence, Data streams, Kafka-ML, Online machine learning

## Key Contribution

Kafka-ML extends Apache Kafka with ML pipeline management for streaming contexts. The online learning extension enables models to continuously adapt to new data without stopping inference. The framework handles both centralized and distributed model configurations, with automatic deployment of improved model versions when performance gains are detected.
