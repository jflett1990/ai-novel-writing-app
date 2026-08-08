"""Backward-compatible import for the former enhanced entry point.

All enhanced routes now live in the canonical ``app:app`` application.
"""

from app import app


__all__ = ["app"]
