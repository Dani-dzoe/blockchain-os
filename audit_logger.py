"""
Audit logger for a blockchain-based OS.

Responsibilities:
- Record system events with timestamp, node ID, action, and outcome.
- Persist events to a rotating file logger for durability.
- Keep an in-memory list for quick inspection and printing.
- Provide a readable audit trail and helpers to extract audit entries
  from a `Blockchain` instance.

Importance of auditing:
- Auditing provides an immutable trail of system actions which is
  critical for forensic analysis, compliance, and detecting misuse.
  In a blockchain-based OS, combining on-chain events with system
  logs gives stronger guarantees about who did what and when.
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class AuditLogger:
    """Audit logger storing events and printing readable audit trails.

    Each event contains:
    - timestamp (UTC ISO8601 string)
    - node_id (who performed the action)
    - action (short action description)
    - outcome (success/failure/details)
    - metadata (optional dict with extra context)

    The class writes structured text to a rotating log file and keeps a
    short-term in-memory list for quick printing.
    """

    def __init__(self, name: str = "audit", logfile: str = "audit.log", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        # avoid duplicate handlers if constructed multiple times
        if not self.logger.handlers:
            fh = RotatingFileHandler(logfile, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
            fmt = "%(asctime)s | %(levelname)s | %(message)s"
            fh.setFormatter(logging.Formatter(fmt))
            self.logger.addHandler(fh)

        # in-memory events store (useful for immediate display/testing)
        self._events: List[Dict[str, Any]] = []

    def _now(self) -> str:
        # Use timezone-aware UTC timestamps to avoid deprecation warnings
        # and to provide a clear UTC offset. Keep the trailing 'Z' for
        # compact ISO-like formatting.
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def log_event(self, node_id: str, action: str, outcome: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record an audit event.

        Args:
            node_id: Identifier of the node/user that performed the action.
            action: Short description of the action.
            outcome: Result of the action (e.g., "success", "denied", error message).
            metadata: Optional additional data (block index, tx id, etc.).
        """
        entry = {
            "timestamp": self._now(),
            "node_id": node_id,
            "action": action,
            "outcome": outcome,
            "metadata": metadata or {},
        }

        # store in-memory
        self._events.append(entry)

        # write to persistent log for long-term auditing
        msg = f"node={node_id} action={action} outcome={outcome} meta={entry['metadata']}"
        self.logger.info(msg)

    def get_events(self) -> List[Dict[str, Any]]:
        """Return a shallow copy of recorded in-memory events."""
        return list(self._events)

    def print_audit_trail(self, events: Optional[List[Dict[str, Any]]] = None) -> None:
        """Print events in a readable audit format.

        If `events` is None, prints the current in-memory events.
        """
        to_print = events if events is not None else self._events
        if not to_print:
            print("No audit events available.")
            return

        for e in to_print:
            ts = e.get("timestamp")
            node = e.get("node_id")
            action = e.get("action")
            outcome = e.get("outcome")
            meta = e.get("metadata") or {}
            parts = [f"[{ts}]", f"Node: {node}", f"Action: {action}", f"Outcome: {outcome}"]
            # add some well-known metadata fields if present for readability
            if isinstance(meta, dict):
                if "block_index" in meta:
                    parts.append(f"Block: {meta['block_index']}")
                if "transaction_type" in meta:
                    parts.append(f"TxType: {meta['transaction_type']}")
                if "resource_type" in meta:
                    parts.append(f"Resource: {meta['resource_type']}")
                if "amount" in meta:
                    parts.append(f"Amount: {meta['amount']}")
            # include any remaining metadata
            remaining = {k: v for k, v in (meta or {}).items() if k not in ("block_index", "transaction_type", "resource_type", "amount")}
            if remaining:
                parts.append(f"Meta: {remaining}")

            print(" | ".join(parts))

    def display_from_blockchain(self, blockchain: Any) -> None:
        """Extract a readable audit trail from a `Blockchain` instance.

        The method is defensive and will ignore missing attributes. It
        creates human-friendly audit entries for each transaction in each
        block and prints them. It does not modify the blockchain.
        """
        if not hasattr(blockchain, "chain"):
            print("Provided object is not a Blockchain (missing 'chain').")
            return

        trail: List[Dict[str, Any]] = []
        for block in getattr(blockchain, "chain", []):
            block_index = getattr(block, "index", None)
            block_ts = getattr(block, "timestamp", None)
            transactions = getattr(block, "transactions", []) or []
            for tx in transactions:
                # try to read common transaction attributes used in this repo
                node_id = getattr(tx, "node_id", "unknown")
                tx_type = getattr(tx, "transaction_type", None)
                resource = getattr(tx, "resource_type", None)
                amount = getattr(tx, "amount", None)

                entry = {
                    "timestamp": block_ts or self._now(),
                    "node_id": node_id,
                    "action": tx_type or "transaction",
                    "outcome": "on-chain",
                    "metadata": {
                        "block_index": block_index,
                        "transaction_type": tx_type,
                        "resource_type": resource,
                        "amount": amount,
                    },
                }
                trail.append(entry)

        # print the derived trail
        self.print_audit_trail(trail)


# Provide a module-level default logger for convenience
default_audit_logger = AuditLogger()


if __name__ == "__main__":
    # Quick demo when run directly
    al = AuditLogger(logfile="audit_demo.log")
    al.log_event("node-1", "start_service", "success")
    al.log_event("node-2", "allocate_resource", "denied", metadata={"resource_type": "cpu", "amount": 2})
    al.print_audit_trail()
