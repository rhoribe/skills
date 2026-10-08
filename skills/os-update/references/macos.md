# macOS Operating System & Package Update Guide

This reference document provides comprehensive instructions and best practices for updating Apple macOS systems, Homebrew environments, and Mac App Store packages.

---

## 1. Apple System Updates (`softwareupdate`)

macOS includes the built-in CLI tool `softwareupdate` for managing OS patches, security updates, firmware updates, and Xcode Command Line Tools.

### Querying Updates
```bash
# List all available updates
softwareupdate -l
```

### Installing Updates
1. **Recommended Updates (Safe default)**:
   Installs security patches, Safari updates, and minor point releases without automatically triggering major operating system upgrades:
   ```bash
   softwareupdate -i -r --verbose
   ```

2. **All Available Updates**:
   ```bash
   softwareupdate -i -a --verbose
   ```

3. **Handling Reboots**:
   If an update requires a restart, `softwareupdate` outputs `[restart]`.
   - To automatically reboot if required (only when user has consented):
     ```bash
     sudo softwareupdate -i -r --restart
     ```

### Major OS Upgrades (e.g., macOS 14 Sonoma -> 15 Sequoia)
Major version upgrades require downloading a full installer image (12–14 GB).
- **Listing full installers**:
  ```bash
  softwareupdate --list-full-installers
  ```
- **Downloading a full installer**:
  ```bash
  softwareupdate --fetch-full-installer --full-installer-version 15.0
  ```
- *Best Practice*: Never force a major macOS version bump automatically without explicit user authorization, verified backup, and compatibility check of critical development tools.

### Xcode Command Line Tools
If developer tools need an update:
```bash
softwareupdate -d -a --include-config-data
```
Or force reinstall/prompt:
```bash
xcode-select --install
```

### Apple Silicon (Rosetta 2)
If running on Apple Silicon (M1/M2/M3/M4) and Rosetta 2 is needed:
```bash
/usr/sbin/softwareupdate --install-rosetta --agree-to-license
```

---

## 2. Homebrew Package Manager (`brew`)

Homebrew manages open-source CLI tools (formulae) and macOS desktop applications (casks).

### Standard Maintenance Sequence
1. **Fetch latest Homebrew taps and formula metadata**:
   ```bash
   brew update
   ```
2. **Review outdated packages**:
   ```bash
   brew outdated --verbose
   ```
3. **Upgrade CLI formulae**:
   ```bash
   brew upgrade
   ```
4. **Upgrade GUI Casks (Applications)**:
   ```bash
   brew upgrade --cask
   ```
   *Note*: Some casks manage their own auto-updates (e.g., Chrome, VS Code). Adding `--greedy` updates casks that have auto-update enabled or unversioned casks:
   ```bash
   brew upgrade --cask --greedy
   ```
5. **Clean up old versions and cached downloads**:
   ```bash
   brew cleanup -s
   ```
6. **Diagnostics**:
   If warnings or linking issues occur after upgrades:
   ```bash
   brew doctor
   ```

### Pinning Sensitive Packages
To prevent a specific tool (e.g. specific Python or Node version) from upgrading:
```bash
brew pin <package_name>
# To unpin later:
brew unpin <package_name>
```

---

## 3. Mac App Store CLI (`mas`)

The `mas` utility allows interacting with the Mac App Store from the command line:

### Inspection & Upgrade
```bash
# Check outdated Mac App Store applications
mas outdated

# Upgrade all outdated apps
mas upgrade
```

---

## 4. Safety & System Snapshots on macOS (APFS)

Before executing large system updates or major upgrades, ensure data protection:

### APFS Local Snapshot
APFS supports instantaneous local snapshots that Time Machine or Recovery Mode can revert to:
```bash
# Create an instant local APFS snapshot
tmutil localsnapshot
```
- List local snapshots:
  ```bash
  tmutil listlocalsnapshots /
  ```
- If an update fails, the snapshot can be booted and restored via macOS Recovery.

### Battery & Power Pre-condition
Updates on macOS can stall or fail if battery power drops below safe thresholds.
- Check power status:
  ```bash
  pmset -g batt
  ```
- Always ensure the MacBook is connected to AC power before triggering `softwareupdate`.
