# Linux Operating System & Package Update Guide

This reference document provides authoritative guidance and best practices for updating and maintaining Linux operating systems across various distribution families.

---

## 1. Debian & Ubuntu Family (`apt`, `apt-get`, `dpkg`)

### Standard Workflow
1. **Fetch index**: `sudo apt-get update`
2. **Review pending packages**: `apt list --upgradable`
3. **Apply safe upgrade**: `sudo apt-get upgrade -y`
   - *Note*: `upgrade` installs new versions of currently installed packages without ever removing packages.
4. **Full / Dist upgrade (use with caution)**: `sudo apt-get dist-upgrade -y` or `sudo apt-get full-upgrade -y`
   - *When to use*: Required when new kernel packages or major library transitions introduce or remove dependencies. Always review the removal list before executing.
5. **Clean up**:
   - Remove orphaned dependencies: `sudo apt-get autoremove --purge -y`
   - Clean downloaded package archives (`/var/cache/apt/archives`): `sudo apt-get clean`

### Security Updates Only
- Using `unattended-upgrades`:
  ```bash
  sudo unattended-upgrade -d --dry-run   # simulation
  sudo unattended-upgrade -d             # execute security upgrades
  ```
- Or filter security repositories directly:
  ```bash
  sudo apt-get --only-upgrade install $(apt-get -s upgrade | awk '/^Inst.*security/ {print $2}')
  ```

### Non-Interactive Execution
When running updates via scripts or agents, prevent debconf interactive curses prompts that block execution:
```bash
DEBIAN_FRONTEND=noninteractive sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade
```
- `--force-confdef`: Use the default action for modified configuration files.
- `--force-confold`: Keep the existing configuration file unmodified if no default exists.

### Reboot Indicator
Debian and Ubuntu write to `/var/run/reboot-required` when a kernel, libc, or systemd update requires a system reboot.
- Inspect triggering packages: `cat /var/run/reboot-required.pkgs`

---

## 2. Red Hat Family (`dnf`, `yum` - Fedora, RHEL, Rocky, AlmaLinux)

### Standard Workflow
1. **Refresh cache**: `dnf makecache`
2. **Check available updates**:
   ```bash
   dnf check-update
   ```
   *Exit codes*:
   - `0`: No updates available.
   - `100`: Updates are available.
   - `1`: Error encountered.
3. **Apply upgrades**:
   ```bash
   sudo dnf upgrade -y
   ```
4. **Clean up**:
   ```bash
   sudo dnf autoremove -y
   sudo dnf clean all
   ```

### Security-Focused Updates
RHEL and Fedora natively support security filtering via the updateinfo metadata:
```bash
# Check security advisories
dnf updateinfo list security

# Apply only security patches
sudo dnf upgrade-minimal --security -y
```

### Reboot Check
Use `needs-restarting` (provided by `dnf-plugins-core` / `yum-utils`):
```bash
# Returns exit code 1 if reboot is needed, 0 if not
needs-restarting -r
```

---

## 3. Arch Linux & Manjaro (`pacman`)

### Critical Rules for Arch Linux
1. **NEVER do partial upgrades**: Running `pacman -Sy <package>` or `pacman -Sy` without `-u` desynchronizes libraries and can break core system components.
2. **Always upgrade the keyring first if system has not been updated in a while**:
   ```bash
   sudo pacman -Sy --needed archlinux-keyring && sudo pacman -Su
   ```
3. **Standard command**:
   ```bash
   sudo pacman -Syu
   ```
4. **Check updates safely without root sync**:
   Use `checkupdates` (from `pacman-contrib`) which downloads to a temporary database:
   ```bash
   checkupdates
   ```
5. **Orphan package removal**:
   ```bash
   # List orphans
   pacman -Qtdq
   # Remove orphans
   sudo pacman -Rns $(pacman -Qtdq)
   ```
6. **AUR Packages**:
   If using an AUR helper (`yay` or `paru`):
   ```bash
   yay -Syu --combinedupgrade
   ```
   *Caution*: Never run AUR helpers with `sudo`; they invoke `sudo` internally when needed.

---

## 4. openSUSE (`zypper` - Leap vs Tumbleweed)

- **openSUSE Leap (Fixed release)**:
  ```bash
  sudo zypper refresh
  sudo zypper list-updates
  sudo zypper update -y
  ```
  For security and recommended patches:
  ```bash
  sudo zypper patch
  ```

- **openSUSE Tumbleweed (Rolling release)**:
  *Always* use `dist-upgrade` on Tumbleweed, never standard `update`:
  ```bash
  sudo zypper refresh
  sudo zypper dist-upgrade -y
  # Short alias:
  sudo zypper dup -y
  ```

---

## 5. Alpine Linux (`apk`)

Alpine Linux is widely used in containers and lightweight servers:
```bash
# Update repository index
apk update

# List upgradable packages
apk version -v -l '<'

# Perform upgrade
apk upgrade
```

---

## 6. Immutable & Atomic Distributions

Modern Linux distributions often feature immutable root filesystems:
- **Fedora Silverblue / Kinoite / IoT (`rpm-ostree`)**:
  ```bash
  # Check status & updates
  rpm-ostree status
  rpm-ostree upgrade --check
  
  # Deploy updates into a new deployment
  rpm-ostree upgrade
  ```
  *Note*: Changes take effect on next reboot.
- **openSUSE MicroOS / Aeon (`transactional-update`)**:
  ```bash
  sudo transactional-update dup
  ```

---

## 7. Universal Application Packages

System package updates do not manage Flatpak or Snap applications. Always check and refresh them separately:

### Flatpak
```bash
# Check updates
flatpak remote-ls --updates

# Update all runtimes and applications
flatpak update -y

# Remove unused runtimes
flatpak uninstall --unused -y
```

### Snap
```bash
# Check updates
snap refresh --list

# Refresh all installed snaps
sudo snap refresh
```
