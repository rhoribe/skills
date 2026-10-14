#!/usr/bin/env python3
"""
generate_drawio.py - Converts IaC Topology Intermediate Representation (IR)
into a native Draw.io (.drawio / .drawio.xml) mxGraphModel document.
"""

import sys
import json
import math
import argparse
import html
from pathlib import Path
import xml.etree.ElementTree as ET


PALETTES = {
    "aws": {
        "compute": {"stroke": "#D9480F", "bg": "#FFE8CC"},
        "network": {"stroke": "#E8590C", "bg": "#FFF4E6"},
        "database": {"stroke": "#099268", "bg": "#E6FCF5"},
        "storage": {"stroke": "#2B8A3E", "bg": "#EBFBEE"},
        "security": {"stroke": "#7048E8", "bg": "#F3F0FF"},
        "messaging": {"stroke": "#AE3EC9", "bg": "#F8F0FC"},
        "management": {"stroke": "#495057", "bg": "#F1F3F5"},
        "group": {"stroke": "#F76707", "bg": "#FFF9DB"}
    },
    "azure": {
        "compute": {"stroke": "#1971C2", "bg": "#D0EBFF"},
        "network": {"stroke": "#1864AB", "bg": "#E7F5FF"},
        "database": {"stroke": "#0C8599", "bg": "#E3FAFC"},
        "storage": {"stroke": "#099268", "bg": "#EBFBEE"},
        "security": {"stroke": "#6741D9", "bg": "#F3F0FF"},
        "messaging": {"stroke": "#D6336C", "bg": "#FFF0F6"},
        "management": {"stroke": "#495057", "bg": "#F1F3F5"},
        "group": {"stroke": "#1971C2", "bg": "#F0F8FF"}
    },
    "gcp": {
        "compute": {"stroke": "#D6336C", "bg": "#FFF0F6"},
        "network": {"stroke": "#1971C2", "bg": "#E7F5FF"},
        "database": {"stroke": "#099268", "bg": "#EBFBEE"},
        "storage": {"stroke": "#F59F00", "bg": "#FFF9DB"},
        "security": {"stroke": "#7048E8", "bg": "#F3F0FF"},
        "messaging": {"stroke": "#AE3EC9", "bg": "#F8F0FC"},
        "management": {"stroke": "#495057", "bg": "#F1F3F5"},
        "group": {"stroke": "#2F9E44", "bg": "#F4FCE3"}
    },
    "generic": {
        "compute": {"stroke": "#1C7ED6", "bg": "#E7F5FF"},
        "network": {"stroke": "#495057", "bg": "#F8F9FA"},
        "database": {"stroke": "#099268", "bg": "#E6FCF5"},
        "storage": {"stroke": "#F08C00", "bg": "#FFF9DB"},
        "security": {"stroke": "#7048E8", "bg": "#F3F0FF"},
        "messaging": {"stroke": "#AE3EC9", "bg": "#F8F0FC"},
        "management": {"stroke": "#495057", "bg": "#F1F3F5"},
        "group": {"stroke": "#868E96", "bg": "#F8F9FA"}
    }
}


def get_colors(provider: str, category: str):
    p = PALETTES.get(provider, PALETTES["generic"])
    return p.get(category, p["management"])


class DrawioGenerator:
    def __init__(self, ir_data: dict):
        self.ir = ir_data

    def generate(self) -> str:
        title = self.ir.get("title", "IaC Topology")
        
        # Build XML tree
        mxfile = ET.Element("mxfile", {
            "host": "Electron",
            "agent": "skills.sh/iac-topology",
            "version": "21.0.0",
            "type": "device"
        })
        diagram = ET.SubElement(mxfile, "diagram", {
            "id": "topology-diagram",
            "name": title
        })
        model = ET.SubElement(diagram, "mxGraphModel", {
            "dx": "1400",
            "dy": "900",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": "1600",
            "pageHeight": "1000",
            "math": "0",
            "shadow": "0"
        })
        root = ET.SubElement(model, "root")
        
        # Base cells
        ET.SubElement(root, "mxCell", {"id": "0"})
        ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

        # Title Cell
        title_cell = ET.SubElement(root, "mxCell", {
            "id": "cell_title",
            "value": f"&lt;b style=&quot;font-size: 20px;&quot;&gt;{html.escape(title)}&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#666666&quot;&gt;Source: {self.ir.get('source_type', 'IaC').upper()} | Nodes: {len(self.ir.get('nodes', []))}&lt;/font&gt;",
            "style": "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;",
            "vertex": "1",
            "parent": "1"
        })
        ET.SubElement(title_cell, "mxGeometry", {
            "x": "40", "y": "30", "width": "600", "height": "50", "as": "geometry"
        })

        # Group and Node layout
        groups = {g["id"]: g for g in self.ir.get("groups", [])}
        grouped_nodes = {gid: [] for gid in groups}
        ungrouped_nodes = []

        for node in self.ir.get("nodes", []):
            gid = node.get("group_id")
            if gid and gid in grouped_nodes:
                grouped_nodes[gid].append(node)
            else:
                ungrouped_nodes.append(node)

        NODE_W = 210
        NODE_H = 80
        COL_GAP = 30
        ROW_GAP = 25
        PAD_X = 35
        PAD_Y = 45

        current_gx = 40
        current_gy = 110
        max_row_h = 0

        # Render Groups (Swimlanes)
        for gid, g_nodes in grouped_nodes.items():
            if not g_nodes:
                continue
            g_info = groups[gid]
            provider = g_info.get("provider", "generic")
            g_colors = PALETTES.get(provider, PALETTES["generic"])["group"]

            cols = min(3, max(1, math.ceil(math.sqrt(len(g_nodes)))))
            rows = math.ceil(len(g_nodes) / cols)

            gw = cols * NODE_W + (cols - 1) * COL_GAP + (2 * PAD_X)
            gh = rows * NODE_H + (rows - 1) * ROW_GAP + PAD_Y + 40

            group_cell_id = f"group_{gid}"
            g_label = html.escape(f"⬡ {g_info.get('label', gid)}")
            g_style = f"swimlane;whiteSpace=wrap;html=1;startSize=28;fillColor={g_colors['bg']};strokeColor={g_colors['stroke']};strokeWidth=2;fontColor=#333333;fontStyle=1;rounded=1;shadow=0;"
            
            g_cell = ET.SubElement(root, "mxCell", {
                "id": group_cell_id,
                "value": g_label,
                "style": g_style,
                "vertex": "1",
                "parent": "1"
            })
            ET.SubElement(g_cell, "mxGeometry", {
                "x": str(current_gx),
                "y": str(current_gy),
                "width": str(gw),
                "height": str(gh),
                "as": "geometry"
            })

            # Place nodes inside container
            for idx, node in enumerate(g_nodes):
                r = idx // cols
                c = idx % cols
                nx = PAD_X + c * (NODE_W + COL_GAP)
                ny = PAD_Y + r * (NODE_H + ROW_GAP)
                self._add_node_cell(root, node, nx, ny, NODE_W, NODE_H, parent_id=group_cell_id)

            current_gx += gw + 50
            max_row_h = max(max_row_h, gh)
            if current_gx > 1600:
                current_gx = 40
                current_gy += max_row_h + 50
                max_row_h = 0

        # Render Standalone / Ungrouped Nodes
        if ungrouped_nodes:
            if current_gx != 40:
                current_gx = 40
                current_gy += max_row_h + 50

            cols = min(4, max(1, math.ceil(math.sqrt(len(ungrouped_nodes)))))
            rows = math.ceil(len(ungrouped_nodes) / cols)
            gw = cols * NODE_W + (cols - 1) * COL_GAP + (2 * PAD_X)
            gh = rows * NODE_H + (rows - 1) * ROW_GAP + PAD_Y + 40

            box_id = "group_standalone"
            b_style = "swimlane;whiteSpace=wrap;html=1;startSize=28;fillColor=#F8F9FA;strokeColor=#ADB5BD;strokeWidth=1;strokeDasharray=3 3;fontColor=#495057;fontStyle=1;rounded=1;"
            b_cell = ET.SubElement(root, "mxCell", {
                "id": box_id,
                "value": "Services &amp; Standalone Resources",
                "style": b_style,
                "vertex": "1",
                "parent": "1"
            })
            ET.SubElement(b_cell, "mxGeometry", {
                "x": str(current_gx),
                "y": str(current_gy),
                "width": str(gw),
                "height": str(gh),
                "as": "geometry"
            })

            for idx, node in enumerate(ungrouped_nodes):
                r = idx // cols
                c = idx % cols
                nx = PAD_X + c * (NODE_W + COL_GAP)
                ny = PAD_Y + r * (NODE_H + ROW_GAP)
                self._add_node_cell(root, node, nx, ny, NODE_W, NODE_H, parent_id=box_id)

        # Render Edges
        for i, edge in enumerate(self.ir.get("edges", [])):
            src_node_id = f"node_{edge['source']}"
            dst_node_id = f"node_{edge['target']}"
            label = edge.get("label", "")
            
            e_style = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#495057;strokeWidth=2;endArrow=classic;endFill=1;"
            e_cell = ET.SubElement(root, "mxCell", {
                "id": f"edge_{i}_{edge['source']}_{edge['target']}",
                "value": html.escape(label),
                "style": e_style,
                "edge": "1",
                "source": src_node_id,
                "target": dst_node_id,
                "parent": "1"
            })
            ET.SubElement(e_cell, "mxGeometry", {
                "relative": "1",
                "as": "geometry"
            })

        return ET.tostring(mxfile, encoding="utf-8", xml_declaration=True).decode("utf-8")

    def _add_node_cell(self, root, node: dict, x: int, y: int, w: int, h: int, parent_id: str):
        node_id = f"node_{node['id']}"
        provider = node.get("provider", "generic")
        category = node.get("category", "management")
        colors = get_colors(provider, category)

        name = html.escape(node.get("name", "unnamed"))
        display_type = html.escape(node.get("display_type", node.get("type", "Resource")))
        props = node.get("properties", {})
        prop_str = f"&lt;br&gt;&lt;font color=&quot;#666666&quot; style=&quot;font-size: 10px;&quot;&gt;{html.escape(str(next(iter(props.values()))))}&lt;/font&gt;" if props else ""

        value = f"&lt;b&gt;{name}&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#444444&quot; style=&quot;font-size: 11px;&quot;&gt;[{display_type}]&lt;/font&gt;{prop_str}"
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={colors['bg']};strokeColor={colors['stroke']};strokeWidth=2;fontColor=#212529;shadow=0;"

        cell = ET.SubElement(root, "mxCell", {
            "id": node_id,
            "value": value,
            "style": style,
            "vertex": "1",
            "parent": parent_id
        })
        ET.SubElement(cell, "mxGeometry", {
            "x": str(x),
            "y": str(y),
            "width": str(w),
            "height": str(h),
            "as": "geometry"
        })


def main():
    parser = argparse.ArgumentParser(description="Generate Draw.io XML from IaC IR")
    parser.add_argument("input_ir", help="Path to IaC IR JSON file (or - for stdin)")
    parser.add_argument("-o", "--output", help="Path to output .drawio file")
    args = parser.parse_args()

    if args.input_ir == "-":
        data = json.load(sys.stdin)
    else:
        data = json.loads(Path(args.input_ir).read_text(encoding="utf-8"))

    generator = DrawioGenerator(data)
    xml_str = generator.generate()

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(xml_str, encoding="utf-8")
        print(f"[OK] Generated Draw.io diagram at {args.output}")
    else:
        print(xml_str)


if __name__ == "__main__":
    main()
