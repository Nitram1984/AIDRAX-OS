# AO-001A Integration Gate

This artifact is integration-ready as a contract, not approved for host or UI
deployment. The following gates are cumulative and require recorded Owner
approval before an adapter is introduced:

1. **Asset intake:** supply licensed/original assets and populate the catalog
   with immutable relative paths plus independently computed SHA-256 values.
2. **Byte verification:** validate every catalog reference against the approved
   asset bundle; reject missing, extra, or hash-mismatched files.
3. **Adapter review:** choose the narrow target (boot, SDDM/login, lock,
   desktop, installer, or recovery). Keep authentication and host controls
   outside the adapter.
4. **Safety review:** for decorative video provide a static fallback, preserve
   the prior theme/configuration, and validate accessibility, performance and
   offline boot behavior.
5. **Acceptance:** test real target behavior, including a successful boot/login
   and the documented restore path. Structural GREEN is not UI acceptance.

No gate authorizes automatic deployment. `AUTO_APPLY_OFF` is the operating
posture: AO-001A returns data only and does not access SDDM, systemd, DBus,
audio, display or power interfaces.
