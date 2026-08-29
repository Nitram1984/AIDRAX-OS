# Lock-Format

Die vom Owner freigegebene JSON-Datei muss exakt ein Ubuntu-24.04-Minimal-amd64-Ziel sowie die Objekte `base_image`, `apt_snapshot` und `packages` enthalten. `base_image.reference` benennt ein Registry-Repository und `base_image.digest` muss ein SHA-256-Digest mit 64 Hex-Zeichen sein. `apt_snapshot.url` muss eine HTTPS-URL ohne Zugangsdaten sein. Die Paketliste muss mindestens `xorriso`, `squashfs-tools` und `grub-efi-amd64-bin` mit je einer konkreten, nichtleeren Version sperren.

AO-010 enthält bewusst keine angeblich freigegebenen Image-Digests, Snapshot-URLs oder Paketversionen. Diese produktionsrelevanten Fakten werden erst als überprüfbarer Owner-Lock akzeptiert.
