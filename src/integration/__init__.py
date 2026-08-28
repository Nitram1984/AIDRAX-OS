"""AIDRAX OS integration pipeline."""

from aidrax_core.errors import PipelineError

from .pipeline import integrate

__all__ = ["PipelineError", "integrate"]
