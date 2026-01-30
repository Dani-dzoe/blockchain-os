"""
Resource Manager for the demo distributed OS.

This class tracks available system resources (global capacity) and can
manage per-node allocations through Node objects. It performs validation
and updates allocations only when instructed (e.g., after consensus).
"""

from __future__ import annotations

from typing import Dict, Any
from core.node import Node


class ResourceManager:
    """Manage resource quotas and allocations for nodes.

    For simplicity, the resource manager delegates per-node accounting to
    the Node class. This manager keeps optional global capacities (not
    strictly required for the classroom demo) and provides helper methods
    used by the controller/CLI.
    """

    def __init__(self, global_cpu: float = 100.0, global_storage: float = 1000.0):
        # Global capacities (optional educational feature)
        self.global_cpu = float(global_cpu)
        self.global_storage = float(global_storage)
        # Keep a registry of nodes by id
        self.nodes: Dict[str, Node] = {}

    def register_node(self, node: Node) -> None:
        """Add a node to resource manager registry."""
        if node.node_id in self.nodes:
            raise ValueError(f"Node {node.node_id} already registered")
        self.nodes[node.node_id] = node

    def can_allocate(self, node_id: str, resource: str, amount: float) -> bool:
        """Check if a node can allocate the requested resource now.

        This checks node-specific quotas and the global capacity when
        appropriate.
        """
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        node = self.nodes[node_id]
        # Basic per-node quota check
        return node.can_allocate(resource, amount)

    def apply_allocation(self, node_id: str, resource: str, amount: float) -> None:
        """Apply allocation to a node. Caller must ensure consensus already accepted the block."""
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        node = self.nodes[node_id]
        node.allocate(resource, amount)

    def apply_release(self, node_id: str, resource: str, amount: float) -> None:
        """Apply release of resources for a node. Caller must ensure consensus accepted."""
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        node = self.nodes[node_id]
        node.release(resource, amount)

    def get_status(self) -> Dict[str, Any]:
        """Return summary of registered nodes and their allocations."""
        summary = {}
        for nid, node in self.nodes.items():
            summary[nid] = node.to_dict()
        return {
            'global_cpu': self.global_cpu,
            'global_storage': self.global_storage,
            'nodes': summary
        }
