"""
Persistence helpers for saving/loading system state to/from JSON.

Saves and loads a single JSON file containing:
- nodes: list of node dicts
- chain: list of block dicts
- audit_events: list of audit event dicts
- checksum: SHA-256 hash of the data to detect tampering

Implements atomic writes by writing to a temporary file first, then renaming.
This ensures state is never corrupted if the process crashes mid-write.

The checksum provides an additional layer of tamper detection: if someone
manually edits the JSON file, the checksum won't match and we can detect
unauthorized modifications.
"""

from __future__ import annotations

import json
import os
import tempfile
import hashlib
from typing import Dict, Any, List, Tuple
from pathlib import Path


DEFAULT_STATE_FILE = Path("system_state.json")


def compute_data_checksum(nodes: List[Dict[str, Any]], chain: List[Dict[str, Any]], audit_events: List[Dict[str, Any]]) -> str:
    """Compute SHA-256 checksum of the system state data.

    This provides tamper detection: if someone manually edits the JSON file,
    the checksum won't match and we can detect unauthorized modifications.
    """
    data_string = json.dumps({
        "nodes": nodes,
        "chain": chain,
        "audit_events": audit_events
    }, sort_keys=True)
    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()


def verify_data_integrity(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Verify that loaded data hasn't been tampered with.

    Returns (True, "OK") if checksum matches, (False, reason) otherwise.
    """
    stored_checksum = data.get("checksum")
    if not stored_checksum:
        return False, "No checksum found - file may have been manually edited"

    nodes = data.get("nodes", [])
    chain = data.get("chain", [])
    audit_events = data.get("audit_events", [])

    computed_checksum = compute_data_checksum(nodes, chain, audit_events)

    if stored_checksum != computed_checksum:
        return False, f"Checksum mismatch - file has been tampered with!\nStored: {stored_checksum[:16]}...\nComputed: {computed_checksum[:16]}..."

    return True, "Integrity verified"


def save_state(file_path: Path = DEFAULT_STATE_FILE, *, nodes: List[Dict[str, Any]], chain: List[Dict[str, Any]], audit_events: List[Dict[str, Any]]) -> None:
    """Save system state to JSON file atomically.

    Uses atomic write pattern: write to temp file, then rename.
    This prevents corruption if interrupted.

    Also computes and stores a checksum to detect manual tampering.
    """
    # Compute checksum of the data
    checksum = compute_data_checksum(nodes, chain, audit_events)

    payload = {
        "nodes": nodes,
        "chain": chain,
        "audit_events": audit_events,
        "checksum": checksum,  # Include checksum to detect tampering
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

    Verifies the checksum to detect if the file has been manually tampered with.
    """
    if not file_path.exists():
        return {"nodes": [], "chain": [], "audit_events": [], "checksum": None, "integrity_ok": True}

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Verify integrity
    integrity_ok, integrity_msg = verify_data_integrity(data)

    return {
        "nodes": data.get("nodes", []),
        "chain": data.get("chain", []),
        "audit_events": data.get("audit_events", []),
        "checksum": data.get("checksum"),
        "integrity_ok": integrity_ok,
        "integrity_msg": integrity_msg,
    }


