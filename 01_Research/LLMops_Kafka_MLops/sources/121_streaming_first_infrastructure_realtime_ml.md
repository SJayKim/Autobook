---
source_id: 121
title: "Streaming-First Infrastructure for Real-Time Machine Learning"
url: "https://www.infoq.com/articles/streaming-first-real-time-ml/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_025"]
content_length: 12000
---

# Streaming-First Infrastructure for Real-Time Machine Learning

By Chip Huyen (co-founder of Claypot AI, Stanford CS 329S instructor, author of Designing Machine Learning Systems). Published Aug 22, 2022 on InfoQ.

### Key Takeaways

- A streaming infrastructure can improve ML prediction latency and continual learning
- Batch processing on static data is a subset of processing streaming data, so a streaming system can be used for both cases
- Avoid common production problems by using a single streaming pipeline for online prediction and continual learning
- An event-driven microservices architecture is a better choice for using continual learning than is a REST-based architecture
- To know if continual learning is right for you, you should quantify the value of data freshness and fast iteration

Many companies have begun using machine learning (ML) models to improve their customer experience. This article covers the benefits of streaming-first infrastructure for two scenarios of real-time ML: online prediction, where a model can receive a request and make predictions as soon as the request arrives, and continual learning, when machine learning models are capable of continually adapting to change in data distributions in production.

## Online Prediction

Online prediction is pretty straightforward to deploy. If you have developed a model, the easiest way to deploy is to containerize it, then upload it to a platform like AWS or GCP to create an online prediction web service endpoint. If you send data to that endpoint, you can get predictions for this data.

The problem with online predictions is latency. Research shows that no matter how good your model predictions are, if it takes even a few milliseconds too long to return results, users will leave your site or click on something else. A common trend in ML is toward bigger models. These give better accuracy, but it generally also means that inference takes longer, and users don't want to wait.

How do you make online prediction work? You actually need two components. The first is a model that is capable of returning fast inference. One solution is to use model compression techniques such as quantization and distillation. You could also use more powerful hardware. However, the solution I recommend is to use a real-time pipeline -- a pipeline that can process data, input the data into the model, and generate predictions and return predictions in real time to users.

## Real-Time Transport and Stream Processing

The solution is to use in-memory storage. When you have incoming events - a user books a trip, picks a location, cancels trip, contacts the driver - then you put all the events into in-memory storage, and then you keep them there for as long as those events are useful for real-time purposes. At some point, say after a few days, you can either discard those events or move them to permanent storage, such as AWS S3.

The in-memory storage is generally what is called real-time transport, based on a system such as Kafka, Kinesis, or Pulsar. Because these platforms are event-based, this kind of processing is called event-driven processing.

Static data is often stored in a file format like CSV or Parquet and processed using a batch-processing system such as Hadoop. Because static data is bounded, when each data sample has been processed, you know the job is complete. By contrast, streaming data is usually accessed through a real-time transport platform like Kafka or Kinesis and handled using a stream-processing tool such as Flink or Samza. Because the data is unbounded, processing is never complete.

## One Model, Two Pipelines

The problem with separating data into batch processing and stream processing, is that now you have two different pipelines for one ML model. First, training a model uses static data and batch processing to generate features. During inference, however, you do online predictions with streaming data and stream processing to extract features.

This mismatch is a very common source for errors in production when a change in one pipeline isn't replicated in the pipeline. The solution is to unify the batch and stream processing by using a streaming-first infrastructure. The key insight is that batch processing is a special case of streaming processing, because a bounded dataset is actually a special case of the unbounded data from streaming.

## Request-Driven to Event-Driven Architecture

In the domain of microservices, a concept related to event-driven processing is event-driven architecture, as opposed to request-driven architecture. In request-driven architecture, there is an interaction of a client and server via REST API. This is a synchronous operation.

Instead of having request-driven communications, an alternative is an event-driven architecture. Instead of services communicating directly with each other, there is a central event stream. Whenever a service wants to publish something, it pushes that information onto the stream. Other services listen to the stream.

There are several advantages to this event-driven architecture. First, it reduces the need for inter-service communications. Another is that because all the data transformation is now in the stream, you can just query the stream and understand how a piece of data is transformed by different services through the entire system.

## From Monitoring to Continual Learning

Model performance degrades in production. There are many different reasons, but one key reason is data distribution shifts. Things change in the real world. The changes can be sudden - due to a pandemic, perhaps - or they can be cyclical. For example, ride sharing demand is probably different on the weekend compared to workdays. The change can also be gradual.

Monitoring helps you detect changing data distributions, but it's a very shallow solution. What you really want is continual learning -- to continually adapt models to changing data distributions.

When people hear continual learning, they think about the case where you have to update the models with every incoming sample. This has several drawbacks. Models could suffer from catastrophic forgetting. It can get unnecessarily expensive. A better strategy is to update models with micro-batches of 500 or 1000 samples.

## Iteration Cycle

With continual learning, you actually don't update the production model. Instead, you create a replica of that model, and then update that replica, which now becomes a candidate model. You only want to deploy that candidate model production after it has been evaluated.

First, you use a static data test set to do offline evaluation ("smoke test"). You also need to do online evaluation, because the whole point of continual learning is to adapt a model to change in distributions. There are a lot of ways to do it safely: through A/B testing, canary analysis, and multi-armed bandits.

For continual learning, the iteration cycles can be done in order of minutes. For example, Weibo has an iteration cycle of around 10 minutes. You can see similar examples with Alibaba, TikTok, and Shein. This speed is remarkable, given that 64% of companies have cycles of a month or longer.

## Continual Learning: Use Cases

Continual learning allows a model to adapt to rare events very quickly. For example, Black Friday happens only once a year, so there's no way you can have enough historical information to accurately predict behavior. For the best performance you would continually train the model during the event. Singles' Day in China is one of the use cases where Alibaba is using continual learning.

Continual learning also helps overcome the continuous cold start problem. If you can update your model during sessions, then you can learn what users want even without historical data. TikTok is very successful because they use continual learning to adapt to users' preference within a session.

Continual learning is especially good for tasks with natural labels, such as recommendation systems. Short feedback loops (on order of minutes) are applicable to online content like short videos, Reddit posts, or Tweets.

## Is Continual Learning Right for You?

You have to quantify the value of data freshness. Back in 2014, Facebook found that switching from training weekly to daily increased their click-through rate by 1%, which was significant enough to change the pipeline.

You should also quantify the value of fast iterations. The more experiments you can run, the more likely you are to find models that work better for you.

Regarding cloud cost: In batch learning, retraining takes longer since you retrain from scratch. In continual learning, you just continue training on fresh data, requiring less data and fewer compute resources. Grubhub saw a 45x savings on training compute cost when switching from monthly to daily training, while achieving more than 20% increase in evaluation metrics.
