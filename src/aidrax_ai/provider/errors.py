class ProviderError(RuntimeError):
    """Base error for AIDRAX provider runtime failures."""


class ProviderRegistrationError(ProviderError):
    """Raised when a provider cannot be registered safely."""


class ProviderLifecycleError(ProviderError):
    """Raised when provider initialization or shutdown fails."""


class ProviderAuthorizationError(ProviderError):
    """Raised when an owner-gated provider action is not approved."""


class ProviderExecutionError(ProviderError):
    """Raised when provider execution fails after routing."""
