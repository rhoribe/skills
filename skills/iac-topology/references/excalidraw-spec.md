# Excalidraw JSON Schema & Diagramming Specification

This reference guide documents the Excalidraw v2 JSON format, layout coordinate mathematics, and styling guidelines implemented by `generate_excalidraw.py`.

---

## 1. Excalidraw JSON Document Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://skills.sh/rhoribe/skills",
  "elements": [
    ...
  ],
  "appState": {
    "gridSize": 20,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```

---

## 2. Supported Element Types

### A. Rectangles (`type: "rectangle"`)
Used for resource cards and container groupings:
- `roundness: {"type": 3}`: Produces rounded corner cards.
- `strokeStyle`: `"solid"` for resources, `"dashed"` for virtual network/subnet containers.
- `fillStyle`: `"solid"`.
- `opacity`: `100` for cards, `50-60` for background containers.

### B. Text (`type: "text"`)
- `containerId`: Associates text directly with a parent rectangle card.
- `fontSize`: `14` for node labels, `16` for container headers, `28` for document title.
- `textAlign`: `"center"` for cards, `"left"` for container headers.

### C. Arrows (`type: "arrow"`)
Used for relationships and network traffic flow:
- `startBinding` / `endBinding`: Binds arrow terminals to specific node element IDs.
- `points`: Relative coordinates `[[0, 0], [dx, dy]]`.
- `endArrowhead`: `"arrow"`.

---

## 3. Viewing & Editing Excalidraw Files

Generated `.excalidraw` files can be opened in:
- **Web**: Open [excalidraw.com](https://excalidraw.com) and drag & drop the file onto the canvas.
- **VS Code**: Install the *Excalidraw* extension by *pomdtr* to view and edit inline.
- **Obsidian**: Install the *Obsidian-Excalidraw* plugin.
