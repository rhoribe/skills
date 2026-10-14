# Terraform & OpenTofu Topology Guide

This reference guide explains how `iac-topology` parses Terraform and OpenTofu projects, identifies cloud resource hierarchies, maps network boundaries, and extracts inter-resource dependencies.

---

## 1. Supported Terraform Input Types

`iac-topology` supports two primary methods for inspecting Terraform infrastructure:

1. **Static HCL Configuration Files (`.tf`)**:
   - Parses `resource "type" "name" { ... }` blocks.
   - Parses `module "name" { ... }` blocks.
   - Parses `data "type" "name" { ... }` blocks.
   - Extracts implicit references (`aws_security_group.sg.id`) and explicit dependencies (`depends_on = [...]`).
2. **Terraform Plan & State JSON (`terraform show -json`)**:
   - Standard output from `terraform show -json tfplan.binary` or `terraform state pull`.
   - Ingests `resource_changes` with configuration and applied values.

---

## 2. Resource Categorization & Providers

Resources are classified by provider prefix and functional category:

| Provider | Type Prefix | Examples | Default Palette |
|---|---|---|---|
| **AWS** | `aws_` | `aws_vpc`, `aws_instance`, `aws_db_instance`, `aws_s3_bucket` | Orange / Warm Amber |
| **Azure** | `azurerm_` | `azurerm_virtual_network`, `azurerm_linux_virtual_machine`, `azurerm_mssql_database` | Azure Blue |
| **GCP** | `google_` | `google_compute_network`, `google_compute_instance`, `google_sql_database_instance` | Emerald / Google Blue |
| **Kubernetes** | `kubernetes_` | `kubernetes_deployment`, `kubernetes_service`, `kubernetes_ingress_v1` | Indigo / Navy |

---

## 3. Network Boundary & Container Grouping

Hierarchical groupings are extracted automatically:
- **VPC / VNet Boundary**: Grouped by `vpc_id`, `virtual_network_name`, or the VPC resource itself.
- **Subnet Boundary**: Grouped by `subnet_id` or `subnet_ids`.
- **Azure Resource Groups**: Grouped by `resource_group_name`.

---

## 4. Best Practices for Clear Terraform Diagrams

1. **Use Explicit Module Outputs**: When modularizing infrastructure, pass resource IDs through outputs to preserve edge connections in static parsing.
2. **Tag Resources with Environment/Name**: The parser extracts `tags.Name` or `name` attributes for human-friendly diagram labels.
3. **Generate Plan JSON for Complex Workspaces**: For workspaces heavily reliant on dynamic blocks, counts, or `for_each`, export a plan JSON:
   ```bash
   terraform plan -out=tfplan.bin
   terraform show -json tfplan.bin > tfplan.json
   ./skills/iac-topology/scripts/iac_topology.sh tfplan.json
   ```
