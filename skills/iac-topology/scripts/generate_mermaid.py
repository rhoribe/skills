#!/usr/bin/env python3
"""
generate_mermaid.py - Converts IaC Topology Intermediate Representation (IR)
into an instant Markdown Mermaid flowchart with subgraphs and semantic cloud colors.
"""

import sys
import json
import re
import argparse
from pathlib import Path

# Icon registry import
try:
    from icons import get_icon
except ImportError:
    try:
        from .icons import get_icon
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from icons import get_icon


def sanitize_id(raw_id: str) -> str:
    """Sanitize string for Mermaid node ID."""
    return re.sub(r'[^a-zA-Z0-9_]', '_', raw_id)


def sanitize_text(text: str) -> str:
    """Escape characters that break Mermaid labels."""
    return text.replace('"', "'").replace("\n", " ")


class MermaidGenerator:
    def __init__(self, ir_data: dict, orientation="TD"):
        self.ir = ir_data
        self.orientation = orientation

    def generate(self) -> str:
        lines = [f"flowchart {self.orientation}"]

        # Class styles
        lines.append("    %% Styling classes")
        lines.append("    classDef aws fill:#ffe8cc,stroke:#d9480f,stroke-width:2px,color:#212529;")
        lines.append("    classDef azure fill:#d0ebff,stroke:#1971c2,stroke-width:2px,color:#212529;")
        lines.append("    classDef gcp fill:#ebfbee,stroke:#2b8a3e,stroke-width:2px,color:#212529;")
        lines.append("    classDef k8s fill:#edf2ff,stroke:#364fc7,stroke-width:2px,color:#212529;")
        lines.append("    classDef generic fill:#f1f3f5,stroke:#495057,stroke-width:2px,color:#212529;")
        lines.append("")

        groups = {g["id"]: g for g in self.ir.get("groups", [])}
        grouped_nodes = {gid: [] for gid in groups}
        ungrouped_nodes = []

        for node in self.ir.get("nodes", []):
            gid = node.get("group_id")
            if gid and gid in grouped_nodes:
                grouped_nodes[gid].append(node)
            else:
                ungrouped_nodes.append(node)

        node_classes = {}

        # Subgraphs for groups
        for gid, g_nodes in grouped_nodes.items():
            if not g_nodes:
                continue
            g_info = groups[gid]
            g_provider = g_info.get("provider", "generic")
            g_icon = get_icon(g_provider, "management")
            g_label = sanitize_text(g_info.get("label", gid))
            s_gid = sanitize_id(gid)

            lines.append(f'    subgraph {s_gid} ["{g_icon["provider_badge"]} {g_label}"]')
            for node in g_nodes:
                nid = sanitize_id(node["id"])
                name = sanitize_text(node.get("name", "unnamed"))
                dtype = sanitize_text(node.get("display_type", node.get("type", "Resource")))
                props = node.get("properties", {})
                prop_str = f"<br/><small>{sanitize_text(str(next(iter(props.values()))))}</small>" if props else ""
                
                icon = node.get("icon") or get_icon(node.get("provider", "generic"), node.get("category", "management"), node.get("type", ""))
                fa_prefix = f"{icon['fa']} " if icon.get("fa") else ""
                badge = f"{icon['provider_badge']} " if icon.get("provider_badge") else ""
                
                lines.append(f'        {nid}["{fa_prefix}{badge}<b>{name}</b><br/>{dtype}{prop_str}"]')
                node_classes[nid] = node.get("provider", "generic")
            lines.append("    end")
            lines.append("")

        # Ungrouped nodes
        if ungrouped_nodes:
            lines.append('    subgraph standalone ["Services & Standalone Resources"]')
            for node in ungrouped_nodes:
                nid = sanitize_id(node["id"])
                name = sanitize_text(node.get("name", "unnamed"))
                dtype = sanitize_text(node.get("display_type", node.get("type", "Resource")))
                props = node.get("properties", {})
                prop_str = f"<br/><small>{sanitize_text(str(next(iter(props.values()))))}</small>" if props else ""
                
                icon = node.get("icon") or get_icon(node.get("provider", "generic"), node.get("category", "management"), node.get("type", ""))
                fa_prefix = f"{icon['fa']} " if icon.get("fa") else ""
                badge = f"{icon['provider_badge']} " if icon.get("provider_badge") else ""
                
                lines.append(f'        {nid}["{fa_prefix}{badge}<b>{name}</b><br/>{dtype}{prop_str}"]')
                node_classes[nid] = node.get("provider", "generic")
            lines.append("    end")
            lines.append("")

        # Edges
        for edge in self.ir.get("edges", []):
            src = sanitize_id(edge["source"])
            dst = sanitize_id(edge["target"])
            label = sanitize_text(edge.get("label", ""))
            if label:
                lines.append(f'    {src} -->|"{label}"| {dst}')
            else:
                lines.append(f'    {src} --> {dst}')

        lines.append("")
        # Apply classes
        lines.append("    %% Apply class mapping")
        for nid, provider in node_classes.items():
            cls = "aws" if provider == "aws" else "azure" if provider == "azure" else "gcp" if provider == "gcp" else "k8s" if provider == "kubernetes" else "generic"
            lines.append(f"    class {nid} {cls};")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate Mermaid Flowchart from IaC IR")
    parser.add_argument("input_ir", help="Path to IaC IR JSON file (or - for stdin)")
    parser.add_argument("-o", "--output", help="Path to output .mmd file")
    parser.add_argument("--orientation", default="TD", choices=["TD", "LR"], help="Flowchart layout orientation")
    args = parser.parse_args()

    if args.input_ir == "-":
        data = json.load(sys.stdin)
    else:
        data = json.loads(Path(args.input_ir).read_text(encoding="utf-8"))

    generator = MermaidGenerator(data, orientation=args.orientation)
    mmd = generator.generate()

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(mmd, encoding="utf-8")
        print(f"[OK] Generated Mermaid diagram at {args.output}")
    else:
        print(mmd)


if __name__ == "__main__":
    main()
