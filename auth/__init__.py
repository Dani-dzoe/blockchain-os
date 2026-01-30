"""
Authentication Package

This package provides node authentication and identity management.
The AuthManager issues unique tokens to nodes and verifies their identity
before allowing operations.
"""

from .auth import AuthManager

__all__ = ['AuthManager']

