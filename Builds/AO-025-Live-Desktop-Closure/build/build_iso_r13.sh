#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
base_iso="/home/maddin/AIDRAX-OS-AO-013-24-dual-path-20260829T174000Z/live-base/ubuntu-24.04.4-live-server-amd64.iso"
base_sha256="e907d92eeec9df64163a7e454cbc8d7755e8ddc7ed42f99dbc80c40f1a138433"
rootfs="$root/build-output/rootfs-ao025-desktop-20260920-r13"
work="$root/build-output/iso-work-20260920-r13"
output="$root/build-output/AIDRAX-OS-24.04.4-Live-amd64-r13.iso"

for command in xorriso mksquashfs sha256sum podman; do
    command -v "$command" >/dev/null || { echo "BLOCKED: missing $command" >&2; exit 2; }
done
[[ "$(id -u)" -ne 0 ]] || { echo "BLOCKED: run rootless" >&2; exit 2; }
[[ -f "$base_iso" && -d "$rootfs" ]] || { echo "BLOCKED: immutable input missing" >&2; exit 2; }
[[ "$(sha256sum "$base_iso" | awk '{print $1}')" == "$base_sha256" ]] || { echo "BLOCKED: base ISO hash mismatch" >&2; exit 2; }
[[ ! -e "$work" && ! -e "$output" ]] || { echo "BLOCKED: output already exists" >&2; exit 2; }

mkdir -p "$work/iso"
cleanup() { rm -rf "$work"; }
trap cleanup EXIT

xorriso -osirrox on -indev "$base_iso" -extract / "$work/iso" >/dev/null
chmod -R u+w "$work/iso"
for grub_config in "$work/iso/boot/grub/grub.cfg" "$work/iso/boot/grub/loopback.cfg"; do
    [[ -f "$grub_config" ]] || continue
    sed -i -E 's#^([[:space:]]*linux[[:space:]]+/casper/[^[:space:]]*)[[:space:]]+#\1 boot=casper #' "$grub_config"
done
sudo mksquashfs "$rootfs" "$work/iso/casper/ubuntu-server-minimal.squashfs" -comp xz -noappend -all-root >/dev/null
sudo cp "$rootfs/boot/vmlinuz-6.8.0-31-generic" "$work/iso/casper/vmlinuz"
sudo cp "$rootfs/boot/initrd.img-6.8.0-31-generic" "$work/iso/casper/initrd"
printf '%s\n' "$(sudo du -sx --block-size=1 "$rootfs" | cut -f1)" > "$work/iso/casper/filesystem.size"
rootfs_size="$(stat -c %s "$work/iso/casper/ubuntu-server-minimal.squashfs")"
cat > "$work/iso/casper/install-sources.yaml" <<EOF
- default: true
  description:
    en: AIDRAX OS live desktop with owner-gated installation.
  id: aidrax-os
  locale_support: locale-only
  name:
    en: AIDRAX OS
  path: ubuntu-server-minimal.squashfs
  size: $rootfs_size
  type: fsimage
  variant: server
EOF
(cd "$work/iso" && find . -type f ! -path './md5sum.txt' -print0 | sort -z | xargs -0 md5sum > md5sum.txt)

xorriso -as mkisofs \
  -V 'AIDRAX OS 24.04.4 Live amd64' \
  --grub2-mbr --interval:local_fs:0s-15s:zero_mbrpt,zero_gpt:"$base_iso" \
  --protective-msdos-label -partition_cyl_align off -partition_offset 16 --mbr-force-bootable \
  -append_partition 2 28732ac11ff8d211ba4b00a0c93ec93b --interval:local_fs:6640484d-6650643d::"$base_iso" \
  -appended_part_as_gpt -iso_mbr_part_type a2a0d0ebe5b9334487c068b6b72699c7 \
  -c /boot.catalog -b /boot/grub/i386-pc/eltorito.img -no-emul-boot -boot-load-size 4 -boot-info-table --grub2-boot-info \
  -eltorito-alt-boot -e --interval:appended_partition_2_start_1660121s_size_10160d:all:: -no-emul-boot -boot-load-size 10160 \
  -o "$output" "$work/iso" >/dev/null

sha256sum "$output" > "$output.sha256"
xorriso -indev "$output" -report_el_torito plain 2>&1 | grep -q 'El Torito images'
printf 'AO025_ISO_STRUCTURAL_GREEN\nISO=%s\nSHA256=%s\n' "$output" "$(cut -d' ' -f1 "$output.sha256")"
