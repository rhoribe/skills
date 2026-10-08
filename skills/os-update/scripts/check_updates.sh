#!/usr/bin/env bash
# ==============================================================================
# check_updates.sh - Safe read-only update inspector
# Checks pending system and package updates without applying modifications.
# Supports: Linux (APT, DNF, Pacman, Zypper, APK, Snap, Flatpak) & macOS (softwareupdate, Brew, MAS)
# ==============================================================================
set -euo pipefail

DO_REFRESH=false
OUTPUT_JSON=false

for arg in "$@"; do
  case "$arg" in
    --refresh)
      DO_REFRESH=true
      ;;
    --json)
      OUTPUT_JSON=true
      ;;
    -h|--help)
      echo "Usage: $0 [--refresh] [--json]"
      echo "  --refresh : Refresh package repository indexes before checking (may require sudo on Linux)"
      echo "  --json    : Output summary in JSON format"
      exit 0
      ;;
  esac
done

TOTAL_PENDING=0
SUMMARY_DETAILS=()

log_info() {
  if [ "$OUTPUT_JSON" = false ]; then
    echo "$@"
  fi
}

# ------------------------------------------------------------------------------
# APT (Debian, Ubuntu, etc.)
# ------------------------------------------------------------------------------
APT_COUNT=0
APT_PKGS=""
if command -v apt >/dev/null 2>&1 || command -v apt-get >/dev/null 2>&1; then
  log_info "==> Checking APT updates..."
  if [ "$DO_REFRESH" = true ]; then
    if [ "$(id -u)" -eq 0 ]; then
      apt-get update -qq 2>/dev/null || true
    elif command -v sudo >/dev/null 2>&1; then
      sudo apt-get update -qq 2>/dev/null || true
    fi
  fi

  if command -v apt >/dev/null 2>&1; then
    APT_LIST="$(apt list --upgradable 2>/dev/null | grep -v 'Listing\.\.\.' || true)"
    if [ -n "$APT_LIST" ]; then
      APT_COUNT="$(echo "$APT_LIST" | grep -c . || true)"
      APT_PKGS="$(echo "$APT_LIST" | head -n 30)"
    fi
  fi
  TOTAL_PENDING=$((TOTAL_PENDING + APT_COUNT))
fi

# ------------------------------------------------------------------------------
# DNF (Fedora, RHEL, CentOS)
# ------------------------------------------------------------------------------
DNF_COUNT=0
DNF_PKGS=""
if command -v dnf >/dev/null 2>&1; then
  log_info "==> Checking DNF updates..."
  if [ "$DO_REFRESH" = true ]; then
    dnf makecache -q 2>/dev/null || true
  fi
  # DNF check-update returns exit code 100 if updates are available, 0 if none
  set +e
  DNF_RAW="$(dnf check-update -q 2>/dev/null)"
  DNF_EXIT=$?
  set -e
  if [ "$DNF_EXIT" -eq 100 ] && [ -n "$DNF_RAW" ]; then
    DNF_COUNT="$(echo "$DNF_RAW" | grep -v '^$' | grep -v 'Last metadata expiration' | grep -c . || true)"
    DNF_PKGS="$(echo "$DNF_RAW" | head -n 30)"
  fi
  TOTAL_PENDING=$((TOTAL_PENDING + DNF_COUNT))
fi

# ------------------------------------------------------------------------------
# Pacman (Arch Linux, Manjaro)
# ------------------------------------------------------------------------------
PACMAN_COUNT=0
PACMAN_PKGS=""
if command -v pacman >/dev/null 2>&1; then
  log_info "==> Checking Pacman updates..."
  if command -v checkupdates >/dev/null 2>&1; then
    set +e
    PACMAN_RAW="$(checkupdates 2>/dev/null)"
    set -e
    if [ -n "$PACMAN_RAW" ]; then
      PACMAN_COUNT="$(echo "$PACMAN_RAW" | grep -c . || true)"
      PACMAN_PKGS="$(echo "$PACMAN_RAW" | head -n 30)"
    fi
  else
    set +e
    PACMAN_RAW="$(pacman -Qu 2>/dev/null)"
    set -e
    if [ -n "$PACMAN_RAW" ]; then
      PACMAN_COUNT="$(echo "$PACMAN_RAW" | grep -c . || true)"
      PACMAN_PKGS="$(echo "$PACMAN_RAW" | head -n 30)"
    fi
  fi
  TOTAL_PENDING=$((TOTAL_PENDING + PACMAN_COUNT))
fi

# ------------------------------------------------------------------------------
# Zypper (openSUSE)
# ------------------------------------------------------------------------------
ZYPPER_COUNT=0
ZYPPER_PKGS=""
if command -v zypper >/dev/null 2>&1; then
  log_info "==> Checking Zypper updates..."
  set +e
  ZYPPER_RAW="$(zypper list-updates -t package 2>/dev/null | grep -E '^v ' || true)"
  set -e
  if [ -n "$ZYPPER_RAW" ]; then
    ZYPPER_COUNT="$(echo "$ZYPPER_RAW" | grep -c . || true)"
    ZYPPER_PKGS="$(echo "$ZYPPER_RAW" | head -n 30)"
  fi
  TOTAL_PENDING=$((TOTAL_PENDING + ZYPPER_COUNT))
fi

# ------------------------------------------------------------------------------
# macOS softwareupdate
# ------------------------------------------------------------------------------
MACOS_SYS_COUNT=0
MACOS_SYS_PKGS=""
if command -v softwareupdate >/dev/null 2>&1; then
  log_info "==> Checking macOS System Software updates..."
  set +e
  SW_RAW="$(softwareupdate -l 2>&1 || true)"
  set -e
  if echo "$SW_RAW" | grep -qi "Software Update found the following"; then
    MACOS_SYS_COUNT="$(echo "$SW_RAW" | grep -c '^\* ' || true)"
    MACOS_SYS_PKGS="$(echo "$SW_RAW" | grep -E '^\* |Title:' | head -n 20 || true)"
  fi
  TOTAL_PENDING=$((TOTAL_PENDING + MACOS_SYS_COUNT))
fi

# ------------------------------------------------------------------------------
# Homebrew (macOS & Linux)
# ------------------------------------------------------------------------------
BREW_COUNT=0
BREW_PKGS=""
if command -v brew >/dev/null 2>&1; then
  log_info "==> Checking Homebrew updates..."
  if [ "$DO_REFRESH" = true ]; then
    brew update >/dev/null 2>&1 || true
  fi
  set +e
  BREW_RAW="$(brew outdated --verbose 2>/dev/null || true)"
  set -e
  if [ -n "$BREW_RAW" ]; then
    BREW_COUNT="$(echo "$BREW_RAW" | grep -c . || true)"
    BREW_PKGS="$(echo "$BREW_RAW" | head -n 30)"
  fi
  TOTAL_PENDING=$((TOTAL_PENDING + BREW_COUNT))
fi

# ------------------------------------------------------------------------------
# Mac App Store CLI (mas)
# ------------------------------------------------------------------------------
MAS_COUNT=0
MAS_PKGS=""
if command -v mas >/dev/null 2>&1; then
  log_info "==> Checking Mac App Store updates..."
  set +e
  MAS_RAW="$(mas outdated 2>/dev/null || true)"
  set -e
  if [ -n "$MAS_RAW" ]; then
    MAS_COUNT="$(echo "$MAS_RAW" | grep -c . || true)"
    MAS_PKGS="$(echo "$MAS_RAW" | head -n 20)"
  fi
  TOTAL_PENDING=$((TOTAL_PENDING + MAS_COUNT))
fi

# ------------------------------------------------------------------------------
# Flatpak (Linux)
# ------------------------------------------------------------------------------
FLATPAK_COUNT=0
FLATPAK_PKGS=""
if command -v flatpak >/dev/null 2>&1; then
  log_info "==> Checking Flatpak updates..."
  set +e
  FLATPAK_RAW="$(flatpak remote-ls --updates 2>/dev/null || true)"
  set -e
  if [ -n "$FLATPAK_RAW" ]; then
    FLATPAK_COUNT="$(echo "$FLATPAK_RAW" | grep -c . || true)"
    FLATPAK_PKGS="$(echo "$FLATPAK_RAW" | head -n 20)"
  fi
  TOTAL_PENDING=$((TOTAL_PENDING + FLATPAK_COUNT))
fi

# ------------------------------------------------------------------------------
# Snap (Linux)
# ------------------------------------------------------------------------------
SNAP_COUNT=0
SNAP_PKGS=""
if command -v snap >/dev/null 2>&1; then
  log_info "==> Checking Snap updates..."
  set +e
  SNAP_RAW="$(snap refresh --list 2>/dev/null || true)"
  set -e
  if [ -n "$SNAP_RAW" ] && ! echo "$SNAP_RAW" | grep -qi "All snaps up to date"; then
    SNAP_COUNT="$(echo "$SNAP_RAW" | tail -n +2 | grep -c . || true)"
    SNAP_PKGS="$(echo "$SNAP_RAW" | tail -n +2 | head -n 20 || true)"
  fi
  TOTAL_PENDING=$((TOTAL_PENDING + SNAP_COUNT))
fi

# ------------------------------------------------------------------------------
# Output results
# ------------------------------------------------------------------------------
if [ "$OUTPUT_JSON" = true ]; then
  cat <<EOF
{
  "total_pending_updates": $TOTAL_PENDING,
  "sources": {
    "apt": { "pending": $APT_COUNT },
    "dnf": { "pending": $DNF_COUNT },
    "pacman": { "pending": $PACMAN_COUNT },
    "zypper": { "pending": $ZYPPER_COUNT },
    "macos_system": { "pending": $MACOS_SYS_COUNT },
    "brew": { "pending": $BREW_COUNT },
    "mas": { "pending": $MAS_COUNT },
    "flatpak": { "pending": $FLATPAK_COUNT },
    "snap": { "pending": $SNAP_COUNT }
  }
}
EOF
else
  echo ""
  echo "=================================================="
  echo " Available Updates Summary"
  echo "=================================================="
  echo " Total pending updates: $TOTAL_PENDING"
  echo "--------------------------------------------------"
  [ "$APT_COUNT" -gt 0 ] && echo " [APT] $APT_COUNT package(s) pending:" && echo "$APT_PKGS" && echo ""
  [ "$DNF_COUNT" -gt 0 ] && echo " [DNF] $DNF_COUNT package(s) pending:" && echo "$DNF_PKGS" && echo ""
  [ "$PACMAN_COUNT" -gt 0 ] && echo " [Pacman] $PACMAN_COUNT package(s) pending:" && echo "$PACMAN_PKGS" && echo ""
  [ "$ZYPPER_COUNT" -gt 0 ] && echo " [Zypper] $ZYPPER_COUNT package(s) pending:" && echo "$ZYPPER_PKGS" && echo ""
  [ "$MACOS_SYS_COUNT" -gt 0 ] && echo " [macOS System] $MACOS_SYS_COUNT update(s) pending:" && echo "$MACOS_SYS_PKGS" && echo ""
  [ "$BREW_COUNT" -gt 0 ] && echo " [Homebrew] $BREW_COUNT package(s) pending:" && echo "$BREW_PKGS" && echo ""
  [ "$MAS_COUNT" -gt 0 ] && echo " [Mac App Store] $MAS_COUNT app(s) pending:" && echo "$MAS_PKGS" && echo ""
  [ "$FLATPAK_COUNT" -gt 0 ] && echo " [Flatpak] $FLATPAK_COUNT app(s) pending:" && echo "$FLATPAK_PKGS" && echo ""
  [ "$SNAP_COUNT" -gt 0 ] && echo " [Snap] $SNAP_COUNT snap(s) pending:" && echo "$SNAP_PKGS" && echo ""

  if [ "$TOTAL_PENDING" -eq 0 ]; then
    echo " All recognized packages and system components are up to date!"
  fi
  echo "=================================================="
fi
