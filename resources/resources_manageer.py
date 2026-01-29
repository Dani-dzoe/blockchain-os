"""
Resource Management Module for Blockchain-Based Distributed Operating System

This module manages system resources (CPU and Storage) across distributed nodes.
It enforces allocation rules and ensures nodes cannot exceed their limits.

KEY CONCEPTS:
- Each node has a fixed pool of CPU units and Storage units
- Transactions represent resource requests (allocate or release)
- Resources are updated ONLY after consensus approves the block
- Invalid requests are rejected with clear error messages

RESOURCE RULES:
1. Nodes cannot exceed their allocated CPU or storage limits
2. Nodes cannot have negative resources (can't release more than they have)
3. Invalid requests must be rejected before applying
4. All operations are logged for audit purposes
"""


class ResourceManager:
    """
    Manages resource allocation and tracking for all nodes in the system.
    
    This class acts as the central authority for resource management,
    similar to a kernel's resource scheduler in a traditional OS.
    
    Attributes:
        node_resources (dict): Maps node_id -> {cpu, storage, cpu_limit, storage_limit}
        default_cpu_limit (int): Default CPU units per node
        default_storage_limit (int): Default storage (MB) per node
        transaction_history (list): Log of all resource operations
    """
    
    def __init__(self, default_cpu_limit=100, default_storage_limit=100):
        """
        Initialize the Resource Manager.
        
        Args:
            default_cpu_limit (int): Default CPU units allocated to each node
            default_storage_limit (int): Default storage in MB allocated to each node
        """
        self.default_cpu_limit = default_cpu_limit
        self.default_storage_limit = default_storage_limit
        
        # Track resources for each node
        # Format: {node_id: {'cpu': available, 'storage': available, 
        #                     'cpu_limit': max, 'storage_limit': max}}
        self.node_resources = {}
        
        # Keep history of all resource operations for audit
        self.transaction_history = []
        
        print(f"\n[RESOURCE MANAGER INITIALIZED]")
        print(f"  Default CPU Limit per Node: {default_cpu_limit} units")
        print(f"  Default Storage Limit per Node: {default_storage_limit} MB")
    
    
    def register_node(self, node_id, cpu_limit=None, storage_limit=None):
        """
        Register a new node with the resource manager.
        
        When a node joins the system, it gets allocated its resource pool.
        Custom limits can be set per node, or defaults will be used.
        
        Args:
            node_id (str): Unique identifier for the node
            cpu_limit (int, optional): Custom CPU limit for this node
            storage_limit (int, optional): Custom storage limit for this node
        
        Raises:
            ValueError: If node is already registered
        """
        if node_id in self.node_resources:
            raise ValueError(f"Node '{node_id}' is already registered")
        
        # Use custom limits or defaults
        cpu = cpu_limit if cpu_limit is not None else self.default_cpu_limit
        storage = storage_limit if storage_limit is not None else self.default_storage_limit
        
        # Initially, all resources are available (none allocated)
        self.node_resources[node_id] = {
            'cpu': cpu,           # Currently available CPU
            'storage': storage,   # Currently available storage
            'cpu_limit': cpu,     # Maximum CPU capacity
            'storage_limit': storage  # Maximum storage capacity
        }
        
        print(f"\n[NODE REGISTERED]")
        print(f"  Node ID: {node_id}")
        print(f"  CPU Limit: {cpu} units")
        print(f"  Storage Limit: {storage} MB")
    
    
    def get_node_resources(self, node_id):
        """
        Get current resource status for a specific node.
        
        Args:
            node_id (str): The node to query
        
        Returns:
            dict: Resource information or None if node not found
        """
        if node_id not in self.node_resources:
            return None
        
        return self.node_resources[node_id].copy()
    
    
    def display_all_resources(self):
        """
        Display resource status for all registered nodes.
        
        This provides a system-wide view of resource utilization,
        useful for monitoring and debugging.
        """
        print(f"\n{'='*80}")
        print(f"[SYSTEM RESOURCE STATUS]")
        print(f"{'='*80}")
        
        if not self.node_resources:
            print("  No nodes registered")
            print(f"{'='*80}\n")
            return
        
        for node_id, resources in self.node_resources.items():
            cpu_used = resources['cpu_limit'] - resources['cpu']
            storage_used = resources['storage_limit'] - resources['storage']
            
            cpu_percent = (cpu_used / resources['cpu_limit']) * 100
            storage_percent = (storage_used / resources['storage_limit']) * 100
            
            print(f"\n  Node: {node_id}")
            print(f"    CPU:     {cpu_used}/{resources['cpu_limit']} units " +
                  f"({cpu_percent:.1f}% used, {resources['cpu']} available)")
            print(f"    Storage: {storage_used}/{resources['storage_limit']} MB " +
                  f"({storage_percent:.1f}% used, {resources['storage']} available)")
        
        print(f"\n{'='*80}\n")
    
    
    def apply_block_transactions(self, block):
        """
        Apply all resource transactions in a consensus-approved block.
        
        THIS IS THE CRITICAL METHOD - Resources are updated ONLY after consensus.
        
        Process:
        1. Extract transactions from the block
        2. Validate each transaction
        3. Apply valid transactions
        4. Reject invalid transactions with clear errors
        5. Log all operations
        
        Args:
            block: The consensus-approved block containing transactions
        
        Returns:
            dict: Summary of applied and rejected transactions
        """
        print(f"\n{'='*80}")
        print(f"[APPLYING BLOCK TRANSACTIONS]")
        print(f"  Block Index: {getattr(block, 'index', 'N/A')}")
        print(f"  Total Transactions: {len(getattr(block, 'transactions', []))}")
        print(f"{'='*80}")
        
        # Get transactions from block
        transactions = getattr(block, 'transactions', [])
        
        if not transactions:
            print("  No transactions to process")
            print(f"{'='*80}\n")
            return {'applied': 0, 'rejected': 0, 'details': []}
        
        applied_count = 0
        rejected_count = 0
        details = []
        
        # Process each transaction
        for idx, transaction in enumerate(transactions, 1):
            print(f"\n[Transaction {idx}/{len(transactions)}]")
            
            # Apply the transaction and get result
            success, message = self._apply_single_transaction(transaction)
            
            if success:
                applied_count += 1
                print(f"  ✓ SUCCESS: {message}")
            else:
                rejected_count += 1
                print(f"  ✗ REJECTED: {message}")
            
            details.append({
                'transaction': transaction,
                'success': success,
                'message': message
            })
        
        # Display summary
        print(f"\n{'='*80}")
        print(f"[TRANSACTION SUMMARY]")
        print(f"  Applied:  {applied_count}")
        print(f"  Rejected: {rejected_count}")
        print(f"  Total:    {len(transactions)}")
        print(f"{'='*80}\n")
        
        return {
            'applied': applied_count,
            'rejected': rejected_count,
            'details': details
        }
    
    
    def _apply_single_transaction(self, transaction):
        """
        Apply a single resource transaction.
        
        This method validates and executes one resource request.
        
        Args:
            transaction: Transaction object or dict with resource request
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Extract transaction details
        # Support both object attributes and dict keys
        node_id = getattr(transaction, 'node_id', transaction.get('node_id'))
        operation = getattr(transaction, 'operation', transaction.get('operation'))
        resource_type = getattr(transaction, 'resource_type', transaction.get('resource_type'))
        amount = getattr(transaction, 'amount', transaction.get('amount'))
        
        # Validate transaction has all required fields
        if not all([node_id, operation, resource_type, amount]):
            return False, "Missing required transaction fields"
        
        # Validate node exists
        if node_id not in self.node_resources:
            return False, f"Node '{node_id}' not registered"
        
        # Validate resource type
        if resource_type not in ['cpu', 'storage']:
            return False, f"Invalid resource type '{resource_type}' (must be 'cpu' or 'storage')"
        
        # Validate amount is positive
        if amount <= 0:
            return False, f"Amount must be positive (got {amount})"
        
        # Validate operation type
        if operation not in ['allocate', 'release']:
            return False, f"Invalid operation '{operation}' (must be 'allocate' or 'release')"
        
        # Get current resource state
        node_resources = self.node_resources[node_id]
        current_available = node_resources[resource_type]
        limit = node_resources[f'{resource_type}_limit']
        
        # Process based on operation type
        if operation == 'allocate':
            return self._allocate_resource(node_id, resource_type, amount, 
                                          current_available, limit)
        else:  # release
            return self._release_resource(node_id, resource_type, amount, 
                                         current_available, limit)
    
    
    def _allocate_resource(self, node_id, resource_type, amount, current_available, limit):
        """
        Allocate (consume) resources from a node's pool.
        
        Allocation reduces available resources.
        Example: Allocating 10 CPU units means 10 fewer units are available.
        
        Args:
            node_id (str): Node requesting allocation
            resource_type (str): 'cpu' or 'storage'
            amount (int): Amount to allocate
            current_available (int): Currently available amount
            limit (int): Maximum capacity
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Check if enough resources are available
        if amount > current_available:
            return False, (f"Insufficient {resource_type}: requested {amount}, " +
                          f"but only {current_available} available")
        
        # Allocate the resources (reduce available amount)
        new_available = current_available - amount
        self.node_resources[node_id][resource_type] = new_available
        
        # Calculate usage for display
        used = limit - new_available
        usage_percent = (used / limit) * 100
        
        # Log the operation
        self.transaction_history.append({
            'node_id': node_id,
            'operation': 'allocate',
            'resource_type': resource_type,
            'amount': amount,
            'new_available': new_available,
            'timestamp': self._get_timestamp()
        })
        
        return True, (f"Allocated {amount} {resource_type} units to {node_id} | " +
                     f"Available: {new_available}/{limit} ({usage_percent:.1f}% used)")
    
    
    def _release_resource(self, node_id, resource_type, amount, current_available, limit):
        """
        Release (free) resources back to a node's pool.
        
        Release increases available resources.
        Example: Releasing 10 CPU units makes 10 more units available.
        
        Args:
            node_id (str): Node releasing resources
            resource_type (str): 'cpu' or 'storage'
            amount (int): Amount to release
            current_available (int): Currently available amount
            limit (int): Maximum capacity
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Calculate new available amount
        new_available = current_available + amount
        
        # Check if release would exceed the limit (can't release more than was allocated)
        if new_available > limit:
            exceeds_by = new_available - limit
            return False, (f"Cannot release {amount} {resource_type} units: " +
                          f"would exceed limit by {exceeds_by} " +
                          f"(current: {current_available}, limit: {limit})")
        
        # Release the resources (increase available amount)
        self.node_resources[node_id][resource_type] = new_available
        
        # Calculate usage for display
        used = limit - new_available
        usage_percent = (used / limit) * 100 if limit > 0 else 0
        
        # Log the operation
        self.transaction_history.append({
            'node_id': node_id,
            'operation': 'release',
            'resource_type': resource_type,
            'amount': amount,
            'new_available': new_available,
            'timestamp': self._get_timestamp()
        })
        
        return True, (f"Released {amount} {resource_type} units from {node_id} | " +
                     f"Available: {new_available}/{limit} ({usage_percent:.1f}% used)")
    
    
    def _get_timestamp(self):
        """
        Get current timestamp for logging.
        
        Returns:
            str: Current timestamp
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    
    def get_transaction_history(self, node_id=None, limit=None):
        """
        Retrieve transaction history for audit purposes.
        
        Args:
            node_id (str, optional): Filter by specific node
            limit (int, optional): Limit number of results
        
        Returns:
            list: Transaction history records
        """
        history = self.transaction_history
        
        # Filter by node if specified
        if node_id:
            history = [h for h in history if h['node_id'] == node_id]
        
        # Limit results if specified
        if limit:
            history = history[-limit:]
        
        return history
    
    
    def display_transaction_history(self, node_id=None, limit=10):
        """
        Display recent transaction history.
        
        Args:
            node_id (str, optional): Filter by specific node
            limit (int): Number of recent transactions to show
        """
        history = self.get_transaction_history(node_id, limit)
        
        print(f"\n{'='*80}")
        print(f"[TRANSACTION HISTORY]")
        if node_id:
            print(f"  Filtered by Node: {node_id}")
        print(f"  Showing last {min(len(history), limit)} transactions")
        print(f"{'='*80}")
        
        if not history:
            print("  No transactions recorded")
        else:
            for i, record in enumerate(history, 1):
                print(f"\n  [{i}] {record['timestamp']}")
                print(f"      Node: {record['node_id']}")
                print(f"      Operation: {record['operation'].upper()}")
                print(f"      Resource: {record['resource_type']}")
                print(f"      Amount: {record['amount']}")
                print(f"      New Available: {record['new_available']}")
        
        print(f"\n{'='*80}\n")
    
    
    def reset_node_resources(self, node_id):
        """
        Reset a node's resources to initial state (all available).
        
        Useful for testing or when a node needs to be reinitialized.
        
        Args:
            node_id (str): Node to reset
        
        Raises:
            ValueError: If node not found
        """
        if node_id not in self.node_resources:
            raise ValueError(f"Node '{node_id}' not found")
        
        node = self.node_resources[node_id]
        node['cpu'] = node['cpu_limit']
        node['storage'] = node['storage_limit']
        
        print(f"\n[NODE RESOURCES RESET]")
        print(f"  Node: {node_id}")
        print(f"  CPU: {node['cpu']}/{node['cpu_limit']}")
        print(f"  Storage: {node['storage']}/{node['storage_limit']}")


# Example usage demonstration
if __name__ == "__main__":
    """
    Demonstration of the Resource Management module.
    Shows how it integrates with the blockchain system.
    """
    
    print("="*80)
    print("RESOURCE MANAGEMENT MODULE DEMONSTRATION")
    print("="*80)
    
    # Initialize the resource manager
    rm = ResourceManager(default_cpu_limit=100, default_storage_limit=100)
    
    # Register some nodes
    print("\n" + "="*80)
    print("STEP 1: Register Nodes")
    print("="*80)
    rm.register_node("Node_A")
    rm.register_node("Node_B", cpu_limit=150, storage_limit=200)  # Custom limits
    rm.register_node("Node_C")
    
    # Display initial state
    rm.display_all_resources()
    
    # Create mock transactions
    class MockTransaction:
        def __init__(self, node_id, operation, resource_type, amount):
            self.node_id = node_id
            self.operation = operation
            self.resource_type = resource_type
            self.amount = amount
    
    # Create a mock block with transactions
    class MockBlock:
        def __init__(self, index, transactions):
            self.index = index
            self.transactions = transactions
    
    # Scenario 1: Valid allocations
    print("\n" + "="*80)
    print("SCENARIO 1: Valid Resource Allocations")
    print("="*80)
    
    block1 = MockBlock(1, [
        MockTransaction("Node_A", "allocate", "cpu", 30),
        MockTransaction("Node_A", "allocate", "storage", 50),
        MockTransaction("Node_B", "allocate", "cpu", 75),
    ])
    
    rm.apply_block_transactions(block1)
    rm.display_all_resources()
    
    # Scenario 2: Valid releases
    print("\n" + "="*80)
    print("SCENARIO 2: Valid Resource Releases")
    print("="*80)
    
    block2 = MockBlock(2, [
        MockTransaction("Node_A", "release", "cpu", 10),
        MockTransaction("Node_B", "release", "cpu", 25),
    ])
    
    rm.apply_block_transactions(block2)
    rm.display_all_resources()
    
    # Scenario 3: Invalid requests (exceeding limits)
    print("\n" + "="*80)
    print("SCENARIO 3: Invalid Requests (Should be Rejected)")
    print("="*80)
    
    block3 = MockBlock(3, [
        MockTransaction("Node_A", "allocate", "cpu", 200),  # Exceeds limit
        MockTransaction("Node_C", "release", "storage", 150),  # Can't release more than allocated
        MockTransaction("Node_A", "allocate", "storage", 60),  # Valid request
    ])
    
    rm.apply_block_transactions(block3)
    rm.display_all_resources()
    
    # Display transaction history
    rm.display_transaction_history(limit=15)
    
    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)