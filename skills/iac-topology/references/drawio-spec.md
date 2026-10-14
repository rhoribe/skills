# Draw.io / mxGraph XML Schema Specification

This reference guide documents the Draw.io (`.drawio` / `mxGraphModel`) XML schema and style parameters implemented by `generate_drawio.py`.

---

## 1. Document Structure

A native Draw.io XML file adheres to the following root hierarchy:

```xml
<mxfile host="Electron" agent="skills.sh/iac-topology" version="21.0.0" type="device">
  <diagram id="topology-diagram" name="IaC Topology">
    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1600" pageHeight="1000" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- Container swimlanes, vertices, and connectors -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

## 2. Cell Elements & Styles

### Swimlane Containers (VPC, Subnet, Resource Groups)
```xml
<mxCell id="group_vpc" value="⬡ VPC: Production" 
        style="swimlane;whiteSpace=wrap;html=1;startSize=28;fillColor=#FFF9DB;strokeColor=#F76707;strokeWidth=2;fontColor=#333333;fontStyle=1;rounded=1;shadow=0;" 
        vertex="1" parent="1">
  <mxGeometry x="40" y="110" width="600" height="350" as="geometry" />
</mxCell>
```

### Resource Vertices (Compute, DB, Storage)
```xml
<mxCell id="node_web" value="&lt;b&gt;web-server&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#444444&quot;&gt;[EC2 Instance]&lt;/font&gt;" 
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE8CC;strokeColor=#D9480F;strokeWidth=2;fontColor=#212529;shadow=0;" 
        vertex="1" parent="group_vpc">
  <mxGeometry x="35" y="45" width="210" height="80" as="geometry" />
</mxCell>
```

### Orthogonal Edge Connectors
```xml
<mxCell id="edge_1" value="depends_on" 
        style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#495057;strokeWidth=2;endArrow=classic;endFill=1;" 
        edge="1" source="node_web" target="node_db" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

---

## 3. Viewing & Editing Draw.io Files

- **Web Browser**: Open [app.diagrams.net](https://app.diagrams.net/) and choose "Open Existing Diagram".
- **VS Code**: Install the *Draw.io Integration* extension (`hediet.vscode-drawio`) to edit `.drawio` files natively inside the editor.
- **Desktop**: Install the official Draw.io Desktop client for Linux, macOS, or Windows.
