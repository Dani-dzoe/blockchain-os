"""
Consensus Module for Blockchain-Based Distributed Operating System

This module implements a simple majority-voting consensus mechanism.
In a distributed system, nodes must agree on which blocks to add to the blockchain.
This prevents conflicts and ensures all nodes have a consistent view of the system state.

CONSENSUS RULE:
A block is accepted if and only if a MAJORITY of nodes vote to approve it.
Majority means: votes_for > total_nodes / 2

This is a SIMULATION - no real networking occurs.
All nodes and their votes are simulated in Python.
"""


class ConsensusEngine:
    """
    Manages the consensus process for block approval.
    
    In a real distributed system, this would involve network communication.
    Here, we simulate multiple nodes voting on a proposed block.
    
    Attributes:
        nodes (list): List of node identifiers participating in consensus
        vote_threshold (float): Percentage needed for approval (default 0.5 for majority)
    """
    
    def __init__(self, nodes, vote_threshold=0.5):
        """
        Initialize the consensus engine.
        
        Args:
            nodes (list): List of node objects or node IDs that can vote
            vote_threshold (float): Fraction of votes needed (0.5 = majority, 0.66 = supermajority)
        
        Raises:
            ValueError: If nodes list is empty or threshold is invalid
        """
        if not nodes:
            raise ValueError("Consensus requires at least one node")
        
        if vote_threshold <= 0 or vote_threshold > 1:
            raise ValueError("Vote threshold must be between 0 and 1")
        
        self.nodes = nodes
        self.vote_threshold = vote_threshold
        
        print(f"\n[CONSENSUS ENGINE INITIALIZED]")
        print(f"  Total Nodes: {len(self.nodes)}")
        print(f"  Vote Threshold: {vote_threshold * 100}%")
        print(f"  Votes Required: {self._calculate_required_votes()} of {len(self.nodes)}")
    
    
    def _calculate_required_votes(self):
        """
        Calculate the minimum number of votes needed for consensus.
        
        For majority: requires MORE than half (not equal to half)
        Example: 5 nodes need 3 votes, 4 nodes need 3 votes, 3 nodes need 2 votes
        
        Returns:
            int: Minimum number of approving votes required
        """
        total_nodes = len(self.nodes)
        # Use ceiling division to ensure strict majority
        required = int(total_nodes * self.vote_threshold) + 1
        
        # Ensure we don't require more votes than nodes available
        return min(required, total_nodes)
    
    
    def request_consensus(self, block, validator_func=None):
        """
        Request consensus from all nodes on a proposed block.
        
        This is the main consensus method. It simulates asking each node
        whether they approve the proposed block, counts the votes,
        and determines if consensus is reached.
        
        Args:
            block: The block object to validate and vote on
            validator_func: Optional function to validate block before voting
                           Should return (bool, str) - (is_valid, reason)
        
        Returns:
            tuple: (bool, dict) - (consensus_reached, voting_details)
                   voting_details contains votes_for, votes_against, abstentions
        
        Raises:
            ValueError: If block is None
        """
        if block is None:
            raise ValueError("Cannot request consensus on None block")
        
        print(f"\n{'='*70}")
        print(f"[CONSENSUS REQUEST INITIATED]")
        print(f"  Block Index: {getattr(block, 'index', 'N/A')}")
        print(f"  Block Hash: {getattr(block, 'hash', 'N/A')[:16]}...")
        print(f"  Transactions: {len(getattr(block, 'transactions', []))}")
        print(f"{'='*70}")
        
        # Step 1: Pre-validation (optional)
        if validator_func:
            print("\n[STEP 1: PRE-VALIDATION]")
            is_valid, reason = validator_func(block)
            if not is_valid:
                print(f"  ✗ Block failed pre-validation: {reason}")
                return False, {
                    'votes_for': 0,
                    'votes_against': len(self.nodes),
                    'abstentions': 0,
                    'reason': f'Pre-validation failed: {reason}'
                }
            print(f"  ✓ Block passed pre-validation")
        
        # Step 2: Simulate voting from each node
        print("\n[STEP 2: COLLECTING VOTES]")
        votes_for = 0
        votes_against = 0
        abstentions = 0
        voting_record = []
        
        for i, node in enumerate(self.nodes, 1):
            # Simulate each node's vote
            # In a real system, this would be a network call to each node
            vote = self._simulate_node_vote(node, block)
            
            if vote == "APPROVE":
                votes_for += 1
                symbol = "✓"
            elif vote == "REJECT":
                votes_against += 1
                symbol = "✗"
            else:  # ABSTAIN
                abstentions += 1
                symbol = "○"
            
            # Get node identifier for display
            node_id = getattr(node, 'node_id', f'Node_{i}')
            print(f"  {symbol} {node_id}: {vote}")
            
            voting_record.append({
                'node': node_id,
                'vote': vote
            })
        
        # Step 3: Count votes and determine consensus
        print(f"\n[STEP 3: VOTE COUNTING]")
        print(f"  Votes FOR:     {votes_for}")
        print(f"  Votes AGAINST: {votes_against}")
        print(f"  Abstentions:   {abstentions}")
        print(f"  Total Votes:   {len(self.nodes)}")
        
        required_votes = self._calculate_required_votes()
        print(f"\n[STEP 4: CONSENSUS DECISION]")
        print(f"  Required for Approval: {required_votes}")
        print(f"  Received:              {votes_for}")
        
        # Consensus is reached if votes_for meets or exceeds required threshold
        consensus_reached = votes_for >= required_votes
        
        if consensus_reached:
            print(f"  ✓ CONSENSUS REACHED - Block ACCEPTED")
        else:
            print(f"  ✗ CONSENSUS FAILED - Block REJECTED")
        
        print(f"{'='*70}\n")
        
        # Return detailed results
        return consensus_reached, {
            'votes_for': votes_for,
            'votes_against': votes_against,
            'abstentions': abstentions,
            'required_votes': required_votes,
            'total_nodes': len(self.nodes),
            'voting_record': voting_record,
            'consensus_reached': consensus_reached
        }
    
    
    def _simulate_node_vote(self, node, block):
        """
        Simulate a single node's vote on a block.
        
        In a real distributed system, this would:
        1. Send the block to the node over the network
        2. Wait for the node to validate and respond
        3. Receive the vote
        
        Here, we simulate the node's decision-making process.
        
        Args:
            node: The node object voting
            block: The block being voted on
        
        Returns:
            str: "APPROVE", "REJECT", or "ABSTAIN"
        """
        # Check if node has a custom voting method
        if hasattr(node, 'vote_on_block'):
            # Let the node decide based on its own logic
            return node.vote_on_block(block)
        
        # Default voting logic: approve if block appears valid
        # In a simple simulation, we can check basic properties
        
        # Check if block has required attributes
        if not hasattr(block, 'transactions'):
            return "REJECT"
        
        if not hasattr(block, 'previous_hash'):
            return "REJECT"
        
        # Check if block is properly formed
        if getattr(block, 'index', -1) < 0:
            return "REJECT"
        
        # Check if transactions list exists (can be empty for genesis block)
        if not isinstance(getattr(block, 'transactions', None), list):
            return "REJECT"
        
        # Default: approve well-formed blocks
        return "APPROVE"
    
    
    def update_nodes(self, new_nodes):
        """
        Update the list of participating nodes.
        
        This allows the consensus group to change over time as nodes
        join or leave the network.
        
        Args:
            new_nodes (list): Updated list of nodes
        
        Raises:
            ValueError: If new_nodes is empty
        """
        if not new_nodes:
            raise ValueError("Cannot update to empty node list")
        
        old_count = len(self.nodes)
        self.nodes = new_nodes
        new_count = len(self.nodes)
        
        print(f"\n[CONSENSUS ENGINE UPDATED]")
        print(f"  Previous Node Count: {old_count}")
        print(f"  New Node Count: {new_count}")
        print(f"  New Required Votes: {self._calculate_required_votes()} of {new_count}")
    
    
    def get_consensus_info(self):
        """
        Get current consensus configuration information.
        
        Returns:
            dict: Current consensus settings and statistics
        """
        return {
            'total_nodes': len(self.nodes),
            'vote_threshold': self.vote_threshold,
            'required_votes': self._calculate_required_votes(),
            'consensus_type': 'Majority Vote' if self.vote_threshold == 0.5 else 'Custom Threshold'
        }


def validate_block_structure(block):
    """
    Example validator function for block structure.
    
    This is a helper function that can be passed to request_consensus()
    to perform pre-validation before voting begins.
    
    Args:
        block: The block to validate
    
    Returns:
        tuple: (is_valid, reason)
    """
    # Check required attributes
    required_attrs = ['index', 'timestamp', 'transactions', 'previous_hash', 'hash']
    
    for attr in required_attrs:
        if not hasattr(block, attr):
            return False, f"Missing required attribute: {attr}"
    
    # Check index is non-negative
    if block.index < 0:
        return False, "Block index cannot be negative"
    
    # Check transactions is a list
    if not isinstance(block.transactions, list):
        return False, "Transactions must be a list"
    
    # Check hash is not empty
    if not block.hash:
        return False, "Block hash cannot be empty"
    
    return True, "Block structure is valid"


# Example usage demonstration
if __name__ == "__main__":
    """
    Demonstration of the consensus module.
    This shows how the module would be used in the larger system.
    """
    
    print("="*70)
    print("CONSENSUS MODULE DEMONSTRATION")
    print("="*70)
    
    # Create mock node objects for testing
    class MockNode:
        def __init__(self, node_id, behavior="honest"):
            self.node_id = node_id
            self.behavior = behavior
        
        def vote_on_block(self, block):
            """Simulate different node behaviors"""
            if self.behavior == "honest":
                return "APPROVE"
            elif self.behavior == "malicious":
                return "REJECT"
            else:
                return "ABSTAIN"
    
    # Create mock block for testing
    class MockBlock:
        def __init__(self, index, transactions):
            self.index = index
            self.timestamp = "2026-01-29 12:00:00"
            self.transactions = transactions
            self.previous_hash = "0" * 64
            self.hash = "a" * 64
    
    # Scenario 1: Consensus with majority approval
    print("\n" + "="*70)
    print("SCENARIO 1: Consensus Reached (3 of 5 approve)")
    print("="*70)
    
    nodes_scenario1 = [
        MockNode("Node_A", "honest"),
        MockNode("Node_B", "honest"),
        MockNode("Node_C", "honest"),
        MockNode("Node_D", "malicious"),
        MockNode("Node_E", "malicious")
    ]
    
    consensus1 = ConsensusEngine(nodes_scenario1)
    test_block1 = MockBlock(index=1, transactions=["tx1", "tx2"])
    
    result1, details1 = consensus1.request_consensus(test_block1, validate_block_structure)
    
    # Scenario 2: Consensus fails (minority approval)
    print("\n" + "="*70)
    print("SCENARIO 2: Consensus Failed (2 of 5 approve)")
    print("="*70)
    
    nodes_scenario2 = [
        MockNode("Node_A", "honest"),
        MockNode("Node_B", "honest"),
        MockNode("Node_C", "malicious"),
        MockNode("Node_D", "malicious"),
        MockNode("Node_E", "malicious")
    ]
    
    consensus2 = ConsensusEngine(nodes_scenario2)
    test_block2 = MockBlock(index=2, transactions=["tx3", "tx4"])
    
    result2, details2 = consensus2.request_consensus(test_block2, validate_block_structure)
    
    # Scenario 3: Small network (3 nodes)
    print("\n" + "="*70)
    print("SCENARIO 3: Small Network (2 of 3 approve)")
    print("="*70)
    
    nodes_scenario3 = [
        MockNode("Node_X", "honest"),
        MockNode("Node_Y", "honest"),
        MockNode("Node_Z", "malicious")
    ]
    
    consensus3 = ConsensusEngine(nodes_scenario3)
    test_block3 = MockBlock(index=3, transactions=["tx5"])
    
    result3, details3 = consensus3.request_consensus(test_block3, validate_block_structure)
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)