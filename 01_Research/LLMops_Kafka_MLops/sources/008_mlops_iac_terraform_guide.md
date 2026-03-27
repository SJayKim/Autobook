---
source_id: 008
title: "A Comprehensive Guide to MLOps Terraform: Infrastructure As Code (IaC)"
url: "https://betterprogramming.pub/a-comprehensive-guide-to-mlops-infrastructure-as-code-iac-ef4c97742351"
type: web
scraped_at: 2026-03-27
keywords: ["kw_047"]
content_length: 5500
---

# A Comprehensive Guide to MLOps Terraform: Infrastructure As Code (IaC)

## What is Infrastructure As Code (IaC)

Infrastructure as Code (IaC) is the management of infrastructure (networks, virtual machines, load balancers, connection topology) in a descriptive model, using the same versioning as DevOps team uses for source code. An IaC model generates the same environment every time it is applied. IaC is a key DevOps practice used in conjunction with continuous delivery.

In simple terms, you provision the infrastructure by writing code instead of provisioning it manually.

## Advantages of Using IaC

- Speed, Cost reduction, Repeatability, Standardization
- Scalability, Consistency, Automation (avoid manual intervention)
- Reliability, Version management (GitOps), Security
- Documentation, Faster disaster recovery, CI/CD Integration

## Imperative vs. Declarative

- **Imperative Approach**: Developer defines exact steps to be carried out
- **Declarative Approach**: Developer defines required end state; platform handles steps needed. Terraform uses declarative approach.

## Major Players in IaC

Terraform, Ansible, AWS CloudFormation, Google Cloud Deployment Manager, Azure Resource Manager, Puppet, SaltStack, Chef

## Terraform

- IaC tool by HashiCorp, written in Golang, open-source
- Cloud agnostic -- works with any cloud provider (AWS, GCP, Azure, OCI)
- Works with provider APIs -- 1781+ providers
- Uses declarative approach with HashiCorp Configuration Language (HCL)
- Creates state file to track infrastructure

### How Terraform Works
Developer creates configuration file (desired state). Terraform creates resources and state file. When config changes, Terraform compares config with state file and applies only the differences. Similar to Kubernetes replica management.

### Key Advantage
Can create infrastructure in multiple cloud providers with one configuration file (unlike CloudFormation which is AWS-only).

## Terraform for GCP ML Projects

Example provisions:
- Google Cloud Storage bucket
- Notebook instance for ML training
- Required API enablement
- Service accounts for Vertex Training and Vertex Pipelines
- GKE cluster for ML App deployment

## File Structure

- `main.tf`: provider information, locals, module, resource definitions
- `variables.tf`: variable declarations (inputs/parameters)
- `terraform.tfvars`: variable values
- `gcs-bucket.tf`, `gke.tf`, `notebook-instance.tf`, `service-accounts.tf`, `services.tf`: separate resource files

Terraform loads all .tf files in directory alphabetically.

## Core Concepts

### Variables
- Declared with `variable` keyword, support types: string, number, bool, list, set, tuple, map, object, any
- Referenced as `var.<variable_identifier>`
- Set via environment variables, command-line flags, .tfvars files, or variable defaults

### Data Sources
Allow Terraform to use information available outside current project. Defined by `data` block.

### Outputs
Show data from Terraform state file after activities are completed.

### Locals
Defined once, used multiple times. Can reference other expressions.

### Modules
Organize code for reuse. Can use from external vendors (AWS, GitHub) or local folders. Pass arguments, use Output to pass values.

## Terraform Workflow

1. **terraform init**: Downloads all plugins associated with the provider
2. **terraform validate**: Validates configuration files (undeclared variables, duplicate resources, etc.)
3. **terraform plan**: Creates execution plan previewing changes; compares current config to prior state
4. **terraform apply**: Executes proposed actions; creates state file (terraform.tfstate)
5. **terraform destroy**: Destroys created resources (all or targeted with -target flag)

## State File

terraform.tfstate stores all resources created by Terraform. Maintains dependency relationships. Backup in terraform.tfstate.backup. Used during plan, apply, and destroy.
