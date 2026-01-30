"""
Audit Logging Package

This package provides system-wide audit logging capabilities.
All important system events are logged with timestamps, node IDs,
actions, and outcomes for accountability and debugging.
"""

from .audit_logger import log_event, print_audit_log, get_events, set_events

__all__ = ['log_event', 'print_audit_log', 'get_events', 'set_events']

