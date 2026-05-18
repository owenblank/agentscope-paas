"""
Compression Package for AgentScope-PaaS

This package provides intelligent context compression strategies.
"""

from .engine import (
    ContextCompressionEngine,
    CompressionStrategy,
    CompressionQuality,
    ContextCompressionError,
    compression_engine
)

__all__ = [
    'ContextCompressionEngine',
    'CompressionStrategy',
    'CompressionQuality',
    'ContextCompressionError',
    'compression_engine'
]