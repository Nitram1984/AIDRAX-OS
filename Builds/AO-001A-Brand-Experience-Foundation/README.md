# AIDRAX OS — AO-001A Brand & Experience Foundation

**Release:** AO-001A.0.0-alpha.3  
**Status:** Owner-approved contract; additive only

AO-001A separates the two new platform boundaries:

- **Brand Engine** validates a versioned catalog of approved brand assets.
- **Experience Engine** converts declared lifecycle events into inert presentation cues.

It intentionally ships **no media assets**, installs no SDDM theme, opens no GUI,
and executes no audio, video, DBus, systemd, session, power, or network action.
An adapter may consume a returned cue only after its own explicit integration and
Owner-Gate review. Asset content remains an external, approved supply input.

## Validation first

`docs/VBC-INVENTORY-REPORT.md` records the inspected AO-001/AO-006 boundaries,
their classification, and why this package is an additive extension instead of a
replacement. `config/brand-catalog.json` is deliberately empty: missing source
assets must be represented honestly, never by placeholder artwork or invented
paths.

## Verify and package

```bash
./build/verify_release.sh
./build/build_release.sh
./build/package_release.sh
```

GREEN proves the contracts, schemas, and unit tests agree. It does not prove a
boot animation, login screen, desktop experience, or ISO integration.

The recorded Owner approval covers the controlled AIDRAX OS work scope;
see `docs/OWNER-APPROVAL.md`. It does not waive evidence, safety, supply-chain,
or target-specific acceptance gates.

## Rollback

The package is self-contained at `Builds/AO-001A-Brand-Experience-Foundation`.
It does not mutate AO-001, AO-006, host configuration, or existing media. Remove
only this package after an Owner-approved review if rollback is required.
