class AIDRAXError(Exception):
    """Base exception for AIDRAX OS."""
    pass


class ConfigurationError(AIDRAXError):
    pass


class ModuleError(AIDRAXError):
    pass
