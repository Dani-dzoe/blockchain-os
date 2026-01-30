"""
Basic integration tests for validating system flow.

These tests verify that the main components work together correctly.
"""

from cli.cli import IntegratedCLI


def test_basic_node_creation():
    """Test that we can create a node and it's registered."""
    cli = IntegratedCLI(difficulty=1)
    result = cli.add_node('test_node', {'CPU': 4.0, 'Memory': 8.0})
    assert 'test_node' in result
    assert 'test_node' in cli.resource_manager.nodes


def test_end_to_end_allocation_flow():
    """Test complete flow: create nodes, allocate, validate chain."""
    cli = IntegratedCLI(difficulty=1)

    # Create nodes
    cli.add_node('node1', {'CPU': 4.0})
    cli.add_node('node2', {'CPU': 4.0})

    # Request resource (triggers consensus and blockchain update)
    result = cli.request_resource('node1', 'CPU', 2.0)
    assert 'block' in result.lower()

    # Verify blockchain is valid
    is_valid, reason = cli.validate_chain()
    assert is_valid

    # Verify allocation was applied
    node1 = cli.resource_manager.nodes['node1']
    assert node1.allocated['CPU'] == 2.0
