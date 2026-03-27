---
source_id: 088
title: "Which test is the best? We compared 5 methods to detect data drift on large datasets"
url: "https://www.evidentlyai.com/blog/data-drift-detection-large-datasets"
type: web
scraped_at: 2026-03-27
keywords: ["kw_020", "kw_006"]
content_length: 25000
---

# Which test is the best? We compared 5 methods to detect data drift on large datasets

By Olga Filippova, Dasha Maliugina | Evidently AI | Published: June 20, 2022 | Last updated: July 16, 2025

TL;DR: We compared five different statistical tests for drift detection on large datasets. Our goal was to build intuition on how the tests react to data changes of varying magnitude.

When machine learning systems are running in production, it's important to check if the input data is changing over time. This is called data drift, and spotting it early helps make sure the model still operates in a familiar environment. Data and prediction drift analysis are important components of ML model monitoring.

One way to detect drift is by using statistical tests to compare new data to past data. But choosing a correct test is not an easy task.

Depending on your use case, you might care a lot about tiny changes (like in critical systems), or you might only want to catch major shifts. The size of your dataset also matters: with large datasets, even tiny differences can look statistically significant, though they might not matter in practice.

## Too much data, too much drift

Each statistical test has particular properties and in-built assumptions.

Let's take a two-sample Kolmogorov-Smirnov (KS) test. It is often a default choice for detecting a distributional change in numerical features. While it does the job in many cases, the test can be "too sensitive" for larger datasets. It would fire alarms for many real-world use cases all the time, just because you have a lot of data and small changes add up.

## Picking the drift metric

We ran experiments comparing five popular statistical tests to understand how they behave:

1. Kolmogorov-Smirnov test
2. Population Stability Index (PSI)
3. Wasserstein distance (Earth-Mover distance)
4. Kullback-Leibler divergence
5. Jensen-Shannon distance

## Experiment design

We picked three features with different characteristics:
- Feature 1: a continuous feature with non-normal distribution ("Multimodal feature")
- Feature 2: a variable with a heavy right tail ("Right-tailed feature")
- Feature 3: "Feature with outliers"

We implemented a function to imitate data drift by shifting the whole distribution for each feature by a fixed value: (alpha + mean(feature)) * perc

We tested three questions for each statistical test:
1. How does the sample size influence the test results?
2. How does the magnitude of data change influence the test results?
3. Is the test sensitive to a change in the data segment?

## Results: Kolmogorov-Smirnov (KS) test

The KS test is a nonparametric statistical test. The null hypothesis is that the two samples come from the same distribution. It returns a p-value; if the p-value is less than 0.05, you can usually declare the two samples different.

Key findings:
- The KS test tends to be pretty sensitive in larger datasets. It raises flags even for a minor change of 0.5%, as soon as we have more than 100,000 objects.
- For a fixed sample size of 100,000, the p-value is close to zero for dataset drift as small as 1%.
- KS is sensitive to a change in the 20%-data segment as well. The p-value approaches zero for data drift of 5% and above.

Recommendation: Use KS if you have fewer observations (under 1000) or when you expect data to be stable and want to react even to slight deviations. For larger datasets, consider sampling before applying KS.

## Results: Population Stability Index (PSI)

PSI returns a number from 0 and above. Common interpretation:
- PSI < 0.1: no significant population change
- 0.1 <= PSI < 0.2: moderate population change
- PSI >= 0.2: significant population change

Key findings:
- For a minor change of 0.5%, the sample size has a low effect on the PSI value.
- PSI only starts detecting significant change for a drift size larger than 10%.
- For segment drift, PSI has the chance of detecting only major changes (100%-shift in data segment).
- PSI has low sensitivity but returns consistent results regardless of sample size.

Recommendation: Use PSI in industries familiar with the approach. Good for large datasets where you only want to react to major changes.

## Results: Kullback-Leibler divergence (KL)

KL divergence returns a score from 0 to infinity. A score of 0 means identical distributions. Unlike PSI, KL is not symmetric.

Key findings:
- Behavior is very similar to PSI. Low sensitivity for minor data changes.
- Results are consistent regardless of sample size.
- Good default test for larger datasets, but keep asymmetry in mind.

## Results: Jensen-Shannon divergence

JS divergence returns a score between 0 and 1. It is symmetric and always finite (unlike KL).

Key findings:
- Low sensitivity for minor changes (0.5%).
- Becomes more sensitive when drift exceeds 10% for 100,000 observations.
- Barely detects drift in 20%-segment of data.
- Stable behavior for large datasets. Slightly more sensitive than KL and PSI.

## Results: Wasserstein distance (Earth-Mover Distance)

WD measures how much effort it takes to turn one distribution into another. When normalized by standard deviation, the metric shows the number of standard deviations you should move each object of the current group to match the reference group.

Key findings:
- When sample size is "small," WD tends to overestimate the effect, but much less than KS.
- Becomes sustainable for samples of more than 100,000.
- More sensitive than PSI but less "trigger-happy" than KS.
- A good compromise between KS and PSI.

Recommendation: Set a threshold based on standard deviations you consider significant. 0.1 = change of 0.1 standard deviations qualifies as drift.

## Real-world data examples

Six real-world examples demonstrated:
- Example 1: Huge change, all tests agree.
- Example 2: Minor change, only KS reacts (too sensitive).
- Example 3: Trend change, PSI detects but WD does not (PSI sensitive to new values).
- Example 4: Obvious drift, all agree.
- Example 5: Sudden spike, all detect except KL.
- Example 6: Ambiguous drift, tests disagree.

## Summary and heuristics

There is no "perfect" test. Consider:

**The size of drift you want to detect.** In some cases, react only to large changes; in others, even minor ones.

**The size of samples you will compare.** Different tests give different results depending on sample size.

**The cost of model performance drop.** If every mistake is expensive, pick a more sensitive test.

Heuristics:
- **If accuracy is key, pick KS.** Control sample size to avoid over-sensitivity.
- **If you want reasonable drift detection, pick WD.** Set threshold in standard deviations.
- **If you are used to PSI, go for it.** Good for features where fluctuation is normal.
- **If you care about data segments, monitor them separately.** No test is perfect for segment-level drift.

Always experiment on your own data and iterate based on production monitoring results.

## Implementation

You can use Evidently, an open-source Python library, which has an in-built algorithm that selects a suitable drift test based on feature type, number of observations, and unique values.
