#!/usr/bin/env python3
"""
icons.py - Cloud Provider Vector Icons & Metadata Registry
Provides clean, self-contained SVG icons, Base64 data URLs, Draw.io shape bindings,
and Mermaid glyphs for AWS, Azure, Google Cloud (GCP), and Kubernetes.
"""

import base64
import xml.etree.ElementTree as ET


def _to_data_url(svg: str) -> str:
    """Encode SVG string to base64 Data URL."""
    b64 = base64.b64encode(svg.strip().encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"


# ─────────────────────────────────────────────────────────────────────────────
# Clean 64x64 Vector SVG Icons for Cloud Providers and Architectures
# ─────────────────────────────────────────────────────────────────────────────

ICONS_SVG = {
    # ── AWS ──
    "aws_logo": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#232F3E"/>
  <path d="M19 36c4 3 10 5 17 5 9 0 14-3 15-4 1-1 0-2-1-2s-1 0-3 1c-3 1-7 2-11 2-6 0-11-2-15-4-1 0-2 0-2 2z" fill="#FF9900"/>
  <path d="M49 39c1-1 3-1 4-1s-1 2-2 3c-1 1-2 1-2-2z" fill="#FF9900"/>
  <path d="M18 29c-1-3 1-6 4-6 4 0 5 3 5 6v2h-9zm15-4c-2 0-4 1-4 3v5h8v-5c0-2-2-3-4-3zm13 1c-1-2-3-2-4-2-3 0-4 2-4 5v4h8v-4c0-2 0-3 0-3z" fill="#FFFFFF"/>
</svg>""",

    "aws_compute": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#ED7100"/>
  <rect x="14" y="14" width="36" height="36" rx="6" fill="#FFFFFF" fill-opacity="0.2"/>
  <path d="M22 22h20v20H22z" fill="#FFFFFF"/>
  <path d="M26 10v4m12-4v4M26 50v4m12-4v4M10 26h4m-4 12h4M50 26h4m-4 12h4" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
  <path d="M28 28h8v8h-8z" fill="#ED7100"/>
</svg>""",

    "aws_database": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#3B48CC"/>
  <ellipse cx="32" cy="20" rx="18" ry="7" fill="#FFFFFF"/>
  <path d="M14 20v12c0 3.8 8.1 7 18 7s18-3.2 18-7V20" fill="none" stroke="#FFFFFF" stroke-width="4"/>
  <path d="M14 32v12c0 3.8 8.1 7 18 7s18-3.2 18-7V32" fill="none" stroke="#FFFFFF" stroke-width="4"/>
  <ellipse cx="32" cy="20" rx="10" ry="3.8" fill="#3B48CC"/>
</svg>""",

    "aws_storage": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#7AA116"/>
  <path d="M16 18l16-6 16 6v8L32 32 16 26v-8z" fill="#FFFFFF"/>
  <path d="M16 26l16 6 16-6v18l-16 8-16-8V26z" fill="#FFFFFF" fill-opacity="0.85"/>
  <path d="M32 32v26" stroke="#7AA116" stroke-width="3"/>
  <circle cx="32" cy="22" r="3" fill="#7AA116"/>
</svg>""",

    "aws_network": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#8C4FFF"/>
  <circle cx="32" cy="18" r="6" fill="#FFFFFF"/>
  <circle cx="18" cy="44" r="6" fill="#FFFFFF"/>
  <circle cx="46" cy="44" r="6" fill="#FFFFFF"/>
  <path d="M32 24v8m0 0l-14 6m14-6l14 6" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
  <circle cx="32" cy="32" r="3" fill="#FFFFFF"/>
</svg>""",

    "aws_security": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#DD344C"/>
  <path d="M32 12l18 7v13c0 13-8 20-18 24-10-4-18-11-18-24V19l18-7z" fill="#FFFFFF"/>
  <path d="M32 24v16m-5-8h10" stroke="#DD344C" stroke-width="4" stroke-linecap="round"/>
</svg>""",

    "aws_messaging": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#E7157B"/>
  <rect x="14" y="20" width="36" height="24" rx="4" fill="#FFFFFF"/>
  <path d="M14 22l18 13 18-13" fill="none" stroke="#E7157B" stroke-width="3"/>
  <circle cx="32" cy="48" r="3" fill="#FFFFFF"/>
  <circle cx="44" cy="48" r="3" fill="#FFFFFF"/>
  <circle cx="20" cy="48" r="3" fill="#FFFFFF"/>
</svg>""",

    # ── Azure ──
    "azure_logo": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#0078D4"/>
  <path d="M16 46l13-30h10L25 46H16z" fill="#50E6FF"/>
  <path d="M26 36l6-14 12 24H33l-7-10z" fill="#FFFFFF"/>
  <path d="M33 46l6-8 9 8H33z" fill="#50E6FF"/>
</svg>""",

    "azure_compute": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#0078D4"/>
  <rect x="14" y="16" width="36" height="24" rx="4" fill="#FFFFFF"/>
  <rect x="18" y="20" width="28" height="16" rx="2" fill="#0078D4"/>
  <path d="M24 46h16M32 40v6" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>
  <circle cx="32" cy="28" r="4" fill="#50E6FF"/>
</svg>""",

    "azure_database": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#005BA1"/>
  <ellipse cx="32" cy="18" rx="18" ry="6" fill="#50E6FF"/>
  <path d="M14 18v14c0 3.3 8.1 6 18 6s18-2.7 18-6V18" fill="none" stroke="#FFFFFF" stroke-width="4"/>
  <path d="M14 32v14c0 3.3 8.1 6 18 6s18-2.7 18-6V32" fill="none" stroke="#FFFFFF" stroke-width="4"/>
</svg>""",

    "azure_storage": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#107C41"/>
  <rect x="14" y="14" width="36" height="15" rx="3" fill="#FFFFFF"/>
  <rect x="14" y="33" width="36" height="15" rx="3" fill="#FFFFFF"/>
  <circle cx="22" cy="21.5" r="3" fill="#107C41"/>
  <circle cx="22" cy="40.5" r="3" fill="#107C41"/>
  <path d="M30 21.5h14M30 40.5h14" stroke="#107C41" stroke-width="3" stroke-linecap="round"/>
</svg>""",

    "azure_network": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#004E8C"/>
  <rect x="14" y="14" width="14" height="14" rx="3" fill="#50E6FF"/>
  <rect x="36" y="14" width="14" height="14" rx="3" fill="#FFFFFF"/>
  <rect x="25" y="36" width="14" height="14" rx="3" fill="#50E6FF"/>
  <path d="M21 28v12h11M43 28v6H32" stroke="#FFFFFF" stroke-width="3"/>
</svg>""",

    "azure_security": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#5C2D91"/>
  <circle cx="28" cy="30" r="10" fill="none" stroke="#FFFFFF" stroke-width="4"/>
  <path d="M36 30h14v8h-6v-4h-4v-4" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>
</svg>""",

    "azure_messaging": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#D83B01"/>
  <circle cx="20" cy="32" r="6" fill="#FFFFFF"/>
  <circle cx="44" cy="32" r="6" fill="#FFFFFF"/>
  <path d="M26 32h12" stroke="#FFFFFF" stroke-width="4" stroke-dasharray="2 2"/>
  <path d="M32 20l6 12-6 12" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linejoin="round"/>
</svg>""",

    # ── GCP ──
    "gcp_logo": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#FFFFFF" stroke="#DADCE0" stroke-width="2"/>
  <path d="M39 21c-5-4-12-3-15 2l-7 13c-2 4 0 9 5 11l4 2 8-15 5 1-1-14z" fill="#EA4335"/>
  <path d="M42 24l-3 6 8 13 4-2c4-2 5-8 3-12l-7-8-5 3z" fill="#4285F4"/>
  <path d="M21 47l9 5 9-5-4-8-10-1-4 9z" fill="#34A853"/>
  <path d="M24 33l5-9 6 3 3 8-14-2z" fill="#FBBC05"/>
</svg>""",

    "gcp_compute": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#4285F4"/>
  <circle cx="32" cy="32" r="16" fill="#FFFFFF"/>
  <path d="M32 22v20M22 32h20" stroke="#4285F4" stroke-width="4" stroke-linecap="round"/>
  <circle cx="32" cy="32" r="5" fill="#34A853"/>
</svg>""",

    "gcp_database": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#34A853"/>
  <ellipse cx="32" cy="18" rx="18" ry="6" fill="#FFFFFF"/>
  <path d="M14 18v14c0 3.3 8.1 6 18 6s18-2.7 18-6V18" fill="none" stroke="#FFFFFF" stroke-width="4"/>
  <path d="M14 32v14c0 3.3 8.1 6 18 6s18-2.7 18-6V32" fill="none" stroke="#FFFFFF" stroke-width="4"/>
  <circle cx="32" cy="32" r="3" fill="#FFFFFF"/>
</svg>""",

    "gcp_storage": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#FBBC05"/>
  <path d="M16 20h32v26H16z" rx="3" fill="#FFFFFF"/>
  <path d="M16 28h32" stroke="#FBBC05" stroke-width="3"/>
  <circle cx="24" cy="38" r="3" fill="#4285F4"/>
  <circle cx="40" cy="38" r="3" fill="#EA4335"/>
</svg>""",

    "gcp_network": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#1A73E8"/>
  <circle cx="32" cy="32" r="16" fill="none" stroke="#FFFFFF" stroke-width="3"/>
  <ellipse cx="32" cy="32" rx="7" ry="16" fill="none" stroke="#FFFFFF" stroke-width="3"/>
  <path d="M16 32h32" stroke="#FFFFFF" stroke-width="3"/>
</svg>""",

    "gcp_security": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#673AB7"/>
  <path d="M32 14l16 6v12c0 11-7 18-16 22-9-4-16-11-16-22V20l16-6z" fill="#FFFFFF"/>
  <circle cx="32" cy="32" r="4" fill="#673AB7"/>
  <path d="M32 36v6" stroke="#673AB7" stroke-width="3" stroke-linecap="round"/>
</svg>""",

    "gcp_messaging": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#EA4335"/>
  <circle cx="32" cy="32" r="8" fill="#FFFFFF"/>
  <circle cx="16" cy="20" r="5" fill="#FFFFFF"/>
  <circle cx="48" cy="20" r="5" fill="#FFFFFF"/>
  <circle cx="32" cy="50" r="5" fill="#FFFFFF"/>
  <path d="M20 23l8 6m8-6l-8 6m0 8v8" stroke="#FFFFFF" stroke-width="3"/>
</svg>""",

    # ── Kubernetes ──
    "kubernetes_logo": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#326CE5"/>
  <circle cx="32" cy="32" r="18" fill="none" stroke="#FFFFFF" stroke-width="3"/>
  <circle cx="32" cy="32" r="7" fill="#FFFFFF"/>
  <path d="M32 14v11m0 14v11M14 32h11m14 0h11M19 19l8 8m10 10l8 8M19 45l8-8m10-10l8-8" stroke="#FFFFFF" stroke-width="3"/>
</svg>""",

    "kubernetes_compute": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#326CE5"/>
  <rect x="16" y="16" width="14" height="14" rx="3" fill="#FFFFFF"/>
  <rect x="34" y="16" width="14" height="14" rx="3" fill="#FFFFFF"/>
  <rect x="16" y="34" width="14" height="14" rx="3" fill="#FFFFFF"/>
  <rect x="34" y="34" width="14" height="14" rx="3" fill="#50E6FF"/>
</svg>""",

    "kubernetes_network": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#009688"/>
  <circle cx="20" cy="32" r="6" fill="#FFFFFF"/>
  <circle cx="44" cy="22" r="6" fill="#FFFFFF"/>
  <circle cx="44" cy="42" r="6" fill="#FFFFFF"/>
  <path d="M26 32l12-8m-12 8l12 8" stroke="#FFFFFF" stroke-width="3"/>
</svg>""",

    "kubernetes_storage": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#4CAF50"/>
  <path d="M20 20h24v24H20z" fill="#FFFFFF"/>
  <path d="M16 26l16-8 16 8v16l-16 8-16-8V26z" fill="none" stroke="#FFFFFF" stroke-width="3"/>
  <circle cx="32" cy="32" r="4" fill="#4CAF50"/>
</svg>""",

    # ── Generic / Fallback ──
    "generic_cloud": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#495057"/>
  <path d="M46 38c3 0 6-2 6-5s-2-5-5-5h-1c-1-6-6-10-12-10-5 0-10 3-12 8h-1c-4 0-7 3-7 7s3 7 7 7h25z" fill="#FFFFFF"/>
</svg>""",

    "generic_compute": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#1C7ED6"/>
  <rect x="16" y="16" width="32" height="32" rx="4" fill="#FFFFFF"/>
  <rect x="22" y="22" width="20" height="20" rx="2" fill="#1C7ED6"/>
  <path d="M28 12v4m8-4v4M28 48v4m8-4v4M12 28h4m-4 8h4M48 28h4m-4 8h4" stroke="#FFFFFF" stroke-width="3"/>
</svg>""",

    "generic_database": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#099268"/>
  <ellipse cx="32" cy="18" rx="18" ry="6" fill="#FFFFFF"/>
  <path d="M14 18v14c0 3.3 8.1 6 18 6s18-2.7 18-6V18" fill="none" stroke="#FFFFFF" stroke-width="4"/>
  <path d="M14 32v14c0 3.3 8.1 6 18 6s18-2.7 18-6V32" fill="none" stroke="#FFFFFF" stroke-width="4"/>
</svg>""",

    "generic_storage": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#F08C00"/>
  <path d="M16 20h32v24H16z" fill="#FFFFFF"/>
  <circle cx="32" cy="32" r="5" fill="#F08C00"/>
  <path d="M24 20v-4h16v4" fill="none" stroke="#FFFFFF" stroke-width="3"/>
</svg>""",

    "generic_network": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#495057"/>
  <circle cx="20" cy="24" r="6" fill="#FFFFFF"/>
  <circle cx="44" cy="24" r="6" fill="#FFFFFF"/>
  <circle cx="32" cy="44" r="6" fill="#FFFFFF"/>
  <path d="M20 24l12 20 12-20" stroke="#FFFFFF" stroke-width="3"/>
</svg>""",

    "generic_security": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#7048E8"/>
  <rect x="20" y="28" width="24" height="20" rx="3" fill="#FFFFFF"/>
  <path d="M26 28v-8c0-3.3 2.7-6 6-6s6 2.7 6 6v8" fill="none" stroke="#FFFFFF" stroke-width="4"/>
  <circle cx="32" cy="38" r="3" fill="#7048E8"/>
</svg>""",

    "generic_messaging": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#AE3EC9"/>
  <rect x="16" y="20" width="32" height="24" rx="3" fill="#FFFFFF"/>
  <path d="M16 22l16 12 16-12" fill="none" stroke="#AE3EC9" stroke-width="3"/>
</svg>"""
}


# Pre-computed Data URLs for fast embedding in Excalidraw and Draw.io
ICONS_DATA_URL = {k: _to_data_url(v) for k, v in ICONS_SVG.items()}


# Metadata mapping: provider & category -> icon key, emoji, FontAwesome class, Draw.io shape
ICON_METADATA = {
    "aws": {
        "badge": "☁️",
        "fa_prefix": "fa:fa-aws",
        "categories": {
            "compute": {"key": "aws_compute", "emoji": "💻", "fa": "fa:fa-server", "drawio": "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;"},
            "database": {"key": "aws_database", "emoji": "🗄️", "fa": "fa:fa-database", "drawio": "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.rds;"},
            "storage": {"key": "aws_storage", "emoji": "🪣", "fa": "fa:fa-cube", "drawio": "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.s3;"},
            "network": {"key": "aws_network", "emoji": "🌐", "fa": "fa:fa-network-wired", "drawio": "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.vpc;"},
            "security": {"key": "aws_security", "emoji": "🔒", "fa": "fa:fa-shield-alt", "drawio": "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.iam;"},
            "messaging": {"key": "aws_messaging", "emoji": "⚡", "fa": "fa:fa-envelope", "drawio": "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.sqs;"},
            "management": {"key": "aws_compute", "emoji": "⚙️", "fa": "fa:fa-cogs", "drawio": "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudwatch;"}
        }
    },
    "azure": {
        "badge": "🔷",
        "fa_prefix": "fa:fa-microsoft",
        "categories": {
            "compute": {"key": "azure_compute", "emoji": "💻", "fa": "fa:fa-server", "drawio": "shape=mxgraph.azure2.compute.virtual_machine;"},
            "database": {"key": "azure_database", "emoji": "🗄️", "fa": "fa:fa-database", "drawio": "shape=mxgraph.azure2.databases.sql_database;"},
            "storage": {"key": "azure_storage", "emoji": "📦", "fa": "fa:fa-archive", "drawio": "shape=mxgraph.azure2.storage.storage_accounts;"},
            "network": {"key": "azure_network", "emoji": "🌐", "fa": "fa:fa-network-wired", "drawio": "shape=mxgraph.azure2.networking.virtual_networks;"},
            "security": {"key": "azure_security", "emoji": "🔒", "fa": "fa:fa-key", "drawio": "shape=mxgraph.azure2.security.key_vaults;"},
            "messaging": {"key": "azure_messaging", "emoji": "⚡", "fa": "fa:fa-bolt", "drawio": "shape=mxgraph.azure2.integration.service_bus;"},
            "management": {"key": "azure_compute", "emoji": "⚙️", "fa": "fa:fa-cogs", "drawio": "shape=mxgraph.azure2.management_governance.monitor;"}
        }
    },
    "gcp": {
        "badge": "🟢",
        "fa_prefix": "fa:fa-google",
        "categories": {
            "compute": {"key": "gcp_compute", "emoji": "💻", "fa": "fa:fa-microchip", "drawio": "shape=mxgraph.gcp2.compute_engine;"},
            "database": {"key": "gcp_database", "emoji": "🗄️", "fa": "fa:fa-database", "drawio": "shape=mxgraph.gcp2.cloud_sql;"},
            "storage": {"key": "gcp_storage", "emoji": "🪣", "fa": "fa:fa-archive", "drawio": "shape=mxgraph.gcp2.cloud_storage;"},
            "network": {"key": "gcp_network", "emoji": "🌐", "fa": "fa:fa-network-wired", "drawio": "shape=mxgraph.gcp2.vpc;"},
            "security": {"key": "gcp_security", "emoji": "🔒", "fa": "fa:fa-shield-alt", "drawio": "shape=mxgraph.gcp2.cloud_iam;"},
            "messaging": {"key": "gcp_messaging", "emoji": "⚡", "fa": "fa:fa-paper-plane", "drawio": "shape=mxgraph.gcp2.cloud_pub_sub;"},
            "management": {"key": "gcp_compute", "emoji": "⚙️", "fa": "fa:fa-cogs", "drawio": "shape=mxgraph.gcp2.cloud_monitoring;"}
        }
    },
    "kubernetes": {
        "badge": "☸️",
        "fa_prefix": "fa:fa-dharmachakra",
        "categories": {
            "compute": {"key": "kubernetes_compute", "emoji": "📦", "fa": "fa:fa-cubes", "drawio": "shape=mxgraph.kubernetes.pod;"},
            "database": {"key": "generic_database", "emoji": "🗄️", "fa": "fa:fa-database", "drawio": "shape=mxgraph.kubernetes.statefulset;"},
            "storage": {"key": "kubernetes_storage", "emoji": "💾", "fa": "fa:fa-hdd", "drawio": "shape=mxgraph.kubernetes.pv;"},
            "network": {"key": "kubernetes_network", "emoji": "🌐", "fa": "fa:fa-route", "drawio": "shape=mxgraph.kubernetes.svc;"},
            "security": {"key": "generic_security", "emoji": "🔒", "fa": "fa:fa-user-shield", "drawio": "shape=mxgraph.kubernetes.secret;"},
            "messaging": {"key": "generic_messaging", "emoji": "⚡", "fa": "fa:fa-bolt", "drawio": "shape=mxgraph.kubernetes.pod;"},
            "management": {"key": "kubernetes_logo", "emoji": "☸️", "fa": "fa:fa-dharmachakra", "drawio": "shape=mxgraph.kubernetes.k8s;"}
        }
    },
    "generic": {
        "badge": "☁️",
        "fa_prefix": "fa:fa-cloud",
        "categories": {
            "compute": {"key": "generic_compute", "emoji": "💻", "fa": "fa:fa-server", "drawio": ""},
            "database": {"key": "generic_database", "emoji": "🗄️", "fa": "fa:fa-database", "drawio": ""},
            "storage": {"key": "generic_storage", "emoji": "📦", "fa": "fa:fa-box", "drawio": ""},
            "network": {"key": "generic_network", "emoji": "🌐", "fa": "fa:fa-network-wired", "drawio": ""},
            "security": {"key": "generic_security", "emoji": "🔒", "fa": "fa:fa-shield-alt", "drawio": ""},
            "messaging": {"key": "generic_messaging", "emoji": "⚡", "fa": "fa:fa-envelope", "drawio": ""},
            "management": {"key": "generic_cloud", "emoji": "⚙️", "fa": "fa:fa-cogs", "drawio": ""}
        }
    }
}


def get_icon(provider: str, category: str = "management", res_type: str = "") -> dict:
    """
    Retrieve full icon metadata for a given cloud provider and category.
    Returns:
        dict with: key, emoji, fa, drawio, svg, data_url, provider_badge
    """
    p_data = ICON_METADATA.get(provider.lower(), ICON_METADATA["generic"])
    badge = p_data.get("badge", "☁️")
    cats = p_data.get("categories", ICON_METADATA["generic"]["categories"])
    cat_info = cats.get(category.lower(), cats.get("management", {}))

    key = cat_info.get("key", "generic_cloud")
    svg = ICONS_SVG.get(key, ICONS_SVG["generic_cloud"])
    data_url = ICONS_DATA_URL.get(key, ICONS_DATA_URL["generic_cloud"])

    return {
        "key": key,
        "provider": provider.lower(),
        "category": category.lower(),
        "provider_badge": badge,
        "emoji": cat_info.get("emoji", "☁️"),
        "fa": cat_info.get("fa", "fa:fa-cloud"),
        "drawio_shape": cat_info.get("drawio", ""),
        "svg": svg,
        "data_url": data_url
    }
