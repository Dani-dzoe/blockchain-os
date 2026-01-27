"""
Defines transactions representing operating system actions.
"""

class Transaction:
    def __init__(self, node_id, resource_type, amount, transaction_type):
        self.node_id = node_id
        self.resource_type = resource_type
        self.amount = amount
        self.transaction_type = transaction_type
