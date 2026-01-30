"""
Persistence helpers for saving/loading system state to/from JSON.

Saves and loads a single JSON file containing:
- nodes: list of node dicts
- chain: list of block dicts
- audit_events: list of audit event dicts

Implements atomic writes by writing to a temporary file first, then renaming.
This ensures state is never corrupted if the process crashes mid-write.
"""

from __future__ import annotations

import json
import os
import tempfile
from typing import Dict, Any, List
from pathlib import Path


DEFAULT_STATE_FILE = Path("system_state.json")


def save_state(file_path: Path = DEFAULT_STATE_FILE, *, nodes: List[Dict[str, Any]], chain: List[Dict[str, Any]], audit_events: List[Dict[str, Any]]) -> None:
    """Save system state to JSON file atomically.

    Uses atomic write pattern: write to temp file, then rename.
    This prevents corruption if interrupted.
    """
    payload = {
        "nodes": nodes,
        "chain": chain,
        "audit_events": audit_events,
    }

    # Write to a temporary file in the same directory as the target
    dir_path = file_path.parent
    dir_path.mkdir(parents=True, exist_ok=True)

    # Create temp file in same directory to ensure atomic rename works
    fd, temp_path = tempfile.mkstemp(dir=dir_path, prefix=".tmp_state_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        # Atomic rename (overwrites target on POSIX systems)
        os.replace(temp_path, file_path)
    except Exception:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def load_state(file_path: Path = DEFAULT_STATE_FILE) -> Dict[str, Any]:
    """Load system state from JSON file.

    Returns empty state if file doesn't exist.
    """
    if not file_path.exists():
        return {"nodes": [], "chain": [], "audit_events": []}
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        "nodes": data.get("nodes", []),
        "chain": data.get("chain", []),
        "audit_events": data.get("audit_events", []),
    }


