---
source_id: 082
title: "The What, Why, and How of A/B Testing in Machine Learning"
url: "https://mlops.community/the-what-why-and-how-of-a-b-testing-in-ml/"
type: web
scraped_at: 2026-03-27
keywords: ["kw_027", "kw_041"]
content_length: 12500
---

# The What, Why, and How of A/B Testing in Machine Learning

By Demetrios Brinkmann, MLOps Community

A/B tests are a key tool of business decision-making. In this article, we'll discuss the what and why of A/B testing, how an A/B test is designed, and how to easily set them up in production.

An A/B test, also called a controlled experiment or a randomized control trial, is a statistical method of determining which of a set of variants is the best. A/B tests allow organizations and policy-makers to make smarter, data-driven decisions that are less dependent on guesswork.

In the simplest version of an A/B test, subjects are randomly assigned to either the control group (group A) or the treatment group (group B). Subjects in the treatment group receive the treatment (such as a new medicine, a special offer, or a new web page design) while the control group proceeds as normal without the treatment. Data is then collected on the outcomes and used to study the effects of the treatment.

In data science, A/B tests can also be used to choose between two models in production, by measuring which model performs better in the real world. In this formulation, the control is often an existing model that is currently in production, sometimes called the **champion**. The treatment is a new model being considered to replace the old one. This new model is sometimes called the **challenger**. In our discussion, we'll use the terms champion and challenger, rather than control and treatment.

## Designing a Machine Learning A/B Test

A/B tests are a useful way to rely less on opinions and intuition and to be more data-driven in decision-making, but there are a few principles to keep in mind. The experimenter has to decide on a number of things.

**First, decide what you are trying to measure.** We'll call this the Overall Evaluation Criterion or OEC. This may be different and more business-focused than the loss function used while training the models, but it must be something you can measure. Common examples are revenue, click-thru rate, conversion rate, or process completion rate.

**Second, decide how much better is "better".** You might want to just say "Success is when the challenger is better than the champion," but that's actually not a testable question, at least not in the statistical sense. You have to decide how much better the challenger has to be. Let's define two quantities:

- **y0**: The champion's assumed OEC. Since the champion has been running for a while, we should have a good idea of this value. For example, if we are measuring conversion rate, then we might already know that the champion typically achieves a conversion rate of y0 = 2%.

- **delta**: the minimum delta effect size we want to reliably detect. This is how much better the challenger needs to be for us to declare it "the winner." For example, we may decide to switch to our challenger model if it improves the conversion rate by at least 1% -- that is, we want the challenger to have a conversion rate of at least 0.02 * (1.01) = 0.0202. This means delta = 0.002.

**Third, decide how much error you want to tolerate**. The less error you can tolerate, the more data you need, and in an online setting, the longer you have to run the test. In the classical statistics formulation, an A/B test has the following parameters:

- **alpha**: the significance, or false positive rate that we are willing to tolerate. Ideally, we want alpha as small as possible; in practice, alpha is usually set to 0.05.

- **beta**: the power, or true positive rate we want to achieve. Ideally, we would like beta near 1; in practice, beta is usually set to 0.8.

- **n**: the minimum number of examples (per model) we have to examine to make sure our false positive rate alpha and true positive rate beta thresholds are met.

Note that n is per model: so if you are routing your customers between A and B with a 50-50 split, you need a total experiment size of 2*n customers. A 50-50 split is the most efficient.

To run an A/B test, the experimenter picks alpha, beta, and the minimum effect size delta, and then determines n. Power calculators or sample-size calculators exist to do that for you.

## Some Practical Considerations

**Splitting your subjects:** When splitting your subjects up randomly between models, make sure the process is truly random, and think through any interference between the two groups. Also, make sure the assignment is consistent so that each subject always gets the same treatment.

**A/A Tests:** It can be a good idea to run an A/A test, where both groups are control or treatment groups. This can help surface unintentional biases or errors in the processing.

**Don't Peek!:** Due to human nature, it's difficult not to peek at the results early and draw conclusions or stop the experiment before the minimum sample size is reached. Resist the temptation.

**The more sensitive a test is, the longer it will take:** The resolution of an A/B test increases as the square of the samples. If you want to halve the delta effect size you can detect, you have to quadruple your sample size.

## Extensions to A/B Testing

### Bayesian A/B Tests

The classical (frequentist) statistical approach to A/B testing can be a bit unintuitive. The Bayesian approach takes the data from a single run as a given, and asks, "What OEC values are consistent with what I've observed?"

The general steps for a Bayesian analysis are roughly:

1. Specify prior beliefs about possible values of the OEC for the experiment groups.
2. Define a statistical model using a Bayesian analysis tool and flat, uninformative, or equal priors for each group.
3. Collect data and update the beliefs on possible values for the OEC parameters as you go.
4. Continue the experiment as long as it seems valuable to refine the estimates.

A Bayesian approach does not necessarily make the test any shorter; it simply makes quantifying the uncertainties more straightforward and arguably more intuitive.

### Multi-Armed Bandits

If you want to minimize the waiting until the end of an experiment before taking action, consider Multi-Armed Bandit approaches. Multi-armed bandits dynamically adjust the percentage of new requests that go to each option, based on that option's past performance. Essentially, the better performing a model is, the more traffic it gets -- but some small amount of traffic still goes to poorly performing models, so the experiment can still collect information about them. This balances the trade-off between exploitation (extracting maximal value by using models that appear to be the best) and exploration (collecting information about other models, in case they turn out to be better).

## A/B Testing in Production

The Wallaroo ML deployment platform provides specialized pipeline configurations for setting up production experiments, including A/B tests. All the models in an experimentation pipeline receive data via the same endpoint; the pipeline takes care of allocating the requests to each of the models as desired.

Requests can be allocated in a number of ways. For an A/B test, you would use random split. In this allocation scheme, requests are distributed randomly in the proportions you specify: 50-50, 80-20, or whatever is appropriate.

### Other Types of Experiments

**Key split**: requests are distributed according to the value of a key, or query attribute. For example, gold card customers might be routed to model A, platinum cardholders to model B.

**Shadow deployments**: all the models in the experiment pipeline get all the data, and all inferences are logged. However, the pipeline only outputs the inferences from one model -- the default, or champion model. Shadow deployments are useful for "sanity checking" a model before it goes truly live.

A/B tests and other types of experimentation are part of the ML lifecycle. The ability to quickly experiment and test new models in the real world helps data scientists to continually learn, innovate, and improve AI-driven decision processes.
