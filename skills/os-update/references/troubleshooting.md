# Troubleshooting Common OS & Package Update Failures

This reference guide contains targeted recovery procedures for common package manager failures and corrupted update states across Linux and macOS.

---

## 1. Debian & Ubuntu (`apt` / `dpkg`)

### Issue: "Could not get lock /var/lib/dpkg/lock-frontend"
**Cause**: Another process (e.g., `unattended-upgrades`, `apt-daily.service`, or another terminal) is holding the lock.
**Resolution**:
1. Check what is holding the lock:
   ```bash
   sudo lsof /var/lib/dpkg/lock-frontend
   ```
2. If it is `unattended-upgrades`, wait 2–3 minutes for it to complete.
3. If the process is defunct (stale lock after crash):
   ```bash
   sudo kill -9 <PID>  # only if confirmed hung
   sudo rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock /var/lib/apt/lists/lock
   sudo dpkg --configure -a
   ```

### Issue: "dpkg was interrupted, you must manually run 'dpkg --configure -a'"
**Resolution**:
```bash
sudo dpkg --configure -a
```

### Issue: "Unmet dependencies. Try 'apt --fix-broken install'"
**Resolution**:
```bash
sudo apt-get update
sudo apt-get --fix-broken install -y
```

### Issue: "Hash Sum mismatch" or Corrupted Package Lists
**Resolution**:
```bash
sudo rm -rf /var/lib/apt/lists/*
sudo apt-get clean
sudo apt-get update
```

### Issue: Disk Full During Kernel Upgrade (`/boot` full)
**Resolution**:
1. Identify running kernel:
   ```bash
   uname -r
   ```
2. List installed kernels:
   ```bash
   dpkg -l 'linux-image-*' | grep '^ii'
   ```
3. Purge oldest unneeded kernel manually:
   ```bash
   sudo apt-get purge linux-image-<old-version>-generic
   ```
4. Fix broken state:
   ```bash
   sudo apt-get -f install
   sudo update-grub
   ```

---

## 2. Red Hat Family (`dnf` / `rpm`)

### Issue: RPM Database Corruption
**Symptoms**: `error: rpmdb: BDB0111 ...` or `Segmentation fault` during rpm queries.
**Resolution**:
```bash
sudo rm -f /var/lib/rpm/__db.*
sudo rpm --rebuilddb
sudo dnf clean all
sudo dnf makecache
```

### Issue: Transaction Check Conflicts
**Symptoms**: `Transaction check error: file ... from install of packageA conflicts with file from packageB`.
**Resolution**:
```bash
# Identify duplicate packages
dnf repoquery --duplicated

# Remove duplicates
sudo dnf remove --duplicates

# Retry with allowerasing if replacing obsolete dependencies
sudo dnf upgrade --allowerasing
```

---

## 3. Arch Linux (`pacman`)

### Issue: PGP Signature Errors / Corrupted Keys
**Symptoms**: `error: package: signature from "Developer" is invalid` / `error: key could not be looked up remotely`.
**Resolution**:
```bash
# Refresh archlinux keyring explicitly
sudo pacman -Sy --needed archlinux-keyring
# If keys are severely broken, re-initialize pacman keys:
sudo rm -rf /etc/pacman.d/gnupg
sudo pacman-key --init
sudo pacman-key --populate archlinux
sudo pacman -Syu
```

### Issue: File Conflicts
**Symptoms**: `error: failed to commit transaction (conflicting files): package: '/path/file' exists in filesystem`.
**Resolution**:
1. Check which package owns the file:
   ```bash
   pacman -Qo /path/file
   ```
2. If no package owns it (untracked orphan file):
   ```bash
   # Move/backup the conflicting file or overwrite if known safe:
   sudo pacman -Syu --overwrite /path/file
   ```

---

## 4. macOS (`softwareupdate` & Homebrew)

### Issue: `softwareupdate` Fails with Catalog or Network Error
**Resolution**:
1. Flush DNS cache:
   ```bash
   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
   ```
2. Reset softwareupdate catalog to default:
   ```bash
   sudo softwareupdate --clear-catalog
   ```
3. Retry query:
   ```bash
   softwareupdate -l
   ```

### Issue: Homebrew Broken Symlinks or Permission Warnings
**Resolution**:
```bash
brew doctor
```
Follow the specific remediation instructions output by `brew doctor`.
To repair Homebrew git repo and formula states:
```bash
git -C "$(brew --repo)" fetch --tags
brew update-reset
```

### Issue: App Blocked by Gatekeeper After Cask Upgrade
**Resolution**:
```bash
xattr -d com.apple.quarantine /Applications/<App>.app
```
