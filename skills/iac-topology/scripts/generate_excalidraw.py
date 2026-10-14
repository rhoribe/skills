#!/usr/bin/env python3
"""
generate_excalidraw.py - Converts IaC Topology Intermediate Representation (IR)
into an editable, beautifully formatted Excalidraw (.excalidraw) JSON file.
"""

import sys
import json
import math
import argparse
import random
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


# Semantic color palettes
PALETTES = {
    "aws": {
        "compute": {"stroke": "#d9480f", "bg": "#ffe8cc"},       # Warm Orange
        "network": {"stroke": "#e8590c", "bg": "#fff4e6"},       # Amber
        "database": {"stroke": "#099268", "bg": "#e6fcf5"},      # Emerald
        "storage": {"stroke": "#2b8a3e", "bg": "#ebfbee"},       # Green
        "security": {"stroke": "#7048e8", "bg": "#f3f0ff"},      # Purple
        "messaging": {"stroke": "#ae3ec9", "bg": "#f8f0fc"},     # Grape
        "management": {"stroke": "#495057", "bg": "#f1f3f5"},    # Gray
        "group": {"stroke": "#f76707", "bg": "#fff9db"}
    },
    "azure": {
        "compute": {"stroke": "#1971c2", "bg": "#d0ebff"},       # Azure Blue
        "network": {"stroke": "#1864ab", "bg": "#e7f5ff"},       # Deep Blue
        "database": {"stroke": "#0c8599", "bg": "#e3fafc"},      # Cyan
        "storage": {"stroke": "#099268", "bg": "#ebfbee"},       # Green
        "security": {"stroke": "#6741d9", "bg": "#f3f0ff"},      # Indigo
        "messaging": {"stroke": "#d6336c", "bg": "#fff0f6"},     # Pink
        "management": {"stroke": "#495057", "bg": "#f1f3f5"},    # Gray
        "group": {"stroke": "#1971c2", "bg": "#f0f8ff"}
    },
    "gcp": {
        "compute": {"stroke": "#d6336c", "bg": "#fff0f6"},       # Google Red/Pink
        "network": {"stroke": "#1971c2", "bg": "#e7f5ff"},       # Google Blue
        "database": {"stroke": "#099268", "bg": "#ebfbee"},      # Google Green
        "storage": {"stroke": "#f59f00", "bg": "#fff9db"},       # Google Yellow
        "security": {"stroke": "#7048e8", "bg": "#f3f0ff"},      # Purple
        "messaging": {"stroke": "#ae3ec9", "bg": "#f8f0fc"},     # Grape
        "management": {"stroke": "#495057", "bg": "#f1f3f5"},    # Gray
        "group": {"stroke": "#2f9e44", "bg": "#f4fce3"}
    },
    "kubernetes": {
        "compute": {"stroke": "#364fc7", "bg": "#edf2ff"},       # K8s Blue
        "network": {"stroke": "#1971c2", "bg": "#e7f5ff"},       # Cyan
        "database": {"stroke": "#087f5b", "bg": "#e6fcf5"},      # Teal
        "storage": {"stroke": "#2b8a3e", "bg": "#ebfbee"},       # Green
        "security": {"stroke": "#5f3dc4", "bg": "#f3f0ff"},      # Deep Violet
        "messaging": {"stroke": "#e64980", "bg": "#fff0f6"},     # Rose
        "management": {"stroke": "#495057", "bg": "#f1f3f5"},    # Gray
        "group": {"stroke": "#364fc7", "bg": "#f8f9fa"}
    },
    "generic": {
        "compute": {"stroke": "#1c7ed6", "bg": "#e7f5ff"},
        "network": {"stroke": "#495057", "bg": "#f8f9fa"},
        "database": {"stroke": "#099268", "bg": "#e6fcf5"},
        "storage": {"stroke": "#f08c00", "bg": "#fff9db"},
        "security": {"stroke": "#7048e8", "bg": "#f3f0ff"},
        "messaging": {"stroke": "#ae3ec9", "bg": "#f8f0fc"},
        "management": {"stroke": "#495057", "bg": "#f1f3f5"},
        "group": {"stroke": "#868e96", "bg": "#f8f9fa"}
    }
}


def get_colors(provider: str, category: str):
    p = PALETTES.get(provider, PALETTES["generic"])
    return p.get(category, p["management"])


class ExcalidrawGenerator:
    def __init__(self, ir_data: dict):
        self.ir = ir_data
        self.elements = []
        self.files = {}
        self.seed_counter = 100000

    def next_seed(self):
        self.seed_counter += 1
        return self.seed_counter

    def make_title(self, title: str, subtitle: str):
        # Header banner
        title_id = "header_title"
        self.elements.append({
            "id": title_id,
            "type": "text",
            "x": 60,
            "y": 40,
            "width": 800,
            "height": 40,
            "angle": 0,
            "strokeColor": "#1e1e1e",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "roundness": None,
            "seed": self.next_seed(),
            "version": 1,
            "versionNonce": 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "text": title,
            "fontSize": 28,
            "fontFamily": 1,
            "textAlign": "left",
            "verticalAlign": "top",
            "containerId": None,
            "originalText": title,
            "lineHeight": 1.25
        })

        if subtitle:
            self.elements.append({
                "id": "header_subtitle",
                "type": "text",
                "x": 60,
                "y": 85,
                "width": 800,
                "height": 24,
                "angle": 0,
                "strokeColor": "#666666",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 1,
                "strokeStyle": "solid",
                "roughness": 1,
                "opacity": 100,
                "groupIds": [],
                "roundness": None,
                "seed": self.next_seed(),
                "version": 1,
                "versionNonce": 1,
                "isDeleted": False,
                "boundElements": None,
                "updated": 1,
                "link": None,
                "locked": False,
                "text": subtitle,
                "fontSize": 14,
                "fontFamily": 1,
                "textAlign": "left",
                "verticalAlign": "top",
                "containerId": None,
                "originalText": subtitle,
                "lineHeight": 1.25
            })

    def generate(self) -> dict:
        title = self.ir.get("title", "Infrastructure Topology")
        source = self.ir.get("source_type", "IaC").upper()
        summary = self.ir.get("summary", {})
        subtitle = f"Source: {source} | Resources: {summary.get('total_nodes', 0)} | Relationships: {summary.get('total_edges', 0)}"
        
        self.make_title(title, subtitle)

        # 1. Organize nodes by group
        groups = {g["id"]: g for g in self.ir.get("groups", [])}
        grouped_nodes = {}
        for g_id in groups:
            grouped_nodes[g_id] = []
        ungrouped_nodes = []

        for node in self.ir.get("nodes", []):
            gid = node.get("group_id")
            if gid and gid in grouped_nodes:
                grouped_nodes[gid].append(node)
            else:
                ungrouped_nodes.append(node)

        # Layout parameters
        NODE_W = 250
        NODE_H = 85
        COL_GAP = 40
        ROW_GAP = 30
        GROUP_PAD = 40
        GROUP_HEADER = 50

        node_positions = {}  # node_id -> (x, y, w, h)
        
        current_group_x = 60
        current_group_y = 150
        max_row_height = 0

        # Render Group Containers and their nodes
        for gid, g_nodes in grouped_nodes.items():
            if not g_nodes:
                continue
            
            g_info = groups[gid]
            g_provider = g_info.get("provider", "generic")
            g_badge = "☁️" if g_provider == "aws" else "🔷" if g_provider == "azure" else "🟢" if g_provider == "gcp" else "☸️" if g_provider == "kubernetes" else "⬡"
            
            cols = min(3, max(1, math.ceil(math.sqrt(len(g_nodes)))))
            rows = math.ceil(len(g_nodes) / cols)
            
            gw = cols * NODE_W + (cols - 1) * COL_GAP + 2 * GROUP_PAD
            gh = rows * NODE_H + (rows - 1) * ROW_GAP + GROUP_PAD + GROUP_HEADER

            # Draw Group Container Box
            group_box_id = f"box_{gid}"
            g_colors = PALETTES.get(g_provider, PALETTES["generic"])["group"]
            self.elements.append({
                "id": group_box_id,
                "type": "rectangle",
                "x": current_group_x,
                "y": current_group_y,
                "width": gw,
                "height": gh,
                "angle": 0,
                "strokeColor": g_colors["stroke"],
                "backgroundColor": g_colors["bg"],
                "fillStyle": "solid",
                "strokeWidth": 2,
                "strokeStyle": "dashed",
                "roughness": 1,
                "opacity": 60,
                "groupIds": [gid],
                "roundness": {"type": 3},
                "seed": self.next_seed(),
                "version": 1,
                "versionNonce": 1,
                "isDeleted": False,
                "boundElements": [],
                "updated": 1,
                "link": None,
                "locked": False
            })

            # Group Label
            self.elements.append({
                "id": f"label_{gid}",
                "type": "text",
                "x": current_group_x + GROUP_PAD,
                "y": current_group_y + 15,
                "width": gw - (2 * GROUP_PAD),
                "height": 25,
                "angle": 0,
                "strokeColor": g_colors["stroke"],
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 1,
                "strokeStyle": "solid",
                "roughness": 1,
                "opacity": 100,
                "groupIds": [gid],
                "roundness": None,
                "seed": self.next_seed(),
                "version": 1,
                "versionNonce": 1,
                "isDeleted": False,
                "boundElements": None,
                "updated": 1,
                "link": None,
                "locked": False,
                "text": f"{g_badge} {g_info.get('label', gid)}",
                "fontSize": 16,
                "fontFamily": 1,
                "textAlign": "left",
                "verticalAlign": "top",
                "containerId": None,
                "originalText": f"{g_badge} {g_info.get('label', gid)}",
                "lineHeight": 1.25
            })

            # Position nodes inside this group
            for idx, node in enumerate(g_nodes):
                r = idx // cols
                c = idx % cols
                nx = current_group_x + GROUP_PAD + c * (NODE_W + COL_GAP)
                ny = current_group_y + GROUP_HEADER + r * (NODE_H + ROW_GAP)
                node_positions[node["id"]] = (nx, ny, NODE_W, NODE_H)
                self._render_node(node, nx, ny, NODE_W, NODE_H, [gid])

            current_group_x += gw + 60
            max_row_height = max(max_row_height, gh)
            if current_group_x > 1800:
                current_group_x = 60
                current_group_y += max_row_height + 60
                max_row_height = 0

        # Render Ungrouped / Standalone Nodes
        if ungrouped_nodes:
            if current_group_x != 60:
                current_group_x = 60
                current_group_y += max_row_height + 60

            cols = min(4, max(1, math.ceil(math.sqrt(len(ungrouped_nodes)))))
            rows = math.ceil(len(ungrouped_nodes) / cols)
            gw = cols * NODE_W + (cols - 1) * COL_GAP + 2 * GROUP_PAD
            gh = rows * NODE_H + (rows - 1) * ROW_GAP + GROUP_PAD + GROUP_HEADER

            # Container for standalone resources
            box_id = "box_standalone"
            self.elements.append({
                "id": box_id,
                "type": "rectangle",
                "x": current_group_x,
                "y": current_group_y,
                "width": gw,
                "height": gh,
                "angle": 0,
                "strokeColor": "#adb5bd",
                "backgroundColor": "#f8f9fa",
                "fillStyle": "solid",
                "strokeWidth": 1,
                "strokeStyle": "dashed",
                "roughness": 1,
                "opacity": 50,
                "groupIds": ["standalone"],
                "roundness": {"type": 3},
                "seed": self.next_seed(),
                "version": 1,
                "versionNonce": 1,
                "isDeleted": False,
                "boundElements": [],
                "updated": 1,
                "link": None,
                "locked": False
            })

            self.elements.append({
                "id": "label_standalone",
                "type": "text",
                "x": current_group_x + GROUP_PAD,
                "y": current_group_y + 15,
                "width": gw - (2 * GROUP_PAD),
                "height": 25,
                "angle": 0,
                "strokeColor": "#495057",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 1,
                "strokeStyle": "solid",
                "roughness": 1,
                "opacity": 100,
                "groupIds": ["standalone"],
                "roundness": None,
                "seed": self.next_seed(),
                "version": 1,
                "versionNonce": 1,
                "isDeleted": False,
                "boundElements": None,
                "updated": 1,
                "link": None,
                "locked": False,
                "text": "Services & Standalone Resources",
                "fontSize": 16,
                "fontFamily": 1,
                "textAlign": "left",
                "verticalAlign": "top",
                "containerId": None,
                "originalText": "Services & Standalone Resources",
                "lineHeight": 1.25
            })

            for idx, node in enumerate(ungrouped_nodes):
                r = idx // cols
                c = idx % cols
                nx = current_group_x + GROUP_PAD + c * (NODE_W + COL_GAP)
                ny = current_group_y + GROUP_HEADER + r * (NODE_H + ROW_GAP)
                node_positions[node["id"]] = (nx, ny, NODE_W, NODE_H)
                self._render_node(node, nx, ny, NODE_W, NODE_H, ["standalone"])

        # Render Edges / Connections
        for edge_idx, edge in enumerate(self.ir.get("edges", [])):
            src_id = edge["source"]
            dst_id = edge["target"]
            if src_id in node_positions and dst_id in node_positions:
                self._render_edge(edge_idx, edge, node_positions[src_id], node_positions[dst_id], src_id, dst_id)

        return {
            "type": "excalidraw",
            "version": 2,
            "source": "https://skills.sh/rhoribe/skills",
            "elements": self.elements,
            "appState": {
                "gridSize": 20,
                "viewBackgroundColor": "#ffffff"
            },
            "files": self.files
        }

    def _render_node(self, node: dict, x: float, y: float, w: float, h: float, group_ids: list):
        node_id = f"node_{node['id']}"
        text_id = f"text_{node['id']}"
        icon_id = f"icon_{node['id']}"
        node_group_ids = group_ids + [node_id]

        provider = node.get("provider", "generic")
        category = node.get("category", "management")
        colors = get_colors(provider, category)

        # Retrieve icon metadata and register file in Excalidraw
        icon = node.get("icon") or get_icon(provider, category, node.get("type", ""))
        file_id = f"file_{icon['key']}"
        if file_id not in self.files:
            self.files[file_id] = {
                "mimeType": "image/svg+xml",
                "id": file_id,
                "dataURL": icon["data_url"],
                "created": 1
            }

        # Node Container Box
        self.elements.append({
            "id": node_id,
            "type": "rectangle",
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "angle": 0,
            "strokeColor": colors["stroke"],
            "backgroundColor": colors["bg"],
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": node_group_ids,
            "roundness": {"type": 3},
            "seed": self.next_seed(),
            "version": 1,
            "versionNonce": 1,
            "isDeleted": False,
            "boundElements": [{"id": text_id, "type": "text"}],
            "updated": 1,
            "link": None,
            "locked": False
        })

        # Icon Image inside Node
        self.elements.append({
            "id": icon_id,
            "type": "image",
            "x": x + 12,
            "y": y + 20,
            "width": 44,
            "height": 44,
            "angle": 0,
            "strokeColor": "transparent",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": node_group_ids,
            "roundness": None,
            "seed": self.next_seed(),
            "version": 1,
            "versionNonce": 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "status": "saved",
            "fileId": file_id,
            "scale": [1, 1]
        })

        # Formatted Node Content
        display_type = node.get("display_type", node.get("type", "Resource"))
        name = node.get("name", "unnamed")
        props = node.get("properties", {})
        prop_str = f" ({next(iter(props.values()))})" if props else ""

        full_text = f"{name}\n[{display_type}]{prop_str}"

        # Label inside Node (offset right to leave space for icon)
        self.elements.append({
            "id": text_id,
            "type": "text",
            "x": x + 64,
            "y": y + 16,
            "width": w - 74,
            "height": h - 32,
            "angle": 0,
            "strokeColor": "#1e1e1e",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": node_group_ids,
            "roundness": None,
            "seed": self.next_seed(),
            "version": 1,
            "versionNonce": 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "text": full_text,
            "fontSize": 13,
            "fontFamily": 1,
            "textAlign": "left",
            "verticalAlign": "middle",
            "containerId": None,
            "originalText": full_text,
            "lineHeight": 1.25
        })


    def _render_edge(self, idx: int, edge: dict, src_pos, dst_pos, src_id: str, dst_id: str):
        sx, sy, sw, sh = src_pos
        dx, dy, dw, dh = dst_pos

        # Calculate anchor points (center points)
        start_x = sx + (sw / 2)
        start_y = sy + (sh / 2)
        end_x = dx + (dw / 2)
        end_y = dy + (dh / 2)

        # Offsets
        diff_x = end_x - start_x
        diff_y = end_y - start_y

        arrow_id = f"arrow_{idx}_{src_id}_{dst_id}"
        
        self.elements.append({
            "id": arrow_id,
            "type": "arrow",
            "x": start_x,
            "y": start_y,
            "width": abs(diff_x),
            "height": abs(diff_y),
            "angle": 0,
            "strokeColor": "#495057",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "roundness": {"type": 2},
            "seed": self.next_seed(),
            "version": 1,
            "versionNonce": 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "points": [[0, 0], [diff_x, diff_y]],
            "lastCommittedPoint": None,
            "startBinding": {
                "elementId": f"node_{src_id}",
                "focus": 0,
                "gap": 4
            },
            "endBinding": {
                "elementId": f"node_{dst_id}",
                "focus": 0,
                "gap": 4
            },
            "startArrowhead": None,
            "endArrowhead": "arrow"
        })


def main():
    parser = argparse.ArgumentParser(description="Generate Excalidraw JSON from IaC IR")
    parser.add_argument("input_ir", help="Path to IaC IR JSON file (or - for stdin)")
    parser.add_argument("-o", "--output", help="Path to output .excalidraw file")
    args = parser.parse_args()

    if args.input_ir == "-":
        data = json.load(sys.stdin)
    else:
        data = json.loads(Path(args.input_ir).read_text(encoding="utf-8"))

    generator = ExcalidrawGenerator(data)
    result = generator.generate()

    out_json = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(out_json, encoding="utf-8")
        print(f"[OK] Generated Excalidraw diagram at {args.output}")
    else:
        print(out_json)


if __name__ == "__main__":
    main()
