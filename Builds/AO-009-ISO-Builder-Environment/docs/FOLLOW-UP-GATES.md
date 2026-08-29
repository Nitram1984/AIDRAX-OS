# Folge-Gates

AO-009 erstellt weder ein Builder-Image noch Testmedien. Der reproduzierbare Bau kann erst beginnen, wenn alle folgenden Owner-Gates nachweisbar freigegeben sind:

1. Ein unveränderlicher Ubuntu-24.04-Base-Image-Digest, eine Snapshot-Quelle und ein Paket-Lockfile.
2. Eine rootless, ephemere Builder-Ausführung ohne Host-Mounts, Geräte oder Secrets.
3. Ein Signaturverfahren inklusive Schlüsselverwahrung und unabhängiger Prüfung; AO-009 importiert, erzeugt oder registriert keine Schlüssel.
4. Eine Boot-Testmatrix mit VM-UEFI-Konfiguration, Secure-Boot-Negativfall und Recovery-Nachweis.
5. Eine separate reale Hardwareabnahme mit Owner-Freigabe.

Der Builder darf erst nach diesen Gates in einem späteren, explizit freigegebenen Build erzeugt oder gestartet werden.
