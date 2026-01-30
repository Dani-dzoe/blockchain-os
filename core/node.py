"""
Node entity for the distributed operating system demo.

This module defines a clear, well-documented `Node` class used throughout
other components (consensus, resource manager, CLI, etc.). Each node
tracks resource quotas and current allocations and exposes helper methods
for validation and serialization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Node:
    """Represents a participant node in the distributed OS simulation.

    Attributes:
        node_id: Unique identifier for the node (string)
        quotas: Per-resource quotas (e.g., {'CPU': 4.0, 'Storage': 10.0})
        allocated: Current per-resource allocations (same keys as quotas)
        status: Simple status flag such as 'active' or 'inactive'
    """

    node_id: str
    quotas: Dict[str, float] = field(default_factory=dict)
    allocated: Dict[str, float] = field(default_factory=dict)
    status: str = "active"

    def __post_init__(self):
        # Normalize quotas and allocated so keys match and values are floats
        for k, v in list(self.quotas.items()):
            try:
                self.quotas[k] = float(v)
            except Exception:
                raise ValueError(f"Quota for {k} must be numeric")

        # Initialize allocated keys to mirror quotas (default 0)
        for k in list(self.quotas.keys()):
            self.allocated.setdefault(k, 0.0)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the node to a dictionary for logging or transport."""
        return {
            "node_id": self.node_id,
            "quotas": dict(self.quotas),
            "allocated": dict(self.allocated),
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        """Create a Node instance from a dictionary (used for persistence).

        Accepts the same shape produced by `to_dict()`.
        """
        node_id = data.get("node_id")
        quotas = data.get("quotas", {})
        allocated = data.get("allocated", {})
        status = data.get("status", "active")
        node = cls(node_id=node_id, quotas=quotas, allocated=allocated, status=status)
        return node

    def can_allocate(self, resource: str, amount: float) -> bool:
        """Return True if `amount` of `resource` can be allocated without
        exceeding the node's quota.
        """
        if resource not in self.quotas:
            return False
        if amount < 0:
            return False
        return (self.allocated.get(resource, 0.0) + amount) <= self.quotas[resource]

    def allocate(self, resource: str, amount: float) -> None:
        """Apply allocation to this node. Caller should validate first.

        Raises ValueError if allocation would exceed quota or if resource unknown.
        """
        if resource not in self.quotas:
            raise ValueError(f"Unknown resource: {resource}")
        if amount < 0:
            raise ValueError("Amount must be positive")
        if not self.can_allocate(resource, amount):
            raise ValueError(f"Allocation would exceed quota for {resource}")
        self.allocated[resource] = self.allocated.get(resource, 0.0) + amount

    def can_release(self, resource: str, amount: float) -> bool:
        """Return True if `amount` of `resource` can be released (i.e., allocated >= amount)."""
        if resource not in self.allocated:
            return False
        if amount < 0:
            return False
        return self.allocated.get(resource, 0.0) >= amount

    def release(self, resource: str, amount: float) -> None:
        """Release an allocated resource from this node. Caller should validate first.

        Raises ValueError if release amount is invalid.
        """
        if resource not in self.allocated:
            raise ValueError(f"Unknown resource: {resource}")
        if amount < 0:
            raise ValueError("Amount must be positive")
        if not self.can_release(resource, amount):
            raise ValueError(f"Cannot release {amount} {resource}; only {self.allocated.get(resource,0)} allocated")
        self.allocated[resource] = self.allocated.get(resource, 0.0) - amount
        # Normalize tiny float negatives to zero
        if self.allocated[resource] < 1e-12:
            self.allocated[resource] = 0.0

    def __str__(self) -> str:
        return f"Node(id={self.node_id}, status={self.status})"
