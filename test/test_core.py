from core.blockchain import Blockchain
from core.blockchain import Block
from core.transaction import Transaction
from consensus.consensus import ConsensusEngine
from resources.resource_manager import ResourceManager
from core.node import Node


def test_blockchain_tamper_detection():
    bc = Blockchain(difficulty=1)
    tx = Transaction(node_id='n1', resource_type='CPU', amount=1, transaction_type='allocate')
    bc.create_block([tx.to_dict()])
    ok, _ = bc.is_chain_valid()
    assert ok

    # Tamper with a transaction in block 1 and expect validation to fail
    bc.chain[1].transactions[0]['amount'] = 9999
    ok, reason = bc.is_chain_valid()
    assert not ok


def test_consensus_majority_accept():
    class MockNode:
        def __init__(self, node_id, behavior='honest'):
            self.node_id = node_id
            self.behavior = behavior
        def vote_on_block(self, block):
            return 'APPROVE' if self.behavior == 'honest' else 'REJECT'

    nodes = [MockNode('a','honest'), MockNode('b','honest'), MockNode('c','malicious')]
    ce = ConsensusEngine(nodes)
    block = Block(index=1, timestamp=0.0, transactions=[], previous_hash='0')
    result, details = ce.request_consensus(block)
    assert result
    assert details['votes_for'] >= details['required_votes']


def test_resource_manager_allocation_and_release():
    rm = ResourceManager()
    node = Node(node_id='n1', quotas={'CPU': 4})
    rm.register_node(node)
    assert rm.can_allocate('n1', 'CPU', 2)
    rm.apply_allocation('n1', 'CPU', 2)
    assert not rm.can_allocate('n1', 'CPU', 3)
    assert node.allocated['CPU'] == 2
    rm.apply_release('n1', 'CPU', 1)
    assert node.allocated['CPU'] == 1
