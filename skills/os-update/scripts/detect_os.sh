#!/usr/bin/env bash
# ==============================================================================
# detect_os.sh - Environment and Package Manager Detection Helper
# Supports: Linux (Debian, Ubuntu, Fedora, RHEL, Arch, openSUSE, Alpine) & macOS
# ==============================================================================
set -euo pipefail

OUTPUT_JSON=false

for arg in "$@"; do
  case "$arg" in
    --json)
      OUTPUT_JSON=true
      ;;
    -h|--help)
      echo "Usage: $0 [--json]"
      echo "Detects operating system, architecture, disk space, and available package managers."
      exit 0
      ;;
  esac
done

OS_TYPE="$(uname -s)"
ARCH="$(uname -m)"
KERNEL="$(uname -r)"

DISTRO_ID="unknown"
DISTRO_NAME="Unknown"
DISTRO_VERSION="unknown"
DISTRO_CODENAME="unknown"

PKG_MANAGERS=()
REBOOT_REQUIRED=false
REBOOT_REASON=""
BATTERY_STATUS="N/A"

# --- OS-specific detection ---
if [ "$OS_TYPE" = "Darwin" ]; then
  DISTRO_ID="macos"
  DISTRO_NAME="macOS"
  if command -v sw_vers >/dev/null 2>&1; then
    DISTRO_VERSION="$(sw_vers -productVersion 2>/dev/null || echo 'unknown')"
    DISTRO_CODENAME="$(sw_vers -buildVersion 2>/dev/null || echo 'unknown')"
  fi

  # Check Darwin package managers
  if command -v softwareupdate >/dev/null 2>&1; then
    PKG_MANAGERS+=("softwareupdate")
  fi
  if command -v brew >/dev/null 2>&1; then
    PKG_MANAGERS+=("brew")
  fi
  if command -v mas >/dev/null 2>&1; then
    PKG_MANAGERS+=("mas")
  fi

  # Power info
  if command -v pmset >/dev/null 2>&1; then
    BATTERY_STATUS="$(pmset -g batt 2>/dev/null | grep -E -o '[0-9]+%' | head -n1 || echo 'AC/Unknown')"
  fi

elif [ "$OS_TYPE" = "Linux" ]; then
  if [ -f /etc/os-release ]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    DISTRO_ID="${ID:-linux}"
    DISTRO_NAME="${NAME:-Linux}"
    DISTRO_VERSION="${VERSION_ID:-unknown}"
    DISTRO_CODENAME="${VERSION_CODENAME:-unknown}"
  elif [ -f /etc/redhat-release ]; then
    DISTRO_ID="rhel"
    DISTRO_NAME="$(cat /etc/redhat-release)"
  elif [ -f /etc/debian_version ]; then
    DISTRO_ID="debian"
    DISTRO_NAME="Debian"
    DISTRO_VERSION="$(cat /etc/debian_version)"
  fi

  # Check Linux package managers
  if command -v apt >/dev/null 2>&1 || command -v apt-get >/dev/null 2>&1; then
    PKG_MANAGERS+=("apt")
  fi
  if command -v dnf >/dev/null 2>&1; then
    PKG_MANAGERS+=("dnf")
  elif command -v yum >/dev/null 2>&1; then
    PKG_MANAGERS+=("yum")
  fi
  if command -v pacman >/dev/null 2>&1; then
    PKG_MANAGERS+=("pacman")
  fi
  if command -v zypper >/dev/null 2>&1; then
    PKG_MANAGERS+=("zypper")
  fi
  if command -v apk >/dev/null 2>&1; then
    PKG_MANAGERS+=("apk")
  fi
  if command -v flatpak >/dev/null 2>&1; then
    PKG_MANAGERS+=("flatpak")
  fi
  if command -v snap >/dev/null 2>&1; then
    PKG_MANAGERS+=("snap")
  fi
  if command -v brew >/dev/null 2>&1; then
    PKG_MANAGERS+=("brew")
  fi

  # Check reboot status
  if [ -f /var/run/reboot-required ]; then
    REBOOT_REQUIRED=true
    if [ -f /var/run/reboot-required.pkgs ]; then
      REBOOT_REASON="$(tr '\n' ' ' < /var/run/reboot-required.pkgs | sed 's/ $//')"
    else
      REBOOT_REASON="reboot-required flag present"
    fi
  elif command -v needs-restarting >/dev/null 2>&1; then
    if ! needs-restarting -r >/dev/null 2>&1; then
      REBOOT_REQUIRED=true
      REBOOT_REASON="needs-restarting detected kernel/core updates"
    fi
  fi

  # Battery check
  if [ -d /sys/class/power_supply ]; then
    for bat in /sys/class/power_supply/BAT* /sys/class/power_supply/battery; do
      if [ -f "${bat}/capacity" ]; then
        BATTERY_STATUS="$(cat "${bat}/capacity")%"
        break
      fi
    done
  fi
fi

# Disk Space
DISK_ROOT_AVAIL="$(df -h / | awk 'NR==2 {print $4}')"
DISK_ROOT_USE_PCT="$(df -h / | awk 'NR==2 {print $5}')"
DISK_BOOT_AVAIL="N/A"
if mountpoint -q /boot 2>/dev/null; then
  DISK_BOOT_AVAIL="$(df -h /boot | awk 'NR==2 {print $4}')"
fi

# Convert PKG_MANAGERS array to comma/space separated string or json list
PKG_MANAGERS_STR="${PKG_MANAGERS[*]:-none}"

if [ "$OUTPUT_JSON" = true ]; then
  # Format PKG_MANAGERS as JSON array
  PKG_JSON="["
  FIRST=true
  for p in "${PKG_MANAGERS[@]}"; do
    if [ "$FIRST" = true ]; then
      PKG_JSON="${PKG_JSON}\"${p}\""
      FIRST=false
    else
      PKG_JSON="${PKG_JSON}, \"${p}\""
    fi
  done
  PKG_JSON="${PKG_JSON}]"

  cat <<EOF
{
  "os_type": "$OS_TYPE",
  "distro_id": "$DISTRO_ID",
  "distro_name": "$DISTRO_NAME",
  "distro_version": "$DISTRO_VERSION",
  "distro_codename": "$DISTRO_CODENAME",
  "arch": "$ARCH",
  "kernel": "$KERNEL",
  "package_managers": $PKG_JSON,
  "disk_root_available": "$DISK_ROOT_AVAIL",
  "disk_root_usage_pct": "$DISK_ROOT_USE_PCT",
  "disk_boot_available": "$DISK_BOOT_AVAIL",
  "reboot_required": $REBOOT_REQUIRED,
  "reboot_reason": "$REBOOT_REASON",
  "battery": "$BATTERY_STATUS"
}
EOF
else
  echo "=================================================="
  echo " Operating System & Environment Information"
  echo "=================================================="
  echo "  OS Family       : $OS_TYPE"
  echo "  Distribution    : $DISTRO_NAME ($DISTRO_ID) $DISTRO_VERSION"
  echo "  Codename        : $DISTRO_CODENAME"
  echo "  Architecture    : $ARCH"
  echo "  Kernel Release  : $KERNEL"
  echo "  Package Managers: $PKG_MANAGERS_STR"
  echo "  Disk Space (/)  : Free $DISK_ROOT_AVAIL (Used $DISK_ROOT_USE_PCT)"
  if [ "$DISK_BOOT_AVAIL" != "N/A" ]; then
    echo "  Disk Space (/boot): Free $DISK_BOOT_AVAIL"
  fi
  echo "  Reboot Needed   : $REBOOT_REQUIRED $([ "$REBOOT_REQUIRED" = true ] && echo "($REBOOT_REASON)" || true)"
  echo "  Battery Status  : $BATTERY_STATUS"
  echo "=================================================="
fi
