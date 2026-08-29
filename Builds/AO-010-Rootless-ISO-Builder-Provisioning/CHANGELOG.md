# Changelog

## AO-010.0.0-alpha.1

- Ergänzt einen owner-gated Rootless-Provisionierer für den späteren ISO-Builder.
- Validiert immutable Image-, APT-Snapshot- und Paket-Locks vor jeder Kontext-Erzeugung.
- Erzeugt ausschließlich einen lokalen, rootless Podman-Build-Kontext; keine ISO und keine Host-, Schlüssel-, Firmware- oder Datenträgeränderungen.
