"""
Node Management Module - core/node.py

This module defines the Node class, which represents a participant in the
distributed operating system. Each node has:
- A unique identifier
- Resource allocations (CPU and storage limits)
- Current resource usage tracking
- A status indicating whether it's active in the system

EDUCATIONAL NOTE:
In a distributed OS, nodes compete for resources. This class enforces
limits and tracks usage, ensuring no node exceeds its allocation.
"""

from datetime import datetime
from typing import Dict, Any
import uuid


class Node:
    
    
    # Class variable to track all node IDs (ensures uniqueness)
    _all_node_ids = set()
    
    def __init__(
        self,
        node_id: str = None,
        allocated_cpu: int = 100,
        allocated_storage: int = 1024
    ):
        
        # Generate unique ID if not provided
        if node_id is None:
            node_id = f"NODE_{uuid.uuid4().hex[:8].upper()}"
        
        # Validate node_id uniqueness
        if node_id in Node._all_node_ids:
            raise ValueError(f"Node ID '{node_id}' already exists. Node IDs must be unique.")
        
        # Validate resource allocations
        if not isinstance(allocated_cpu, int) or not isinstance(allocated_storage, int):
            raise TypeError("Resource allocations must be integers.")
        
        if allocated_cpu <= 0 or allocated_storage <= 0:
            raise ValueError("Resource allocations must be positive integers.")
        
        # Store node identity
        self.node_id = node_id
        Node._all_node_ids.add(node_id)
        
        # Store resource allocations
        self.allocated_cpu = allocated_cpu
        self.allocated_storage = allocated_storage
        
        # Initialize resource usage at zero
        self.used_cpu = 0
        self.used_storage = 0
        
        # Set initial status to active
        self.status = "active"
        
        # Record creation time for audit purposes
        self.created_at = datetime.now()
    
    def request_cpu(self, amount: int) -> bool:
        
        # Validate request
        if not isinstance(amount, int) or amount <= 0:
            return False
        
        # Check if request exceeds available resources
        if self.used_cpu + amount > self.allocated_cpu:
            return False
        
        # Grant the request
        self.used_cpu += amount
        return True
    
    def release_cpu(self, amount: int) -> bool:
        
        # Validate release amount
        if not isinstance(amount, int) or amount <= 0:
            return False
        
        # Prevent over-releasing
        if amount > self.used_cpu:
            return False
        
        # Release the resources
        self.used_cpu -= amount
        return True
    
    def request_storage(self, amount: int) -> bool:
        
        # Validate request
        if not isinstance(amount, int) or amount <= 0:
            return False
        
        # Check if request exceeds available resources
        if self.used_storage + amount > self.allocated_storage:
            return False
        
        # Grant the request
        self.used_storage += amount
        return True
    
    def release_storage(self, amount: int) -> bool:
        
        # Validate release amount
        if not isinstance(amount, int) or amount <= 0:
            return False
        
        # Prevent over-releasing
        if amount > self.used_storage:
            return False
        
        # Release the resources
        self.used_storage -= amount
        return True
    
    def get_available_cpu(self) -> int:
        
        return self.allocated_cpu - self.used_cpu
    
    def get_available_storage(self) -> int:
        
        return self.allocated_storage - self.used_storage
    
    def set_status(self, new_status: str) -> bool:
        
        # Validate status
        valid_statuses = ["active", "inactive"]
        if new_status not in valid_statuses:
            return False
        
        self.status = new_status
        return True
    
    def is_active(self) -> bool:
       
        return self.status == "active"
    
    def validate(self) -> bool:
        
        # Check resource constraints
        if self.used_cpu < 0 or self.used_cpu > self.allocated_cpu:
            return False
        
        if self.used_storage < 0 or self.used_storage > self.allocated_storage:
            return False
        
        # Check status is valid
        if self.status not in ["active", "inactive"]:
            return False
        
        # Check node ID exists
        if not self.node_id or not isinstance(self.node_id, str):
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
    
        return {
            "node_id": self.node_id,
            "allocated_cpu": self.allocated_cpu,
            "allocated_storage": self.allocated_storage,
            "used_cpu": self.used_cpu,
            "used_storage": self.used_storage,
            "available_cpu": self.get_available_cpu(),
            "available_storage": self.get_available_storage(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Node':
        
        # Validate required keys exist
        required_keys = {
            "node_id",
            "allocated_cpu",
            "allocated_storage",
            "used_cpu",
            "used_storage",
            "status"
        }
        
        if not all(key in data for key in required_keys):
            missing = required_keys - set(data.keys())
            raise ValueError(f"Missing required keys: {missing}")
        
        # Create node with basic info
        node = Node(
            node_id=data["node_id"],
            allocated_cpu=data["allocated_cpu"],
            allocated_storage=data["allocated_storage"]
        )
        
        # Restore resource usage and status
        node.used_cpu = data["used_cpu"]
        node.used_storage = data["used_storage"]
        node.status = data["status"]
        
        return node
    
    def __str__(self) -> str:
        
        return (
            f"Node(id={self.node_id}, status={self.status}, "
            f"CPU={self.used_cpu}/{self.allocated_cpu}, "
            f"Storage={self.used_storage}/{self.allocated_storage})"
        )
    
    def __repr__(self) -> str:
        
        return self.__str__()
    
    def __hash__(self) -> int:
        
        return hash(self.node_id)
    
    def __eq__(self, other) -> bool:
        
        if not isinstance(other, Node):
            return False
        return self.node_id == other.node_id

# ============================================================================
# EXAMPLE USAGE (for testing and learning)
# ============================================================================

if __name__ == "__main__":
    
    print("=== Node Management Module Demo ===\n")
    
    # Create some nodes
    print("1. Creating nodes...")
    node1 = Node("NODE_ALPHA", allocated_cpu=100, allocated_storage=1024)
    node2 = Node("NODE_BETA", allocated_cpu=50, allocated_storage=512)
    node3 = Node()  # Auto-generated ID
    
    print(f"   {node1}")
    print(f"   {node2}")
    print(f"   {node3}\n")
    
    # Test resource requests
    print("2. Requesting resources...")
    print(f"   NODE_ALPHA requests 30 CPU: {node1.request_cpu(30)}")
    print(f"   Available CPU: {node1.get_available_cpu()}")
    print(f"   NODE_ALPHA requests 50 storage: {node1.request_storage(50)}")
    print(f"   Available Storage: {node1.get_available_storage()}\n")
    
    # Test over-allocation prevention
    print("3. Testing resource limits...")
    print(f"   NODE_ALPHA requests 80 CPU (exceeds limit): {node1.request_cpu(80)}")
    print(f"   (Request denied - would exceed 100 CPU limit)\n")
    
    # Test resource release
    print("4. Releasing resources...")
    print(f"   NODE_ALPHA releases 30 CPU: {node1.release_cpu(30)}")
    print(f"   Available CPU: {node1.get_available_cpu()}\n")
    
    # Test validation
    print("5. Validating node state...")
    print(f"   NODE_ALPHA valid: {node1.validate()}")
    print(f"   NODE_BETA valid: {node2.validate()}\n")
    
    # Test serialization
    print("6. Serializing to dictionary...")
    node1_dict = node1.to_dict()
    print(f"   {node1_dict}\n")
    
    # Test deserialization
    print("7. Deserializing from dictionary...")
    reconstructed = Node.from_dict(node1_dict)
    print(f"   {reconstructed}\n")
    
    print("=== Demo Complete ===")