---
source_id: "056"
title: "Dify Helm Chart - Dify Enterprise Docs"
url: "https://enterprise-docs.dify.ai/en-us/deployment/advanced-configuration/dify-helm-chart"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify Kubernetes deployment", "Dify Helm chart", "Dify self-hosting"]
content_length: 1580
---

# Dify Helm Chart - Dify Enterprise Docs

## Requirements

- Kubernetes 1.24+
- Helm 3.14+
- Warning: If you are using a restricted environment (like OpenShift), make sure pods are allowed to run as root.

## Quick Start

### Helm Chart Repository

Add the Dify Helm chart repository:

```bash
helm repo add dify https://langgenius.github.io/dify-helm
```

### Installation or Upgrade

For the first time installation or upgrade:

```bash
helm repo update
helm search repo dify/dify
helm upgrade -i dify -f values.yaml dify/dify
```

## Advanced Usage

### Uninstallation

```bash
helm uninstall dify
```

### Display Helm Chart Values

```bash
helm show values dify/dify
```

### Use Helm Template to Generate Kubernetes YAML

```bash
helm template dify -f values.yaml dify/dify > dify-k8s-template.yaml
```

### Download the Helm Chart Locally

```bash
helm pull dify/dify
helm pull dify/dify --version x.x.x
```

## Enterprise Edition Features

Dify Enterprise is built for Kubernetes and supports official Helm chart deployment, giving organizations the flexibility to run Dify on their own cloud infrastructure or in on-premise environments, meeting strict compliance, data residency, and regulatory requirements.

Key enterprise features:
- Robust multi-tenant management
- Seamless SSO integration (SAML, OIDC, OAuth2)
- Centralized access control
- Two-step verification and MFA support
- Dedicated priority support with private support channels
- Add-on paid options for consulting services, custom development, and negotiated SLAs

Enterprise customers can deploy via AWS Marketplace, Microsoft Marketplace, or direct licensing.
