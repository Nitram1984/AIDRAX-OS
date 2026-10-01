"""AIDRAX OS core package metadata."""

__version__ = "0.15.0a2"

from .errors import (
    CapabilityDependencyError,
    CapabilityDiscoveryError,
    CapabilityFactoryError,
    CapabilityLifecycleError,
    CapabilityManifestError,
    CapabilityPermissionError,
    CapabilityRegistrationError,
    ConfigurationError,
    PipelineError,
    QueueOverflowError,
    RegistryError,
    RuntimeFailure,
    RuntimeFailureCode,
    RuntimeTypeError,
    RuntimeValidationError,
    SubscriberFailureError,
    SubscriberTimeoutError,
)

__all__ = [
    "CapabilityDependencyError",
    "CapabilityDiscoveryError",
    "CapabilityFactoryError",
    "CapabilityLifecycleError",
    "CapabilityManifestError",
    "CapabilityPermissionError",
    "CapabilityRegistrationError",
    "ConfigurationError",
    "PipelineError",
    "QueueOverflowError",
    "RegistryError",
    "RuntimeFailure",
    "RuntimeFailureCode",
    "RuntimeTypeError",
    "RuntimeValidationError",
    "SubscriberFailureError",
    "SubscriberTimeoutError",
    "__version__",
]
