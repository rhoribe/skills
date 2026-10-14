#!/usr/bin/env bash
# ==============================================================================
# iac_topology.sh - Universal IaC Topology Diagram Generator CLI
# Supports: Terraform, AWS CloudFormation, Azure Bicep, Ansible, Kubernetes
# Exports: Excalidraw (.excalidraw), Draw.io (.drawio), Mermaid (.mmd)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD=""

# Locate python3
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "[ERROR] Python 3 is required to run iac_topology.sh but was not found in PATH." >&2
  exit 1
fi

TARGET_PATH=""
OUTPUT_DIR="./diagrams"
FORMAT="all"
TITLE="Cloud Infrastructure Topology"
LAYOUT="TD"
VERBOSE=false

show_help() {
  cat << 'EOF'
Usage: iac_topology.sh <target-iac-path> [options]

Arguments:
  <target-iac-path>       File or directory containing IaC code (Terraform, CloudFormation,
                          Bicep, Ansible, or Kubernetes manifests).

Options:
  -f, --format FORMAT     Output format: 'excalidraw', 'drawio', 'mermaid', or 'all' (default: all)
  -o, --output-dir DIR    Directory where diagrams will be saved (default: ./diagrams)
  --title TITLE           Title displayed on top of the diagrams
  --layout ORIENTATION    Layout orientation: 'TD' (top-down) or 'LR' (left-right) (default: TD)
  -v, --verbose           Display detailed processing logs
  -h, --help              Show this help message

Examples:
  ./scripts/iac_topology.sh ./infra/terraform/
  ./scripts/iac_topology.sh template.yaml --format excalidraw
  ./scripts/iac_topology.sh main.bicep --format drawio --output-dir ./docs/architecture
  ./scripts/iac_topology.sh playbook.yml --format all --title "Production App Topology"
EOF
}

# Parse CLI options
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      show_help
      exit 0
      ;;
    -f|--format)
      FORMAT="$2"
      shift 2
      ;;
    -o|--output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --title)
      TITLE="$2"
      shift 2
      ;;
    --layout)
      LAYOUT="$2"
      shift 2
      ;;
    -v|--verbose)
      VERBOSE=true
      shift
      ;;
    -*)
      echo "[ERROR] Unknown option: $1" >&2
      show_help
      exit 1
      ;;
    *)
      if [[ -z "$TARGET_PATH" ]]; then
        TARGET_PATH="$1"
      else
        echo "[ERROR] Unexpected argument: $1" >&2
        show_help
        exit 1
      fi
      shift
      ;;
  esac
done

if [[ -z "$TARGET_PATH" ]]; then
  echo "[ERROR] Missing target IaC file or directory path." >&2
  show_help
  exit 1
fi

if [[ ! -e "$TARGET_PATH" ]]; then
  echo "[ERROR] Path does not exist: $TARGET_PATH" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
BASE_NAME="$(basename "$TARGET_PATH")"
BASE_NAME="${BASE_NAME%.*}"
[[ "$BASE_NAME" == "" || "$BASE_NAME" == "." ]] && BASE_NAME="topology"

TMP_IR="$(mktemp "${TMPDIR:-/tmp}/iac_ir_XXXXXX.json")"
trap 'rm -f "$TMP_IR"' EXIT

echo "==> [1/3] Parsing Infrastructure as Code from: $TARGET_PATH"
"$PYTHON_CMD" "$SCRIPT_DIR/parse_iac.py" "$TARGET_PATH" --title "$TITLE" -o "$TMP_IR"

if [[ "$VERBOSE" == "true" ]]; then
  echo "--- Parsed Intermediate Representation ---"
  cat "$TMP_IR"
  echo "------------------------------------------"
fi

echo "==> [2/3] Generating topology diagrams (Format: $FORMAT)..."

OUT_EXCALIDRAW="$OUTPUT_DIR/${BASE_NAME}.excalidraw"
OUT_DRAWIO="$OUTPUT_DIR/${BASE_NAME}.drawio"
OUT_MERMAID="$OUTPUT_DIR/${BASE_NAME}.mmd"

case "$FORMAT" in
  excalidraw)
    "$PYTHON_CMD" "$SCRIPT_DIR/generate_excalidraw.py" "$TMP_IR" -o "$OUT_EXCALIDRAW"
    ;;
  drawio)
    "$PYTHON_CMD" "$SCRIPT_DIR/generate_drawio.py" "$TMP_IR" -o "$OUT_DRAWIO"
    ;;
  mermaid)
    "$PYTHON_CMD" "$SCRIPT_DIR/generate_mermaid.py" "$TMP_IR" -o "$OUT_MERMAID" --orientation "$LAYOUT"
    ;;
  all)
    "$PYTHON_CMD" "$SCRIPT_DIR/generate_excalidraw.py" "$TMP_IR" -o "$OUT_EXCALIDRAW"
    "$PYTHON_CMD" "$SCRIPT_DIR/generate_drawio.py" "$TMP_IR" -o "$OUT_DRAWIO"
    "$PYTHON_CMD" "$SCRIPT_DIR/generate_mermaid.py" "$TMP_IR" -o "$OUT_MERMAID" --orientation "$LAYOUT"
    ;;
  *)
    echo "[ERROR] Unsupported format '$FORMAT'. Allowed: excalidraw, drawio, mermaid, all" >&2
    exit 1
    ;;
esac

echo "==> [3/3] Topology Generation Completed Successfully!"
echo ""
echo "Output files in $OUTPUT_DIR:"
[[ "$FORMAT" == "excalidraw" || "$FORMAT" == "all" ]] && echo "  - Excalidraw: $OUT_EXCALIDRAW (Open in excalidraw.com or VSCode Excalidraw)"
[[ "$FORMAT" == "drawio" || "$FORMAT" == "all" ]] && echo "  - Draw.io:    $OUT_DRAWIO (Open in app.diagrams.net or Draw.io desktop)"
[[ "$FORMAT" == "mermaid" || "$FORMAT" == "all" ]] && echo "  - Mermaid:    $OUT_MERMAID (Preview in Markdown, GitHub, or Mermaid Live)"
echo ""
