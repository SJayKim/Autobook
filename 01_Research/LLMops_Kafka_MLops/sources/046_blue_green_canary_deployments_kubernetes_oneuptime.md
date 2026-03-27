---
source_id: 046
title: "How to Implement Blue-Green and Canary Deployments in Kubernetes"
url: "https://oneuptime.com/blog/post/2026-01-19-kubernetes-blue-green-canary-deployments/view"
type: web
scraped_at: 2026-03-27
keywords: ["kw_019", "kw_030"]
content_length: 9200
---

# How to Implement Blue-Green and Canary Deployments in Kubernetes

Blue-green and canary deployments are progressive delivery strategies that minimize deployment risk by gradually shifting traffic to new versions.

## Deployment Strategies Overview

| Strategy | Risk | Rollback Speed | Resource Usage |
|----------|------|----------------|----------------|
| Blue-Green | Low | Instant | 2x during deployment |
| Canary | Very Low | Fast | 1.1x during deployment |
| Rolling Update | Medium | Slow | 1.2x during deployment |

## Blue-Green Deployment

### Manual Blue-Green with Services

Maintain two deployments (blue and green) with different version labels. A single Service points to the active version via label selector. Switching traffic is done by patching the Service selector from "blue" to "green".

Key YAML pattern: two Deployment resources (myapp-blue with image:v1.0.0, myapp-green with image:v2.0.0) and one Service that selects version: blue (or green after switch).

### Blue-Green Switch Script

Bash script that: checks current active version, verifies new deployment readiness (readyReplicas == spec.replicas), patches the Service selector.

### Blue-Green with Ingress

Create a preview Ingress pointing to green deployment at preview.myapp.example.com for testing before switching the main Ingress.

## Canary Deployment

### Manual Canary with Replica Ratios

Use two Deployments (stable: 9 replicas, canary: 1 replica) both matching the same Service selector (app: myapp). Service routes to both based on label match, achieving approximately 10% traffic to canary.

### Canary with NGINX Ingress

Use NGINX Ingress annotations:
- nginx.ingress.kubernetes.io/canary: "true"
- nginx.ingress.kubernetes.io/canary-weight: "10" (10% to canary)

### Header-Based Canary Routing

Route specific users to canary using:
- nginx.ingress.kubernetes.io/canary-by-header: "X-Canary"
- nginx.ingress.kubernetes.io/canary-by-header-value: "true"

## Argo Rollouts

### Blue-Green Rollout

Argo Rollouts provides a Rollout CRD with blueGreen strategy. Features: activeService, previewService, autoPromotionEnabled with configurable autoPromotionSeconds, scaleDownDelaySeconds for previous version.

### Canary Rollout

Canary steps with progressive traffic shifting:
- Step 1: 10% traffic, pause 5m
- Step 2: 25% traffic, pause 5m
- Step 3: 50% traffic, pause 5m
- Step 4: 75% traffic, pause 5m
- Step 5: 100% traffic

### Canary with Analysis

AnalysisTemplate CRD integrates with Prometheus for automated canary analysis:
- success-rate metric: query Prometheus for HTTP 2xx ratio, successCondition >= 0.95
- latency-check metric: query Prometheus for p99 latency, successCondition < 500ms
- failureLimit: 3 (max failed measurements before rollback)

## Flagger for Automated Canary

Install Flagger with NGINX support via Helm. Flagger Canary resource configures:
- targetRef: existing Deployment
- ingressRef: existing Ingress
- analysis: interval 1m, maxWeight 50, stepWeight 10
- metrics: request-success-rate (min 99%), request-duration (max 500ms)
- webhooks for automated load testing

## Monitoring Deployments

PromQL queries:
- Canary vs Stable error rates: sum(rate(http_requests_total{status=~"5..",deployment="canary"}[5m])) / sum(rate(http_requests_total{deployment="canary"}[5m]))
- Latency comparison: histogram_quantile(0.99, ...) by (deployment, le)
- Request rate by deployment: sum(rate(http_requests_total[5m])) by (deployment)

Rollout management:
- kubectl argo rollouts status myapp
- kubectl argo rollouts promote myapp (manual promote)
- kubectl argo rollouts abort myapp (rollback)

## Best Practices

1. Always have readiness probes (initialDelaySeconds: 5, periodSeconds: 5, failureThreshold: 3)
2. Use meaningful analysis metrics (error-rate < 1%, latency-p99 < 500ms, CPU saturation < 80%)
3. Configure appropriate timeouts (pause duration: enough time to detect issues)

## Key Takeaways

1. Blue-green for instant rollback -- double resources, instant switch
2. Canary for gradual rollout -- lower risk, early detection
3. Automate with Argo Rollouts or Flagger -- metrics-driven promotion
4. Monitor throughout -- track error rates and latency
5. Have rollback ready -- know how to abort quickly
