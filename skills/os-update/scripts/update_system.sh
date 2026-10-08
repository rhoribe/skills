#!/usr/bin/env bash
# ==============================================================================
# update_system.sh - Safe operating system and package updater
# Supports: Linux (Debian/Ubuntu, Fedora/RHEL, Arch, openSUSE, Alpine, Flatpak, Snap)
#           macOS (softwareupdate, Homebrew, Mac App Store)
# ==============================================================================
set -euo pipefail

DRY_RUN=false
SECURITY_ONLY=false
AUTO_YES=false
DO_CLEAN=false
SCOPE="all"  # "system", "user", or "all"

usage() {
  cat <<EOF
Usage: $0 [OPTIONS]

Options:
  -n, --dry-run        Simulate updates without making changes (where supported)
  -s, --security-only  Apply only security updates (Debian/Ubuntu, RHEL/Fedora, openSUSE)
  -y, --yes            Assume yes to prompts and run non-interactively
  -c, --clean          Perform cleanup (autoremove, cache clean) after updating
  --scope SCOPE        Limit scope: 'system' (OS/root PM), 'user' (Homebrew/Flatpak/Snap), or 'all' (default)
  -h, --help           Show this help message
EOF
  exit 0
}

while [ $# -gt 0 ]; do
  case "$1" in
    -n|--dry-run)
      DRY_RUN=true
      shift
      ;;
    -s|--security-only)
      SECURITY_ONLY=true
      shift
      ;;
    -y|--yes)
      AUTO_YES=true
      shift
      ;;
    -c|--clean)
      DO_CLEAN=true
      shift
      ;;
    --scope)
      SCOPE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      ;;
  esac
done

# Colors (if terminal supports it)
if [ -t 1 ]; then
  BOLD="\033[1m"
  GREEN="\033[0;32m"
  YELLOW="\033[0;33m"
  RED="\033[0;31m"
  RESET="\033[0m"
else
  BOLD=""
  GREEN=""
  YELLOW=""
  RED=""
  RESET=""
fi

log_step() {
  echo -e "\n${BOLD}${GREEN}==>${RESET} ${BOLD}$*${RESET}"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${RESET} $*" >&2
}

log_error() {
  echo -e "${RED}[ERROR]${RESET} $*" >&2
}

# --- Pre-flight Checks ---
log_step "Performing Pre-Flight Checks..."

OS_TYPE="$(uname -s)"
AVAIL_MB="$(df -m / | awk 'NR==2 {print $4}')"
if [ "$AVAIL_MB" -lt 1024 ]; then
  log_error "Low disk space on root filesystem (/): only ${AVAIL_MB}MB available. At least 1024MB (1GB) is recommended."
  if [ "$AUTO_YES" = false ]; then
    read -r -p "Do you want to proceed anyway? (y/N): " resp
    if [[ ! "$resp" =~ ^[yY] ]]; then
      echo "Aborting due to insufficient disk space."
      exit 1
    fi
  fi
fi

RUN_AS_SUDO=""
if [ "$OS_TYPE" = "Linux" ] && [ "$SCOPE" != "user" ]; then
  if [ "$(id -u)" -eq 0 ]; then
    RUN_AS_SUDO=""
  elif command -v sudo >/dev/null 2>&1; then
    RUN_AS_SUDO="sudo"
  else
    log_warn "Neither root nor sudo detected. System-level package operations might fail."
  fi
fi

# Confirmation prompt if not dry-run and not auto-yes
if [ "$DRY_RUN" = false ] && [ "$AUTO_YES" = false ]; then
  echo ""
  echo "Ready to execute update with:"
  echo "  Mode         : $([ "$SECURITY_ONLY" = true ] && echo "Security Only" || echo "Full Update")"
  echo "  Scope        : $SCOPE"
  echo "  Cleanup      : $DO_CLEAN"
  read -r -p "Proceed with updates? (y/N): " confirm
  if [[ ! "$confirm" =~ ^[yY] ]]; then
    echo "Update aborted by user."
    exit 0
  fi
fi

# ==============================================================================
# LINUX SYSTEM UPDATES
# ==============================================================================
if [ "$OS_TYPE" = "Linux" ] && [ "$SCOPE" != "user" ]; then

  # --- APT ---
  if command -v apt-get >/dev/null 2>&1; then
    log_step "Updating Debian/Ubuntu (APT)..."
    if [ "$DRY_RUN" = true ]; then
      echo "Simulating apt upgrade:"
      $RUN_AS_SUDO apt-get -s upgrade
    elif [ "$SECURITY_ONLY" = true ]; then
      $RUN_AS_SUDO apt-get update
      if command -v unattended-upgrade >/dev/null 2>&1; then
        $RUN_AS_SUDO unattended-upgrade -v
      else
        log_warn "unattended-upgrade not found; upgrading security packages via apt-get upgrade..."
        SEC_PKGS="$(apt-get --just-print upgrade 2>/dev/null | awk '/^Inst / && /security/ {print $2}' | grep -E '^[a-zA-Z0-9._+-]+$' | tr '\n' ' ' || true)"
        if [ -n "$SEC_PKGS" ]; then
          # shellcheck disable=SC2086
          $RUN_AS_SUDO apt-get --only-upgrade install -y $SEC_PKGS
        fi
      fi
    else
      $RUN_AS_SUDO apt-get update
      DEBIAN_FRONTEND=noninteractive $RUN_AS_SUDO apt-get upgrade -y
    fi

    if [ "$DO_CLEAN" = true ] && [ "$DRY_RUN" = false ]; then
      log_step "Cleaning APT cache and orphaned packages..."
      $RUN_AS_SUDO apt-get autoremove --purge -y
      $RUN_AS_SUDO apt-get clean
    fi
  fi

  # --- DNF ---
  if command -v dnf >/dev/null 2>&1; then
    log_step "Updating Fedora/RHEL (DNF)..."
    if [ "$DRY_RUN" = true ]; then
      $RUN_AS_SUDO dnf upgrade --assumeno || true
    elif [ "$SECURITY_ONLY" = true ]; then
      $RUN_AS_SUDO dnf upgrade-minimal --security -y
    else
      $RUN_AS_SUDO dnf upgrade -y
    fi

    if [ "$DO_CLEAN" = true ] && [ "$DRY_RUN" = false ]; then
      log_step "Cleaning DNF packages..."
      $RUN_AS_SUDO dnf autoremove -y
      $RUN_AS_SUDO dnf clean all
    fi
  fi

  # --- Pacman ---
  if command -v pacman >/dev/null 2>&1; then
    log_step "Updating Arch Linux (Pacman)..."
    if [ "$DRY_RUN" = true ]; then
      if command -v checkupdates >/dev/null 2>&1; then
        checkupdates || true
      else
        pacman -Qu || true
      fi
    else
      # Notice: Partial upgrades are not supported on Arch. Always full sync.
      $RUN_AS_SUDO pacman -Syu --noconfirm
    fi

    if [ "$DO_CLEAN" = true ] && [ "$DRY_RUN" = false ]; then
      log_step "Cleaning Pacman cache..."
      $RUN_AS_SUDO pacman -Sc --noconfirm
    fi
  fi

  # --- Zypper ---
  if command -v zypper >/dev/null 2>&1; then
    log_step "Updating openSUSE (Zypper)..."
    if [ "$DRY_RUN" = true ]; then
      $RUN_AS_SUDO zypper --dry-run update
    elif [ "$SECURITY_ONLY" = true ]; then
      $RUN_AS_SUDO zypper --non-interactive patch --category security
    else
      $RUN_AS_SUDO zypper --non-interactive update
    fi

    if [ "$DO_CLEAN" = true ] && [ "$DRY_RUN" = false ]; then
      $RUN_AS_SUDO zypper clean --all
    fi
  fi

  # --- Alpine (APK) ---
  if command -v apk >/dev/null 2>&1; then
    log_step "Updating Alpine Linux (APK)..."
    if [ "$DRY_RUN" = true ]; then
      $RUN_AS_SUDO apk upgrade --simulate
    else
      $RUN_AS_SUDO apk update
      $RUN_AS_SUDO apk upgrade
    fi
  fi
fi

# ==============================================================================
# macOS SYSTEM UPDATES
# ==============================================================================
if [ "$OS_TYPE" = "Darwin" ] && [ "$SCOPE" != "user" ]; then
  if command -v softwareupdate >/dev/null 2>&1; then
    log_step "Updating macOS System Software (softwareupdate)..."
    if [ "$DRY_RUN" = true ]; then
      softwareupdate -l
    else
      # Note: -r installs only recommended updates to avoid accidental major OS version jumps
      echo "Applying recommended macOS software updates..."
      softwareupdate -i -r --verbose
    fi
  fi
fi

# ==============================================================================
# UNIVERSAL / USER-SPACE MANAGERS (macOS & Linux)
# ==============================================================================
if [ "$SCOPE" != "system" ]; then

  # --- Homebrew ---
  if command -v brew >/dev/null 2>&1; then
    log_step "Updating Homebrew (formulas & casks)..."
    if [ "$DRY_RUN" = true ]; then
      brew outdated --verbose || true
    else
      brew update
      brew upgrade
      # On macOS also upgrade casks
      if [ "$OS_TYPE" = "Darwin" ]; then
        brew upgrade --cask || true
      fi
      if [ "$DO_CLEAN" = true ]; then
        brew cleanup -s
      fi
    fi
  fi

  # --- Mac App Store (mas) ---
  if command -v mas >/dev/null 2>&1; then
    log_step "Updating Mac App Store apps (mas)..."
    if [ "$DRY_RUN" = true ]; then
      mas outdated || true
    else
      mas upgrade || true
    fi
  fi

  # --- Flatpak ---
  if command -v flatpak >/dev/null 2>&1; then
    log_step "Updating Flatpak runtimes and apps..."
    if [ "$DRY_RUN" = true ]; then
      flatpak remote-ls --updates || true
    else
      flatpak update -y
      if [ "$DO_CLEAN" = true ]; then
        flatpak uninstall --unused -y
      fi
    fi
  fi

  # --- Snap ---
  if command -v snap >/dev/null 2>&1; then
    log_step "Refreshing Snap packages..."
    if [ "$DRY_RUN" = true ]; then
      snap refresh --list || true
    else
      if [ -n "$RUN_AS_SUDO" ]; then
        $RUN_AS_SUDO snap refresh
      else
        snap refresh
      fi
    fi
  fi

fi

# ==============================================================================
# POST-UPDATE VERIFICATION & STATUS
# ==============================================================================
log_step "Update cycle complete. Checking system status..."

REBOOT_NEEDED=false

if [ "$OS_TYPE" = "Linux" ]; then
  if [ -f /var/run/reboot-required ]; then
    REBOOT_NEEDED=true
    echo -e "${YELLOW}[NOTICE]${RESET} System reboot is required (flag file /var/run/reboot-required present)."
    if [ -f /var/run/reboot-required.pkgs ]; then
      echo "Triggered by packages:"
      tr -cd '[:alnum:] ._/:+-\n' < /var/run/reboot-required.pkgs | sed 's/^/  - /'
    fi
  elif command -v needs-restarting >/dev/null 2>&1; then
    if ! needs-restarting -r >/dev/null 2>&1; then
      REBOOT_NEEDED=true
      echo -e "${YELLOW}[NOTICE]${RESET} System reboot is recommended by needs-restarting."
    fi
  fi
elif [ "$OS_TYPE" = "Darwin" ]; then
  # On macOS, softwareupdate indicates if restart is needed in its output
  echo "On macOS, check notification center if a restart was prompted by softwareupdate."
fi

if [ "$REBOOT_NEEDED" = false ]; then
  echo -e "${GREEN}[OK]${RESET} No reboot is currently required."
fi

echo -e "\n${BOLD}${GREEN}Done!${RESET}"
