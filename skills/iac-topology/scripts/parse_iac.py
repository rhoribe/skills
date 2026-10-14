#!/usr/bin/env python3
"""
parse_iac.py - Universal Infrastructure as Code (IaC) Parser
Extracts resources, metadata, groups, and dependency relationships from:
- Terraform / OpenTofu (.tf, terraform plan/state JSON)
- AWS CloudFormation (YAML, JSON)
- Azure Bicep (.bicep, ARM JSON)
- Ansible (Playbooks, task lists, inventories)
- Kubernetes manifests (.yaml, .yml)
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path

# Optional PyYAML support with graceful fallback
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def detect_provider(res_type: str) -> str:
    """Infer cloud provider from resource type string."""
    lower = res_type.lower()
    if lower.startswith("aws_") or lower.startswith("aws::") or "amazon.aws" in lower or lower.startswith("ec2_"):
        return "aws"
    if lower.startswith("azurerm_") or "microsoft." in lower or "azure.azcollection" in lower or lower.startswith("azure_rm_"):
        return "azure"
    if lower.startswith("google_") or "google.cloud" in lower or lower.startswith("gcp_"):
        return "gcp"
    if "kubernetes" in lower or lower.startswith("k8s_"):
        return "kubernetes"
    if "docker" in lower:
        return "docker"
    return "generic"


def categorize_resource(res_type: str) -> str:
    """Classify resource into architecture category."""
    lower = res_type.lower()
    # Network
    if any(k in lower for k in [
        "vpc", "vnet", "subnet", "route", "gateway", "igw", "nat", "security_group",
        "nsg", "firewall", "load_balancer", "lb", "alb", "nlb", "elb", "ingress",
        "network", "traffic", "dns", "route53", "cdn", "cloudfront"
    ]):
        return "network"
    # Compute
    if any(k in lower for k in [
        "instance", "server", "vm", "virtual_machine", "compute", "lambda",
        "function", "container", "pod", "deployment", "daemonset", "statefulset",
        "eks", "aks", "gke", "ecs", "appservice", "batch", "autoscaling"
    ]):
        return "compute"
    # Database
    if any(k in lower for k in [
        "db", "database", "rds", "aurora", "dynamodb", "cosmos", "sql", "postgres",
        "mysql", "redis", "elasticache", "memcached", "mongodb", "cassandra"
    ]):
        return "database"
    # Storage
    if any(k in lower for k in [
        "s3", "bucket", "storage", "blob", "volume", "ebs", "efs", "disk",
        "filestore", "pvc", "persistentvolume"
    ]):
        return "storage"
    # Security / Identity
    if any(k in lower for k in [
        "iam", "role", "policy", "user", "key", "kms", "keyvault", "vault",
        "certificate", "secret", "waf", "shield"
    ]):
        return "security"
    # Messaging / Queue
    if any(k in lower for k in [
        "sqs", "sns", "queue", "topic", "event", "eventbridge", "pubsub",
        "servicebus", "kafka", "mq"
    ]):
        return "messaging"
    return "management"


def clean_label(text: str) -> str:
    """Clean label for display."""
    return re.sub(r'["\']', '', text).strip()


class IaCParser:
    def __init__(self, title="Infrastructure Topology"):
        self.title = title
        self.nodes = {}       # id -> node dict
        self.edges = []       # list of edge dicts
        self.groups = {}      # id -> group dict
        self.detected_types = set()

    def add_group(self, group_id: str, label: str, group_type: str = "container", provider: str = "generic", parent_id: str = None):
        if group_id not in self.groups:
            self.groups[group_id] = {
                "id": group_id,
                "label": label,
                "type": group_type,
                "provider": provider,
                "parent_id": parent_id
            }

    def add_node(self, node_id: str, name: str, res_type: str, display_type: str = None,
                 provider: str = None, category: str = None, group_id: str = None, properties: dict = None):
        if not provider:
            provider = detect_provider(res_type)
        if not category:
            category = categorize_resource(res_type)
        if not display_type:
            display_type = res_type

        self.nodes[node_id] = {
            "id": node_id,
            "name": name,
            "type": res_type,
            "display_type": display_type,
            "provider": provider,
            "category": category,
            "group_id": group_id,
            "properties": properties or {}
        }

    def add_edge(self, source: str, target: str, label: str = "depends_on", edge_type: str = "reference"):
        if source == target:
            return
        # avoid duplicate edges
        for e in self.edges:
            if e["source"] == source and e["target"] == target and e["label"] == label:
                return
        self.edges.append({
            "source": source,
            "target": target,
            "label": label,
            "type": edge_type
        })

    # =========================================================================
    # Terraform HCL & Plan JSON Parser
    # =========================================================================
    def parse_terraform_file(self, content: str, file_path: str = ""):
        self.detected_types.add("terraform")
        
        # 1. Parse modules
        module_pattern = re.compile(r'module\s+"([^"]+)"\s*\{(.*?)\n\}', re.DOTALL)
        for match in module_pattern.finditer(content):
            mod_name = match.group(1)
            mod_body = match.group(2)
            mod_id = f"module.{mod_name}"
            
            source_match = re.search(r'source\s*=\s*"([^"]+)"', mod_body)
            source_val = source_match.group(1) if source_match else "local_module"
            
            self.add_node(
                node_id=mod_id,
                name=mod_name,
                res_type="module",
                display_type=f"Module: {source_val.split('/')[-1]}",
                provider=detect_provider(source_val),
                category="management",
                properties={"source": source_val}
            )

        # 2. Parse resources: resource "type" "name" { ... }
        resource_pattern = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{(.*?)\n\}', re.DOTALL)
        for match in resource_pattern.finditer(content):
            res_type = match.group(1)
            res_name = match.group(2)
            body = match.group(3)
            node_id = f"{res_type}.{res_name}"
            
            # Detect group association (VPC, Subnet, Resource Group)
            group_id = None
            props = {}

            # Check for VPC / VNet reference
            vpc_match = re.search(r'(?:vpc_id|virtual_network_name)\s*=\s*([a-zA-Z0-9_.-]+)', body)
            if vpc_match:
                vpc_ref = vpc_match.group(1).replace('"', '')
                group_id = f"group_{vpc_ref}"
                self.add_group(group_id, f"Network: {vpc_ref}", "vpc", detect_provider(res_type))

            # Check for Subnet reference
            subnet_match = re.search(r'subnet_id\s*=\s*([a-zA-Z0-9_.-]+)', body)
            if subnet_match:
                sub_ref = subnet_match.group(1).replace('"', '')
                if not group_id:
                    group_id = f"group_{sub_ref}"
                    self.add_group(group_id, f"Subnet: {sub_ref}", "subnet", detect_provider(res_type))

            # Check for Resource Group reference (Azure)
            rg_match = re.search(r'resource_group_name\s*=\s*([a-zA-Z0-9_.-]+)', body)
            if rg_match and not group_id:
                rg_ref = rg_match.group(1).replace('"', '')
                group_id = f"group_{rg_ref}"
                self.add_group(group_id, f"RG: {rg_ref}", "resource_group", "azure")

            # Create group for VPC or VNet resource itself
            if any(k in res_type for k in ["_vpc", "_virtual_network"]):
                self.add_group(f"group_{node_id}", f"VPC: {res_name}", "vpc", detect_provider(res_type))

            # Extract sample properties
            for prop in ["instance_type", "ami", "cidr_block", "engine", "runtime"]:
                m = re.search(rf'{prop}\s*=\s*"([^"]+)"', body)
                if m:
                    props[prop] = m.group(1)

            # Prettify display type
            display_name = res_type
            if "_" in res_type:
                parts = res_type.split("_", 1)
                display_name = parts[1].replace("_", " ").title()

            self.add_node(
                node_id=node_id,
                name=res_name,
                res_type=res_type,
                display_type=display_name,
                group_id=group_id,
                properties=props
            )

        # 3. Second pass for references / dependencies across the whole file
        for match in resource_pattern.finditer(content):
            source_type = match.group(1)
            source_name = match.group(2)
            source_id = f"{source_type}.{source_name}"
            body = match.group(3)

            # References to other resources: type.name
            ref_pattern = re.compile(r'([a-zA-Z0-9_]+)\.([a-zA-Z0-9_-]+)(?:\.[a-zA-Z0-9_-]+)?')
            for ref_match in ref_pattern.finditer(body):
                target_type = ref_match.group(1)
                target_name = ref_match.group(2)
                target_id = f"{target_type}.{target_name}"
                if target_id in self.nodes and target_id != source_id:
                    self.add_edge(source_id, target_id, label="references")

            # Explicit depends_on = [ ... ]
            depends_match = re.search(r'depends_on\s*=\s*\[(.*?)\]', body, re.DOTALL)
            if depends_match:
                deps_text = depends_match.group(1)
                for item in re.findall(r'([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_-]+)+)', deps_text):
                    clean_dep = item.strip()
                    if clean_dep in self.nodes and clean_dep != source_id:
                        self.add_edge(source_id, clean_dep, label="depends_on")

    def parse_terraform_json(self, data: dict):
        """Parse Terraform Plan JSON or State JSON."""
        self.detected_types.add("terraform")
        
        # Check for plan representation (resource_changes)
        if "resource_changes" in data:
            for item in data.get("resource_changes", []):
                res_type = item.get("type", "unknown")
                res_name = item.get("name", "unknown")
                node_id = item.get("address", f"{res_type}.{res_name}")
                provider = detect_provider(item.get("provider_name", res_type))
                
                change = item.get("change", {})
                after = change.get("after") or {}
                
                group_id = None
                if "vpc_id" in after and isinstance(after["vpc_id"], str):
                    group_id = f"group_{after['vpc_id']}"
                    self.add_group(group_id, f"VPC: {after['vpc_id']}", "vpc", provider)

                self.add_node(
                    node_id=node_id,
                    name=res_name,
                    res_type=res_type,
                    display_type=res_type.split("_", 1)[-1].replace("_", " ").title() if "_" in res_type else res_type,
                    provider=provider,
                    group_id=group_id,
                    properties={k: str(v) for k, v in after.items() if k in ["instance_type", "engine", "cidr_block"]}
                )

        # Check for state / values representation
        values = data.get("values", {}).get("root_module", {})
        if "resources" in values:
            for item in values["resources"]:
                res_type = item.get("type", "unknown")
                res_name = item.get("name", "unknown")
                node_id = item.get("address", f"{res_type}.{res_name}")
                self.add_node(node_id=node_id, name=res_name, res_type=res_type)

        # Check for configuration dependencies in plan JSON
        config_resources = data.get("configuration", {}).get("root_module", {}).get("resources", [])
        for res in config_resources:
            src_id = f"{res.get('type')}.{res.get('name')}"
            for dep in res.get("depends_on", []):
                if dep in self.nodes:
                    self.add_edge(src_id, dep, label="depends_on")

    # =========================================================================
    # AWS CloudFormation (YAML / JSON) Parser
    # =========================================================================
    def parse_cloudformation_dict(self, data: dict):
        self.detected_types.add("cloudformation")
        resources = data.get("Resources", {})
        if not isinstance(resources, dict):
            return

        for res_name, res_def in resources.items():
            if not isinstance(res_def, dict):
                continue
            res_type = res_def.get("Type", "AWS::Resource")
            props = res_def.get("Properties", {}) or {}
            node_id = res_name
            
            # Grouping detection
            group_id = None
            if "VpcId" in props:
                vpc_ref = str(props["VpcId"])
                group_id = f"group_{vpc_ref}"
                self.add_group(group_id, f"VPC: {vpc_ref}", "vpc", "aws")
            elif "SubnetId" in props:
                sub_ref = str(props["SubnetId"])
                group_id = f"group_{sub_ref}"
                self.add_group(group_id, f"Subnet: {sub_ref}", "subnet", "aws")

            # Check if this resource is a VPC itself
            if res_type == "AWS::EC2::VPC":
                self.add_group(f"group_{res_name}", f"VPC: {res_name}", "vpc", "aws")

            # Extract clean display name
            display_name = res_type.replace("AWS::", "")
            
            self.add_node(
                node_id=node_id,
                name=res_name,
                res_type=res_type,
                display_type=display_name,
                provider="aws",
                group_id=group_id,
                properties={k: str(v) for k, v in props.items() if isinstance(v, (str, int, bool)) and k in [
                    "InstanceType", "DBInstanceClass", "Engine", "Runtime", "CidrBlock"
                ]}
            )

        # Cross-reference pass
        for res_name, res_def in resources.items():
            if not isinstance(res_def, dict):
                continue
            source_id = res_name
            
            # Explicit DependsOn
            deps = res_def.get("DependsOn", [])
            if isinstance(deps, str):
                deps = [deps]
            for dep in deps:
                if dep in self.nodes:
                    self.add_edge(source_id, dep, label="depends_on")

            # Recursive scan for Ref and Fn::GetAtt
            def find_refs(obj):
                if isinstance(obj, dict):
                    if "Ref" in obj and isinstance(obj["Ref"], str):
                        target = obj["Ref"]
                        if target in self.nodes and target != source_id:
                            self.add_edge(source_id, target, label="ref")
                    if "Fn::GetAtt" in obj:
                        att = obj["Fn::GetAtt"]
                        target = att[0] if isinstance(att, list) and len(att) > 0 else (att.split(".")[0] if isinstance(att, str) else None)
                        if target and target in self.nodes and target != source_id:
                            self.add_edge(source_id, target, label="get_att")
                    for k, v in obj.items():
                        find_refs(v)
                elif isinstance(obj, list):
                    for item in obj:
                        find_refs(item)

            find_refs(res_def.get("Properties", {}))

    # =========================================================================
    # Azure Bicep (.bicep) & ARM Template Parser
    # =========================================================================
    def parse_bicep_file(self, content: str):
        self.detected_types.add("bicep")
        
        # 1. Modules: module <name> '<path>' = { ... }
        mod_pattern = re.compile(r'module\s+([a-zA-Z0-9_]+)\s+[\'"]([^\'"]+)[\'"]\s*=\s*\{(.*?)\n\}', re.DOTALL)
        for match in mod_pattern.finditer(content):
            mod_name = match.group(1)
            mod_path = match.group(2)
            node_id = mod_name
            self.add_node(
                node_id=node_id,
                name=mod_name,
                res_type="module",
                display_type=f"Module ({Path(mod_path).stem})",
                provider="azure",
                category="management",
                properties={"path": mod_path}
            )

        # 2. Resources: resource <name> '<type>@<version>' [existing] = { ... }
        res_pattern = re.compile(r'resource\s+([a-zA-Z0-9_]+)\s+[\'"]([a-zA-Z0-9._/]+)@[0-9-]+[\'"](?:\s+existing)?\s*=\s*\{(.*?)\n\}', re.DOTALL)
        for match in res_pattern.finditer(content):
            res_name = match.group(1)
            res_type = match.group(2)
            body = match.group(3)
            node_id = res_name
            
            group_id = None
            # Check parent relationship
            parent_match = re.search(r'parent\s*:\s*([a-zA-Z0-9_]+)', body)
            if parent_match:
                parent_res = parent_match.group(1)
                group_id = f"group_{parent_res}"
                self.add_group(group_id, f"Parent: {parent_res}", "container", "azure")

            display_type = res_type.split("/")[-1].replace("virtualNetworks", "Virtual Network").title()

            self.add_node(
                node_id=node_id,
                name=res_name,
                res_type=res_type,
                display_type=display_type,
                provider="azure",
                group_id=group_id
            )

        # 3. References and dependsOn
        for match in res_pattern.finditer(content):
            res_name = match.group(1)
            body = match.group(3)
            source_id = res_name

            # Scan for other resource symbolic names in properties
            for target_id in self.nodes:
                if target_id != source_id:
                    # check word boundary
                    if re.search(rf'\b{re.escape(target_id)}\.(?:id|name|properties)\b', body):
                        self.add_edge(source_id, target_id, label="references")

            # Check explicit dependsOn: [ ... ]
            deps_match = re.search(r'dependsOn\s*:\s*\[(.*?)\]', body, re.DOTALL)
            if deps_match:
                for item in re.findall(r'([a-zA-Z0-9_]+)', deps_match.group(1)):
                    if item in self.nodes and item != source_id:
                        self.add_edge(source_id, item, label="depends_on")

    # =========================================================================
    # Ansible Playbook / Tasks Parser
    # =========================================================================
    def parse_ansible_data(self, data):
        self.detected_types.add("ansible")
        tasks = []
        if isinstance(data, list):
            for play in data:
                if isinstance(play, dict):
                    if "tasks" in play and isinstance(play["tasks"], list):
                        tasks.extend(play["tasks"])
                    elif "block" in play and isinstance(play["block"], list):
                        tasks.extend(play["block"])
                    elif any(k in play for k in ["name", "hosts"]) and not any(k in play for k in ["tasks", "roles"]):
                        tasks.append(play)
        elif isinstance(data, dict):
            if "tasks" in data:
                tasks.extend(data["tasks"])

        prev_node_id = None
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                continue
            task_name = task.get("name", f"Task {i+1}")
            
            # Find module name
            module_name = None
            module_args = {}
            for key, val in task.items():
                if key not in ["name", "register", "when", "with_items", "loop", "tags", "vars", "notify", "become", "delegate_to"]:
                    module_name = key
                    module_args = val if isinstance(val, dict) else {}
                    break

            if not module_name:
                continue

            provider = detect_provider(module_name)
            category = categorize_resource(module_name)
            
            # Determine resource label
            res_label = module_args.get("name") or module_args.get("vm_name") or module_args.get("bucket") or task_name
            node_id = task.get("register") or f"task_{i+1}_{module_name.replace('.', '_')}"
            
            # Grouping
            group_id = None
            if "vpc_id" in module_args:
                group_id = f"group_{module_args['vpc_id']}"
                self.add_group(group_id, f"VPC: {module_args['vpc_id']}", "vpc", provider)
            elif "resource_group" in module_args:
                group_id = f"group_{module_args['resource_group']}"
                self.add_group(group_id, f"RG: {module_args['resource_group']}", "resource_group", provider)

            self.add_node(
                node_id=node_id,
                name=clean_label(str(res_label)),
                res_type=module_name,
                display_type=module_name.split(".")[-1].replace("_", " ").title(),
                provider=provider,
                category=category,
                group_id=group_id,
                properties={k: str(v) for k, v in module_args.items() if isinstance(v, (str, int, bool)) and k in [
                    "image", "flavor", "instance_type", "state", "region"
                ]}
            )

            # Link sequential tasks in same role/playbook if relevant
            if prev_node_id and category in ["compute", "database", "storage"]:
                self.add_edge(prev_node_id, node_id, label="precedes", edge_type="sequence")
            prev_node_id = node_id

    # =========================================================================
    # Kubernetes Manifest Parser
    # =========================================================================
    def parse_kubernetes_doc(self, doc: dict):
        if not isinstance(doc, dict):
            return
        kind = doc.get("kind")
        if not kind:
            return
        self.detected_types.add("kubernetes")
        metadata = doc.get("metadata", {})
        name = metadata.get("name", "unnamed")
        namespace = metadata.get("namespace", "default")
        node_id = f"k8s_{kind.lower()}_{namespace}_{name}"

        group_id = f"group_ns_{namespace}"
        self.add_group(group_id, f"Namespace: {namespace}", "namespace", "kubernetes")

        self.add_node(
            node_id=node_id,
            name=name,
            res_type=f"k8s/{kind}",
            display_type=f"K8s {kind}",
            provider="kubernetes",
            category=categorize_resource(kind),
            group_id=group_id
        )

    # =========================================================================
    # Universal File Ingestion
    # =========================================================================
    def ingest_file(self, file_path: str):
        path = Path(file_path)
        if not path.is_file():
            return

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"[WARN] Unable to read file {file_path}: {e}", file=sys.stderr)
            return

        suffix = path.suffix.lower()

        # 1. Terraform / OpenTofu (.tf)
        if suffix == ".tf":
            self.parse_terraform_file(content, file_path)
            return

        # 2. Azure Bicep (.bicep)
        if suffix == ".bicep":
            self.parse_bicep_file(content)
            return

        # 3. JSON files (Terraform Plan/State, ARM, CloudFormation, Ansible JSON)
        if suffix == ".json":
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    if "resource_changes" in data or "terraform_version" in data:
                        self.parse_terraform_json(data)
                        return
                    if "$schema" in data and "deploymentTemplate.json" in data["$schema"]:
                        # ARM template
                        self.detected_types.add("bicep")
                        for res in data.get("resources", []):
                            res_name = res.get("name", "unnamed")
                            res_type = res.get("type", "Azure::Resource")
                            self.add_node(res_name, res_name, res_type, provider="azure")
                        return
                    if "AWSTemplateFormatVersion" in data or "Resources" in data:
                        self.parse_cloudformation_dict(data)
                        return
            except Exception:
                pass

        # 4. YAML files (CloudFormation, Ansible, Kubernetes)
        if suffix in [".yaml", ".yml"]:
            if HAS_YAML:
                try:
                    # Ignore CloudFormation custom tags (!Ref, !Sub, !GetAtt) without error
                    yaml.SafeLoader.add_multi_constructor("!", lambda loader, suffix, node: (
                        loader.construct_mapping(node) if isinstance(node, yaml.MappingNode)
                        else loader.construct_sequence(node) if isinstance(node, yaml.SequenceNode)
                        else loader.construct_scalar(node)
                    ))
                    docs = list(yaml.safe_load_all(content))
                    for doc in docs:
                        if isinstance(doc, dict):
                            if "AWSTemplateFormatVersion" in doc or ("Resources" in doc and isinstance(doc["Resources"], dict)):
                                self.parse_cloudformation_dict(doc)
                            elif "kind" in doc and "apiVersion" in doc:
                                self.parse_kubernetes_doc(doc)
                            elif any(k in doc for k in ["hosts", "tasks"]):
                                self.parse_ansible_data([doc])
                        elif isinstance(doc, list):
                            self.parse_ansible_data(doc)
                    return
                except Exception:
                    pass

            # Fallback simple text scan if PyYAML fails or is absent
            if "AWSTemplateFormatVersion" in content or "AWS::" in content:
                self.detected_types.add("cloudformation")
                res_matches = re.finditer(r'^\s{2}([A-Za-z0-9]+):\s*\n\s{4}Type:\s*([A-Za-z0-9:]+)', content, re.MULTILINE)
                for rm in res_matches:
                    r_name, r_type = rm.group(1), rm.group(2)
                    self.add_node(r_name, r_name, r_type, provider="aws")

    def ingest_path(self, target_path: str):
        path = Path(target_path)
        if path.is_file():
            self.ingest_file(str(path))
        elif path.is_dir():
            for root, dirs, files in os.walk(target_path):
                # skip git and cache dirs
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["node_modules", ".terraform"]]
                for file in sorted(files):
                    ext = Path(file).suffix.lower()
                    if ext in [".tf", ".bicep", ".yaml", ".yml", ".json"]:
                        self.ingest_file(os.path.join(root, file))

    def to_dict(self) -> dict:
        """Produce Intermediate Representation (IR)."""
        detected = list(self.detected_types)
        primary_source = detected[0] if detected else "generic"
        
        return {
            "title": self.title,
            "source_type": primary_source,
            "detected_sources": detected,
            "groups": list(self.groups.values()),
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
            "summary": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "total_groups": len(self.groups)
            }
        }


def main():
    parser = argparse.ArgumentParser(description="Universal IaC Topology Parser")
    parser.add_argument("path", help="Path to IaC file or directory")
    parser.add_argument("-o", "--output", help="Output JSON IR file (stdout if omitted)")
    parser.add_argument("--title", default="Infrastructure Topology", help="Title for the topology")
    args = parser.parse_args()

    iac_parser = IaCParser(title=args.title)
    iac_parser.ingest_path(args.path)
    result = iac_parser.to_dict()

    out_json = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(out_json, encoding="utf-8")
        print(f"[OK] Parsed {result['summary']['total_nodes']} nodes, {result['summary']['total_edges']} edges. Saved to {args.output}")
    else:
        print(out_json)


if __name__ == "__main__":
    main()
