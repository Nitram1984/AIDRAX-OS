#!/usr/bin/env bash
set -euo pipefail

project="/mnt/DATA2/Projects/AIDRAX-OS"
ao027="$project/Builds/AO-027-AI-Provider-Runtime"
rootfs="/mnt/AIDRAX_SNAP/AIDRAX-BUILDS/active/AIDRAX-OS/AO-027/rootfs-ao027-20260922-r16"
base_iso="/home/maddin/AIDRAX-OS-AO-013-24-dual-path-20260829T174000Z/live-base/ubuntu-24.04.4-live-server-amd64.iso"
base_sha256="e907d92eeec9df64163a7e454cbc8d7755e8ddc7ed42f99dbc80c40f1a138433"
stage="/mnt/AIDRAX_SNAP/AIDRAX-BUILDS/staging/AIDRAX-OS/AO-027"
work="/mnt/AIDRAX_SNAP/AIDRAX-BUILDS/temp/AO-027-r16"
output="$stage/AIDRAX-OS-24.04.4-Live-amd64-AO027-r16.iso"
log="/mnt/AIDRAX_SNAP/AIDRAX-BUILDS/logs/AO-027-r16-build.log"

exec > >(tee "$log") 2>&1

for command in xorriso mksquashfs sha256sum; do
  command -v "$command" >/dev/null || { echo "BLOCKED: missing $command"; exit 2; }
done
[[ -f "$base_iso" ]] || { echo "BLOCKED: base ISO missing"; exit 2; }
[[ -d "$rootfs" ]] || { echo "BLOCKED: AO-027 rootfs missing"; exit 2; }
[[ "$(sha256sum "$base_iso" | awk '{print $1}')" == "$base_sha256" ]] || {
  echo "BLOCKED: base ISO hash mismatch"; exit 2;
}
mkdir -p "$stage"
rm -rf "$work"
mkdir -p "$work/iso"

echo "=== AO-027 ROOTFS VERIFY: udisks2 ==="
sudo dpkg --root="$rootfs" -s udisks2 2>/dev/null | grep -q '^Status: install ok installed$' || {
  echo "BLOCKED: udisks2 package state is not installed"; exit 3;
}

for f in   "$rootfs/usr/libexec/udisks2/udisksd"   "$rootfs/usr/bin/udisksctl"   "$rootfs/usr/lib/systemd/system/udisks2.service"
do
  [[ -e "$f" ]] || { echo "BLOCKED: missing after install: $f"; exit 3; }
done

echo "=== EXTRACT BASE ISO ==="
xorriso -osirrox on -indev "$base_iso" -extract / "$work/iso" >/dev/null
chmod -R u+w "$work/iso"

for grub_config in "$work/iso/boot/grub/grub.cfg" "$work/iso/boot/grub/loopback.cfg"; do
  [[ -f "$grub_config" ]] || continue
  sed -i -E 's#^([[:space:]]*linux[[:space:]]+/casper/[^[:space:]]*)[[:space:]]+#\1 boot=casper #' "$grub_config"
done
echo "=== BUILD LIVE FILESYSTEM ==="
rm -f "$work/iso/casper/filesystem.squashfs"       "$work/iso/casper/ubuntu-server-minimal.squashfs"
sudo mksquashfs "$rootfs" "$work/iso/casper/filesystem.squashfs"   -comp xz -noappend -all-root
ln -s filesystem.squashfs "$work/iso/casper/ubuntu-server-minimal.squashfs"

sudo cp "$rootfs/boot/vmlinuz-6.8.0-31-generic" "$work/iso/casper/vmlinuz"
sudo cp "$rootfs/boot/initrd.img-6.8.0-31-generic" "$work/iso/casper/initrd"
printf '%s\n' "$(sudo du -sx --block-size=1 "$rootfs" | cut -f1)"   > "$work/iso/casper/filesystem.size"

rootfs_size="$(stat -c %s "$work/iso/casper/filesystem.squashfs")"
cat > "$work/iso/casper/install-sources.yaml" <<EOF
- default: true
  description:
    en: AIDRAX OS AO-027 live desktop with owner-gated AI provider runtime.
  id: aidrax-os
  locale_support: locale-only
  name:
    en: AIDRAX OS
  path: filesystem.squashfs
  size: $rootfs_size
  type: fsimage
  variant: server
EOF

(cd "$work/iso" && find . -type f ! -path './md5sum.txt' -print0 | sort -z | xargs -0 md5sum > md5sum.txt)
rm -f "$output" "$output.sha256"
echo "=== ASSEMBLE AO-027 r13 ISO ==="
xorriso -as mkisofs   -V 'AIDRAX OS 24.04.4 Live amd64'   --grub2-mbr --interval:local_fs:0s-15s:zero_mbrpt,zero_gpt:"$base_iso"   --protective-msdos-label -partition_cyl_align off -partition_offset 16 --mbr-force-bootable   -append_partition 2 28732ac11ff8d211ba4b00a0c93ec93b --interval:local_fs:6640484d-6650643d::"$base_iso"   -appended_part_as_gpt -iso_mbr_part_type a2a0d0ebe5b9334487c068b6b72699c7   -c /boot.catalog -b /boot/grub/i386-pc/eltorito.img -no-emul-boot   -boot-load-size 4 -boot-info-table --grub2-boot-info   -eltorito-alt-boot -e --interval:appended_partition_2_start_1660121s_size_10160d:all::   -no-emul-boot -boot-load-size 10160   -o "$output" "$work/iso" >/dev/null

sha256sum "$output" > "$output.sha256"
xorriso -indev "$output" -find /casper/filesystem.squashfs -exec lsdl 2>/dev/null   | grep -q filesystem.squashfs
xorriso -indev "$output" -report_el_torito plain 2>&1 | grep -q 'El Torito images'

echo "AO027_R16_ISO_BUILD_GREEN"
echo "ISO=$output"
echo "SHA256=$(cut -d' ' -f1 "$output.sha256")"
ls -lh "$output" "$output.sha256"
