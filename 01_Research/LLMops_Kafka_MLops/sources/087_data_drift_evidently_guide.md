---
source_id: 087
title: "What is data drift in ML, and how to detect and handle it"
url: "https://www.evidentlyai.com/ml-in-production/data-drift"
type: web
scraped_at: 2026-03-27
keywords: ["kw_020", "kw_006"]
content_length: 47972
---

# What is data drift in ML, and how to detect and handle it

By Evidently AI | Last updated: January 9, 2025

## What is data drift?

Data drift (also known as feature drift, covariate shift, or distribution shift) refers to the change in the distribution of model input data over time. It occurs when the statistical properties of the production data differ from those of the training data.

Data drift is one of the primary reasons ML models degrade in production. Even if a model was highly accurate during training and validation, changes in real-world data can cause its performance to deteriorate.

## Data drift vs. Concept drift

While data drift refers to changes in input feature distributions (P(X) changes), concept drift refers to changes in the relationship between inputs and outputs (P(Y|X) changes). In other words:

- **Data drift**: The input data looks different, but the underlying relationship between features and target may still hold
- **Concept drift**: The rules of the game have changed -- the same inputs now lead to different outcomes

For example, in a housing price model: data drift might mean more luxury homes entering the market (the distribution of features changes), while concept drift might mean that the same features now predict different prices due to a market crash.

## Data drift vs. Prediction drift

Prediction drift focuses on changes in the model's output distribution. If the distribution of predictions changes significantly, it can signal that something is off -- either in the input data or in the model's behavior.

Prediction drift can be a useful proxy when you cannot directly monitor ground truth, since it reflects changes in model behavior that may indicate performance issues.

## Data drift vs. Training-serving skew

Training-serving skew is a specific type of data drift that occurs due to differences between the training pipeline and the serving pipeline. Common causes include:

- Different data preprocessing logic
- Feature computation differences
- Data freshness issues
- Schema mismatches

## Data drift vs. Data quality

Data quality issues (missing values, incorrect types, out-of-range values) are distinct from drift. Data quality problems are typically bugs or pipeline failures, while drift represents a genuine change in the underlying data distribution.

However, data quality issues can sometimes masquerade as drift or vice versa, so it's important to monitor both.

## Data drift vs. Outlier detection

Outlier detection focuses on identifying individual unusual data points, while drift detection analyzes changes in the overall distribution. A few outliers may not indicate drift, and drift can occur even without extreme outliers.

## Why is data drift important?

### Model maintenance

Data drift is a leading indicator that a model may need retraining. By detecting drift early, teams can proactively update their models before performance degrades significantly.

### Feedback delay

In many applications, ground truth feedback is delayed (e.g., loan default takes months to observe). Drift monitoring provides an early warning signal even before you know whether the model's predictions were correct.

### Model debugging

When model performance drops, drift analysis helps identify which specific features have changed, providing clues about the root cause and guiding remediation efforts.

## How to detect data drift

### Statistical tests

Several statistical tests can be used to compare distributions:

- **Kolmogorov-Smirnov (KS) test**: A nonparametric test comparing two continuous distributions. Very sensitive on large datasets.
- **Chi-squared test**: Compares observed vs. expected frequencies for categorical features.
- **Population Stability Index (PSI)**: Measures distribution change using binned data. Common thresholds: PSI < 0.1 (no change), 0.1-0.2 (moderate), > 0.2 (significant).
- **Wasserstein distance (Earth Mover's Distance)**: Measures the "cost" of transforming one distribution into another. Interpretable when normalized by standard deviation.
- **Jensen-Shannon divergence**: Symmetric measure based on KL divergence, bounded between 0 and 1.
- **Kullback-Leibler (KL) divergence**: Measures how one distribution differs from another. Asymmetric.

### Choosing the right test

The choice of test depends on:

- **Dataset size**: KS is too sensitive for large datasets; PSI and WD are more stable
- **Feature type**: Some tests work only for numerical features, others for categorical
- **Sensitivity needed**: KS detects tiny changes; PSI only detects large shifts
- **Interpretability**: PSI has well-known thresholds; WD can be normalized

### Monitoring approaches

1. **Reference-based comparison**: Compare current data against a fixed reference (e.g., training data)
2. **Window-based comparison**: Compare recent data against a previous time window
3. **Feature-level monitoring**: Track drift for each individual feature
4. **Multivariate monitoring**: Detect changes in feature correlations and joint distributions

## How to handle data drift

When drift is detected, the response depends on the severity and type:

1. **Investigate the cause**: Is it a data quality issue, a pipeline bug, or a genuine distribution shift?
2. **Assess impact**: Is the drift affecting model performance? Check predictions and business metrics.
3. **Decide on action**:
   - **Ignore**: If drift is minor and performance is unaffected
   - **Retrain**: If drift is significant and performance has degraded
   - **Update pipeline**: If drift is caused by data processing issues
   - **Collect new data**: If the drift represents a genuine shift in the problem space

## Tools for drift detection

- **Evidently AI**: Open-source library with 20+ drift detection methods and automatic test selection
- **WhyLabs**: Enterprise platform with real-time drift monitoring
- **NannyML**: Open-source drift detection focused on performance estimation
- **Great Expectations**: Data quality and drift validation
- **Custom implementations**: Using scipy.stats or similar libraries

## Best practices

1. **Monitor continuously**: Set up automated drift checks on a regular schedule
2. **Start with reasonable defaults**: Use automatic test selection if unsure
3. **Set appropriate thresholds**: Too sensitive = too many false alarms; too loose = missed issues
4. **Monitor segments separately**: Drift in a specific segment may be masked in overall metrics
5. **Combine with performance monitoring**: Drift alone doesn't mean the model is broken
6. **Keep historical records**: Track drift over time to understand patterns and trends
