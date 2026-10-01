# Folge-Gates

AO-010 darf nur mit allen drei dokumentierten Owner-Gates einen lokalen Kontext schreiben. Die spätere `podman build`-Ausführung bleibt ein eigenes Gate und verlangt zusätzlich:

1. unabhängige Prüfung von Base-Image-Digest, Snapshot und Paket-Lock;
2. einen verfügbaren rootless Podman-Host ohne Host-Mounts, Geräte oder Secrets;
3. einen VM-Boot-Test nach AO-009-Testmatrix;
4. separate Freigaben für Signaturkette, reale Hardware und jedes Installationsmedium.

Keine dieser Freigaben erzeugt oder importiert Schlüssel, schreibt Firmware/NVRAM oder beschreibt Datenträger.
