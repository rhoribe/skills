# Ansible Infrastructure Playbook Topology Guide

This reference guide explains how `iac-topology` extracts cloud infrastructure topologies from Ansible playbooks, role tasks, and orchestration workflows.

---

## 1. Supported Ansible Infrastructure Modules

Ansible manages infrastructure via collections. `iac-topology` identifies tasks using:

### Amazon Web Services (`amazon.aws.*`, `community.aws.*`)
- `ec2_vpc_net` / `amazon.aws.ec2_vpc_net` (VPC Container)
- `ec2_vpc_subnet` / `amazon.aws.ec2_vpc_subnet` (Subnet Container)
- `ec2_instance` / `amazon.aws.ec2_instance` (Compute Node)
- `rds_instance` / `amazon.aws.rds_instance` (Database Node)
- `s3_bucket` / `amazon.aws.s3_bucket` (Storage Node)
- `elb_application_lb` / `elb_target_group` (Networking / Edge)

### Microsoft Azure (`azure.azcollection.*`)
- `azure_rm_virtualnetwork` (VNet Container)
- `azure_rm_subnet` (Subnet Container)
- `azure_rm_virtualmachine` (VM Compute Node)
- `azure_rm_storageaccount` (Storage Node)
- `azure_rm_sqldatabase` (Database Node)

### Google Cloud (`google.cloud.*`)
- `gcp_compute_network` / `gcp_compute_subnetwork` (Network Container)
- `gcp_compute_instance` (Compute Node)
- `gcp_sql_instance` (Database Node)

### Containers & Docker (`community.docker.*`)
- `docker_container`, `docker_network`, `docker_volume`

---

## 2. Inferred Relationships

In Ansible playbooks, dependencies are determined by:
1. **Registered Variables**: `register: vpc_out` referenced in subsequent tasks via `vpc_id: "{{ vpc_out.vpc.id }}"`.
2. **Explicit Network IDs**: Parameters like `vpc_id`, `subnet_id`, or `network_name`.
3. **Execution Sequence**: Sequential tasks creating interconnected components within the same playbook.
