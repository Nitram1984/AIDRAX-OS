"""Classified failures for AIDRAX OS runtime boundaries."""
from __future__ import annotations

from enum import StrEnum
from typing import Any


class RuntimeFailureCode(StrEnum):
    CONFIGURATION = "configuration"; REGISTRY = "registry"; PIPELINE = "pipeline"; VALIDATION = "validation"; TYPE = "type"
    QUEUE_OVERFLOW = "queue_overflow"; SUBSCRIBER_FAILURE = "subscriber_failure"; SUBSCRIBER_TIMEOUT = "subscriber_timeout"
    CAPABILITY_MANIFEST = "capability_manifest"; CAPABILITY_REGISTRATION = "capability_registration"; CAPABILITY_DEPENDENCY = "capability_dependency"
    CAPABILITY_PERMISSION = "capability_permission"; CAPABILITY_LIFECYCLE = "capability_lifecycle"; CAPABILITY_DISCOVERY = "capability_discovery"; CAPABILITY_FACTORY = "capability_factory"


class RuntimeFailure(RuntimeError):
    def __init__(self, code: RuntimeFailureCode, message: str, *, cause: BaseException | None = None, recovered: bool = False) -> None:
        super().__init__(message); self.code = code; self.cause = cause; self.recovered = recovered
    def status(self) -> dict[str, Any]:
        return {"status": "failed", "code": self.code.value, "message": str(self), "recovered": self.recovered}


class ConfigurationError(RuntimeFailure, ValueError):
    def __init__(self, message: str, *, cause: BaseException | None = None) -> None: RuntimeFailure.__init__(self, RuntimeFailureCode.CONFIGURATION, message, cause=cause)
class RegistryError(RuntimeFailure, ValueError):
    def __init__(self, message: str, *, cause: BaseException | None = None) -> None: RuntimeFailure.__init__(self, RuntimeFailureCode.REGISTRY, message, cause=cause)
class RuntimeValidationError(RuntimeFailure, ValueError):
    def __init__(self, message: str) -> None: RuntimeFailure.__init__(self, RuntimeFailureCode.VALIDATION, message)
class RuntimeTypeError(RuntimeFailure, TypeError):
    def __init__(self, message: str) -> None: RuntimeFailure.__init__(self, RuntimeFailureCode.TYPE, message)
class QueueOverflowError(RuntimeFailure):
    def __init__(self, message: str) -> None: RuntimeFailure.__init__(self, RuntimeFailureCode.QUEUE_OVERFLOW, message)
class SubscriberFailureError(RuntimeFailure):
    def __init__(self, message: str, *, cause: BaseException | None = None) -> None: RuntimeFailure.__init__(self, RuntimeFailureCode.SUBSCRIBER_FAILURE, message, cause=cause)
class SubscriberTimeoutError(RuntimeFailure):
    def __init__(self, message: str) -> None: RuntimeFailure.__init__(self, RuntimeFailureCode.SUBSCRIBER_TIMEOUT, message)
class PipelineError(RuntimeFailure):
    def __init__(self, phase: str, message: str, *, cause: BaseException | None = None, recovered: bool = False) -> None:
        super().__init__(RuntimeFailureCode.PIPELINE, message, cause=cause, recovered=recovered); self.phase = phase
    def status(self) -> dict[str, Any]: return {**super().status(), "phase": self.phase}

def _capability_error(name: str, code: RuntimeFailureCode, value_error: bool = False):
    base = (RuntimeFailure, ValueError) if value_error else (RuntimeFailure,)
    def init(self, message: str, *, cause: BaseException | None = None) -> None: RuntimeFailure.__init__(self, code, message, cause=cause)
    return type(name, base, {"__init__": init})

CapabilityManifestError = _capability_error("CapabilityManifestError", RuntimeFailureCode.CAPABILITY_MANIFEST, True)
CapabilityRegistrationError = _capability_error("CapabilityRegistrationError", RuntimeFailureCode.CAPABILITY_REGISTRATION, True)
CapabilityDependencyError = _capability_error("CapabilityDependencyError", RuntimeFailureCode.CAPABILITY_DEPENDENCY, True)
CapabilityPermissionError = _capability_error("CapabilityPermissionError", RuntimeFailureCode.CAPABILITY_PERMISSION, True)
CapabilityLifecycleError = _capability_error("CapabilityLifecycleError", RuntimeFailureCode.CAPABILITY_LIFECYCLE)
CapabilityDiscoveryError = _capability_error("CapabilityDiscoveryError", RuntimeFailureCode.CAPABILITY_DISCOVERY, True)
CapabilityFactoryError = _capability_error("CapabilityFactoryError", RuntimeFailureCode.CAPABILITY_FACTORY)
