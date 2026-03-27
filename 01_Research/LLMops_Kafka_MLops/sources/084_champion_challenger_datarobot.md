---
source_id: 084
title: "Introducing MLOps Champion/Challenger Models"
url: "https://www.datarobot.com/blog/introducing-mlops-champion-challenger-models/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_027", "kw_006"]
content_length: 6500
---

# Introducing MLOps Champion/Challenger Models

By DataRobot

Let's suppose you have a number of machine learning models running in your production environment. Perhaps you are using DataRobot to help you with this effort. Perhaps you are doing it using your own custom-built method. Let's also suppose that you are monitoring those models using metrics that help you understand their service health, accuracy, and so on.

First of all, congratulations. You are among the elite 10% of organizations that have actually managed to get this far. The other 90% are still trying to figure out how to get their first model into production and haven't even started to think about how to monitor them.

For the elite 10%, what do you do when your monitoring system tells you, perhaps after a month or two, that a model is deteriorating in terms of accuracy and performance?

If this happens to your model, you have a few options at hand:

1. Replace the deteriorating model with a new one
2. Retrain the deteriorating model
3. Rollback to an earlier version of the model

Regardless of which option you choose, the risk of simply replacing a model that is currently running in production with another model or version is simply bad practice.

## So, Why Is This?

Essentially, regardless of how much you train or test a model in your lab environment, the results will still merely represent just an estimation of your model's behavior once it crosses over to your actual production environment.

## What Is the Best Way to Address Model Deterioration?

There are several ways to conduct these important model management activities correctly. Most of them can be characterized as "champion/challenger" best practices.

Champion/challenger is a method that allows different approaches to testing predictive models in a production environment. It's a similar concept to A/B testing from a marketing perspective. The champion/challenger technique enables you to both monitor and measure predictions using different variations of the same decision logic. The overall goal is to identify which variation is the most successful.

In a nutshell, we allow for the original model (the champion) and the new or re-trained models (challengers) to shadow the champion model. The challengers will compete against each other for a chance to become the new champion. The results of this production-based competition can then be reviewed, and the MLOps engineer can make a recommendation as to which of the models is the winner (i.e., the existing champion or one of the challengers).

If this process is performed within a governed system, at this point a designated approver will route her final decision to which model will actually become the new standard (i.e., the new champion).

In addition to understanding the champion/challenger process, it is also important to understand that this is a cyclical process. This means that the activity takes place (or should be taking place) practically all the time, across all production models that are running. This enables a "hot-swap" of models to be undertaken at any given moment, as opposed to waiting for an answer or for testing to complete.

## Champion/Challengers Are New to MLOps 6.1

In the latest 6.1 release of DataRobot, a champion/challenger framework was added to the MLOps product. This new capability enables DataRobot customers, within a governed framework, to run their challenger models in shadow mode, alongside their current best performing model.

Furthermore, DataRobot's Automated Machine Learning product lets you easily and constantly build high-quality alternative models as potential challengers. You can select a DataRobot model or a custom model as a champion, then pick up to three challenger models to shadow it.

A key difference with champion/challengers in DataRobot's MLOps platform is that only one model is ever live at any one time. One hundred percent of prediction requests are serviced by the current champion model. Later on, the same prediction requests are replayed against the challengers for analytical purposes.

This is an important distinction from A/B testing or multi-armed bandit approaches, where you are actually splitting the traffic between different models. A/B testing lets you gradually test out a new model and it lets you get better experimental results on the impact to your KPIs of the different models. However, the major drawback of this approach for many organizations is that applications are randomly getting predictions from different models.

This means the model variants you are testing need to be acceptable for production (in terms of feature usage, accuracy, and so on). With A/B testing, you cannot compare a maximum accuracy insurance pricing model because you are often prohibited from putting that challenger model into a production environment.

DataRobot's shadowing approach lets you safely mirror before taking an approach that impacts your business or your customers. This safety net means you can be more exploratory in the types of models you wish to compare.

By feeding the challenger models with the same production data as the champion model, they are activated in parallel, allowing you to compare the champion predictions that actually fed the live business process, to those of the challenger models. You can then further analyze predictions, accuracy, and data errors over time and zoom in on any period in the past.

In addition, this process is tightly governed by MLOps by providing strict approval workflows and audit trails, so that only those who are authorized can propose and analyze challenger models or replace the current champion.

MLOps champion/challengers allow you to see what you are leaving on the table in terms of production model options, and to always have a fallback model available. This enables you to react to constantly changing business conditions in order to maintain the highest possible model quality over time.
