"""
Audit logger for the distributed OS demo.

This lightweight logger stores events in-memory for easy printing and for
inclusion in the blockchain audit trail. Each event includes a timestamp,
node_id (optional), action and outcome.
"""

from __future__ import annotations

from typing import List, Dict, Any
import time


_events: List[Dict[str, Any]] = []


def log_event(node_id: str, action: str, outcome: str, details: Dict[str, Any] = None) -> None:
    """Record an event for auditing.

    Args:
        node_id: identifier of the node performing the action (or 'system')
        action: short action name e.g. 'request_resource'
        outcome: human-readable outcome or status e.g. 'accepted' or 'rejected'
        details: optional dictionary with extra context
    """
    event = {
        'timestamp': time.time(),
        'node_id': node_id,
        'action': action,
        'outcome': outcome,
        'details': details or {}
    }
    _events.append(event)


def get_events() -> List[Dict[str, Any]]:
    """Return a copy of recorded events."""
    return list(_events)


def set_events(events: List[Dict[str, Any]]) -> None:
    """Replace the in-memory events with the provided list (used when loading state)."""
    global _events
    _events = list(events)


def print_audit_log() -> None:
    """Print events in a readable audit trail format."""
    if not _events:
        print("(no audit events recorded)")
        return

    print("\n== Audit Log ==")
    for ev in _events:
        ts = ev['timestamp']
        nid = ev['node_id']
        action = ev['action']
        outcome = ev['outcome']
        details = ev['details']
        print(f"[{ts:.3f}] node={nid} action={action} outcome={outcome} details={details}")
    print("== End Audit Log ==\n")


def clear_events() -> None:
    """Clear in-memory audit events."""
    global _events
    _events = []
