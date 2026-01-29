
"""
Defines transactions representing operating system actions.
"""

class Transaction:
    def __init__(self, node_id, resource_type, amount, transaction_type):
        self.node_id = node_id
        self.resource_type = resource_type
        self.amount = amount
        self.transaction_type = transaction_type

# Validate and store inputs
        if not node_id:
            raise ValueError("node_id cannot be empty")
        self.node_id = node_id

        allowed_resources = ["CPU", "Memory", "Storage", "Bandwidth"]
        if resource_type not in allowed_resources:
            raise ValueError(f"resource_type must be one of {allowed_resources}")
        self.resource_type = resource_type

        if amount <= 0:
            raise ValueError("amount must be greater than zero")
        self.amount = amount

        allowed_types = ["allocate", "release", "transfer"]
        if transaction_type not in allowed_types:
            raise ValueError(f"transaction_type must be one of {allowed_types}")
        self.transaction_type = transaction_type

    def to_dict(self):
        """Return transaction details as a dictionary."""
        return {
            "node_id": self.node_id,
            "resource_type": self.resource_type,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "transaction_type": self.transaction_type
        }

    def __str__(self):
        """Readable string version of the transaction."""
        return f"{self.transaction_type} {self.amount} {self.resource_type} by {self.node_id} at {self.timestamp}"