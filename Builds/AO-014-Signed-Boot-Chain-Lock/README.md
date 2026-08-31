# AIDRAX OS — AO-014 Signed Boot Chain Lock

AO-014 pins and locally verifies the Ubuntu 24.04 signed UEFI bootstrap artifacts: `shim-signed` and `grub-efi-amd64-signed`. It does not create media, register MOK keys, modify firmware, or claim that the dependency closure is already an installable ISO boot chain.

Run `python3 build/verify_release.py` and `python3 build/build_release.py`.
