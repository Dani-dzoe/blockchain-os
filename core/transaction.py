"""
Transaction model for the distributed operating system demo.

A Transaction represents an OS-level action (resource allocation or
release) requested by a node. The class includes validation logic to
ensure transactions are well-formed and informative error messages for
educational clarity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict
import time


VALID_RESOURCES = ["CPU", "Memory", "Storage", "Bandwidth"]
VALID_TYPES = ["allocate", "release"]


@dataclass
class Transaction:
    """Represents a single transaction in the system.

    Attributes:
        node_id: ID of the requesting node
        resource_type: one of VALID_RESOURCES
        amount: positive numeric amount
        transaction_type: 'allocate' or 'release'
        timestamp: epoch float when the transaction was created
    """

    node_id: str
    resource_type: str
    amount: float
    transaction_type: str
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        # Validate node_id
        if not self.node_id or not str(self.node_id).strip():
            raise ValueError("node_id cannot be empty")
        self.node_id = str(self.node_id).strip()

        # Validate resource_type
        if self.resource_type not in VALID_RESOURCES:
            raise ValueError(f"resource_type must be one of {VALID_RESOURCES}")

        # Validate amount
        try:
            self.amount = float(self.amount)
        except Exception:
            raise ValueError("amount must be a number")
        if self.amount <= 0:
            raise ValueError("amount must be greater than zero")

        # Validate transaction_type
        if self.transaction_type not in VALID_TYPES:
            raise ValueError(f"transaction_type must be one of {VALID_TYPES}")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize transaction to a JSON-safe dictionary."""
        return {
            "node_id": self.node_id,
            "resource_type": self.resource_type,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "timestamp": self.timestamp,
        }

    def __str__(self) -> str:
        return f"{self.transaction_type.upper()} {self.amount} {self.resource_type} by {self.node_id} @ {self.timestamp:.3f}"
