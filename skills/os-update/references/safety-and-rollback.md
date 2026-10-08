# Safety, Pre-Flight Checks & Rollback Strategies

Applying system and package updates modifies critical low-level libraries, kernel modules, and services. Adhering to strict safety guidelines prevents system corruption, boot failures, and unplanned downtime.

---

## 1. Pre-Flight Checklist

Before running any update commands, verify the following conditions:

| Check | Requirement | Command / Method |
|---|---|---|
| **Root Disk Space** | Minimum 1.5–2.0 GB free on `/` | `df -h /` |
| **Boot Partition Space** | Minimum 200–300 MB free on `/boot` (if separate) | `df -h /boot` |
| **Power Source** | Connected to AC power or battery > 50% | `pmset -g batt` (macOS), `/sys/class/power_supply` (Linux) |
| **Active Locks** | No concurrent package manager running | Check `lsof` / `fuser` on lock files |
| **Network Connection** | Stable internet connection with DNS resolution | `ping -c 2 1.1.1.1` or `curl -I https://archive.ubuntu.com` |
| **Current Kernel** | Verify running kernel | `uname -r` |

---

## 2. Snapshot & Rollback Strategies

### Linux: Filesystem Snapshots

#### Btrfs / OpenSUSE Snapper
If the root filesystem is Btrfs:
```bash
# Snapper creates pre/post update snapshots automatically if configured
sudo snapper create -d "Before system update" -t pre
```
To rollback:
```bash
# List snapshots
snapper list
# Rollback to snapshot ID
sudo snapper rollback <ID>
```

#### Timeshift (Debian / Ubuntu / Arch / Fedora)
Timeshift works with both Btrfs and Rsync:
```bash
# Create an on-demand snapshot
sudo timeshift --create --comments "Pre-update backup" --tags O
```
To restore via CLI:
```bash
sudo timeshift --restore
```

#### LVM Snapshots
If using LVM:
```bash
# Create a snapshot of the root volume
sudo lvcreate --size 5G --snapshot --name root_preupdate /dev/vg0/root
```

### macOS: APFS Snapshots
APFS provides built-in, instantaneous copy-on-write snapshots:
```bash
# Create a local APFS snapshot
tmutil localsnapshot

# View created snapshots
tmutil listlocalsnapshots /
```
If a system update fails or causes regressions:
1. Boot into macOS Recovery (`Cmd + R` or hold Power button on Apple Silicon).
2. Open **Disk Utility** or select **Restore from Time Machine**.
3. Select the local APFS snapshot taken before the update.

---

## 3. Kernel Management & Boot Partition Safety

### The "Full `/boot`" Trap
On Linux systems with a dedicated `/boot` partition, old accumulated kernels can fill the partition to 100%. If an update begins with a full `/boot`, initramfs generation will fail, resulting in an unbootable kernel.

1. **Check `/boot` space**:
   ```bash
   df -h /boot
   ```
2. **Never delete the active kernel**:
   ```bash
   uname -r
   ```
3. **Clean old kernels safely**:
   - Debian/Ubuntu: `sudo apt-get autoremove --purge`
   - Fedora/RHEL: `dnf remove --oldinstallonly --setopt installonly_limit=2 kernel`

---

## 4. Configuration File Conflicts (`conffiles`)

When an updated package provides a new default configuration file and the user has modified the existing file:

- **Debian / Ubuntu (`dpkg`)**:
  - Default non-interactive mode: `DEBIAN_FRONTEND=noninteractive` with `-o Dpkg::Options::="--force-confold"` keeps the existing user configuration and writes the maintainer version to `<file>.dpkg-dist`.
- **RHEL / Fedora (`rpm`)**:
  - Saves the new maintainer configuration as `<file>.rpmnew` (or the old file as `<file>.rpmsave`).
  - Audit `.rpmnew` files with `rpmconf -a`.
- **Arch Linux (`pacman`)**:
  - Saves `.pacnew` and `.pacsave` files.
  - Review and merge conflicts using `pacdiff`.

---

## 5. Handling Lock Files Safely

Never indiscriminately `rm -f /var/lib/dpkg/lock*` or `/var/lib/pacman/db.lck`.

1. **Verify if a process is still holding the lock**:
   ```bash
   # Debian / Ubuntu
   sudo lsof /var/lib/dpkg/lock-frontend
   sudo fuser /var/lib/dpkg/lock-frontend

   # Red Hat / Fedora
   sudo lsof /var/lib/rpm/.rpm.lock

   # Arch Linux
   sudo lsof /var/lib/pacman/db.lck
   ```
2. **If a process is running (e.g. `unattended-upgrades`)**:
   - **WAIT** for it to complete. Killing an active package installation can leave the database in an inconsistent state.
3. **If the process is dead (stale lock after a reboot or power outage)**:
   - Only remove the lock file if no PID is reported by `lsof` or `fuser`.
   - Run database repair immediately (e.g. `sudo dpkg --configure -a`).
