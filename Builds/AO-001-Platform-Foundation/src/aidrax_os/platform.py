"""Minimal, dependency-free platform contract for AO-001."""

BOOT_COMPONENTS = (
    "configuration", "logging", "ATLAS", "HERMES", "ARGUS",
    "CapabilityRuntime", "MissionControl",
)


def boot_plan() -> tuple[str, ...]:
    """Return the immutable canonical AO-001 boot order."""
    return BOOT_COMPONENTS
