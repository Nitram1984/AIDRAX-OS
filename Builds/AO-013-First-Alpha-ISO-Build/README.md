# AIDRAX OS — AO-013 First Alpha ISO Build

AO-013 ist die letzte Autorisierungsstufe vor dem ersten Alpha-ISO-Build. Es prüft einen AO-010-rootless Build-Kontext, einen AO-012-`VERIFIED`-Quellreport und alle Alpha-Owner-Gates. Es baut selbst keine ISO: Der konkrete Container-Recipe, die freigegebenen Quellen und die spätere Ausführung sind bewusst getrennt, damit ein fehlender Nachweis niemals als Build-Erfolg erscheint.

```bash
PYTHONPATH=src python3 src/aidrax_alpha_iso_build/prepare.py \
  --builder-plan /pfad/zu/podman-build-plan.json \
  --source-report /pfad/zu/ao-012-report.json \
  --owner-gates /pfad/zu/owner-gates.json --dry-run
```

Nur mit `--apply --request /neuer/pfad/alpha-build-request.json` wird ein neuer, hash-gebundener Build-Antrag geschrieben. Die reale ISO-Erzeugung, Signatur und VM-Boot-Abnahme bleiben weitere explizite Owner-Gates.
