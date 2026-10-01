# Integration

Die Integration ist separat und additiv:

```bash
./installer/install.sh --dry-run --target /mnt/DATA2/Projects/AIDRAX-OS
AIDRAX_OWNER_APPROVED=YES ./installer/install.sh --apply --target /mnt/DATA2/Projects/AIDRAX-OS
```

Vor `--apply` müssen Zielpfad, Git-Diff, Contract-Kompatibilität und Owner-Freigabe geprüft sein. Das Ziel darf bereits **kein** `ao-001-full` enthalten. Der Vorgang kopiert nur dieses Paket nach `<target>/ao-001-full` und fasst keine vorhandenen Quell- oder Konfigurationsdateien an.

Für einen späteren echten Merge muss ein Owner eine konkrete Mapping-Entscheidung treffen; das Paket nimmt diese Architekturentscheidung nicht vor.
