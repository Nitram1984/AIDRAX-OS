# AO-023 Integration Gate

AO-023 authorizes no ISO build by itself. Before an ISO attempt, provide a
signed boot-input lock, deterministic EFI/GRUB layout, a reproducible SquashFS
recipe, SDDM/Desktop launch adapter, static branding fallback, VM boot proof,
and a tested recovery entry. The installer action must invoke AO-007 preflight
and remain owner-gated.
