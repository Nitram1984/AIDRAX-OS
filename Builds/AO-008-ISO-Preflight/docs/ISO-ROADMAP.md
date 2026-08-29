# ISO-Roadmap und Folge-Gates

AO-008 ist keine ISO-Implementierung. Jeder folgende Schritt ist separat owner-freizugeben und wird erst nach erfolgreichem, archiviertem Preflight begonnen.

1. **Paketquellen-Gate:** versionsfixierte, reproduzierbare Ubuntu-24.04-Quellen mit Provenance-Nachweis.
2. **Builder-Gate:** isolierte Builder-Umgebung mit dokumentiertem Toolchain-Image und ohne Zugriff auf Produktionsdatenträger.
3. **Signatur-Gate:** Verfahren, Schlüsselverwahrung, Rotation und unabhängige Verifikation; keine Schlüssel im Repository.
4. **Boot-Test-Gate:** UEFI-/Secure-Boot-Testmatrix für VM und repräsentative Hardware, inklusive Negativfällen.
5. **Recovery-Gate:** geprüftes Recovery-Medium, Wiederherstellungsablauf und unabhängiger Rücksicherungsnachweis.
6. **Hardware-Abnahme:** reale Hardwareabnahme mit Owner-Freigabe; erst danach darf ein Release-Kandidat entstehen.

Kein Gate legitimiert einen automatischen Secure-Boot-Bypass, automatisches Key-Enrolment oder MOK-Aktionen.
