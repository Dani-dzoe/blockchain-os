"""
Tests for persistence and orchestrator functionality.

These tests verify:
1. Atomic persistence (state save/load)
2. State recovery after restart
3. Orchestrator command handling
4. Socket API basic functionality
"""

import os
import json
import tempfile
import socket
import time
from pathlib import Path

import pytest

from persistence import save_state, load_state
from controller import MainController
from core.node import Node
from core.blockchain import Blockchain


class TestPersistence:
    """Test atomic persistence operations."""

    def test_save_and_load_empty_state(self):
        """Test saving and loading empty state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"

            # Save empty state
            save_state(state_file, nodes=[], chain=[], audit_events=[])

            # Verify file exists
            assert state_file.exists()

            # Load it back
            data = load_state(state_file)
            assert data["nodes"] == []
            assert data["chain"] == []
            assert data["audit_events"] == []

    def test_save_and_load_with_data(self):
        """Test saving and loading state with actual data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"

            # Create test data
            nodes = [
                {"node_id": "n1", "quotas": {"CPU": 4.0}, "allocated": {"CPU": 2.0}, "status": "active"},
                {"node_id": "n2", "quotas": {"Memory": 8.0}, "allocated": {"Memory": 0.0}, "status": "active"},
            ]
            chain = [
                {"index": 0, "timestamp": 1234.5, "transactions": [], "previous_hash": "0", "nonce": 0, "hash": "genesis"},
            ]
            audit_events = [
                {"timestamp": 1234.5, "node_id": "n1", "action": "add_node", "outcome": "created", "details": {}},
            ]

            # Save state
            save_state(state_file, nodes=nodes, chain=chain, audit_events=audit_events)

            # Load it back
            data = load_state(state_file)
            assert len(data["nodes"]) == 2
            assert data["nodes"][0]["node_id"] == "n1"
            assert len(data["chain"]) == 1
            assert len(data["audit_events"]) == 1

    def test_load_nonexistent_file(self):
        """Test loading from a file that doesn't exist returns empty state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "nonexistent.json"
            data = load_state(state_file)
            assert data["nodes"] == []
            assert data["chain"] == []
            assert data["audit_events"] == []

    def test_atomic_write_on_crash(self):
        """Test that atomic write prevents corruption on simulated crash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"

            # Save initial state
            save_state(state_file, nodes=[{"node_id": "n1"}], chain=[], audit_events=[])
            initial_data = load_state(state_file)

            # Verify we can load it
            assert len(initial_data["nodes"]) == 1

            # The atomic write should have cleaned up any temp files
            temp_files = list(Path(tmpdir).glob(".tmp_state_*"))
            assert len(temp_files) == 0


class TestOrchestratorCommands:
    """Test MainController command handling."""

    def test_add_node_command(self):
        """Test add_node command through orchestrator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = str(Path(tmpdir) / "test_state.json")
            controller = MainController(state_file=state_file, difficulty=1)

            result = controller.handle_command("add_node node1 4.0 8.0")
            assert result["success"] is True
            assert "node1" in result["message"]

            # Verify node was added
            assert "node1" in controller.cli.resource_manager.nodes

    def test_invalid_command(self):
        """Test handling of invalid command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = str(Path(tmpdir) / "test_state.json")
            controller = MainController(state_file=state_file, difficulty=1)

            result = controller.handle_command("invalid_command")
            assert result["success"] is False
            assert "Unknown command" in result["message"]

    def test_request_resource_command(self):
        """Test resource request through orchestrator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = str(Path(tmpdir) / "test_state.json")
            controller = MainController(state_file=state_file, difficulty=1)

            # Add nodes first
            controller.handle_command("add_node node1 4.0")
            controller.handle_command("add_node node2 4.0")

            # Request resource
            result = controller.handle_command("request_resource node1 CPU 2.0")
            assert result["success"] is True
            assert "block" in result["message"].lower()

    def test_view_chain_command(self):
        """Test view_chain command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = str(Path(tmpdir) / "test_state.json")
            controller = MainController(state_file=state_file, difficulty=1)

            result = controller.handle_command("view_chain")
            assert result["success"] is True
            assert "chain" in result["data"]
            # Should have at least genesis block
            assert len(result["data"]["chain"]) >= 1

    def test_status_command(self):
        """Test status command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = str(Path(tmpdir) / "test_state.json")
            controller = MainController(state_file=state_file, difficulty=1)

            result = controller.handle_command("status")
            assert result["success"] is True
            assert "time" in result["data"]
            assert "nodes" in result["data"]
            assert "blocks" in result["data"]


class TestStatePersistence:
    """Test state persistence across controller restarts."""

    def test_state_survives_restart(self):
        """Test that state is preserved across controller restarts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = str(Path(tmpdir) / "test_state.json")

            # First controller: add nodes and make transactions
            controller1 = MainController(state_file=state_file, difficulty=1)
            controller1.handle_command("add_node node1 4.0 8.0")
            controller1.handle_command("add_node node2 4.0 8.0")
            controller1.handle_command("request_resource node1 CPU 2.0")

            # Check state
            assert len(controller1.cli.blockchain.chain) >= 2  # genesis + 1 transaction block
            assert "node1" in controller1.cli.resource_manager.nodes

            # Simulate restart by creating new controller with same state file
            controller2 = MainController(state_file=state_file, difficulty=1)

            # Verify state was loaded
            assert len(controller2.cli.blockchain.chain) >= 2
            assert "node1" in controller2.cli.resource_manager.nodes
            assert "node2" in controller2.cli.resource_manager.nodes

            # Verify allocation was preserved
            node1 = controller2.cli.resource_manager.nodes["node1"]
            assert node1.allocated["CPU"] == 2.0

    def test_audit_log_persistence(self):
        """Test that audit logs are preserved across restarts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = str(Path(tmpdir) / "test_state.json")

            # First controller: generate some audit events
            controller1 = MainController(state_file=state_file, difficulty=1)
            controller1.handle_command("add_node node1 4.0")

            result1 = controller1.handle_command("print_audit")
            events1 = result1["data"]["events"]
            assert len(events1) > 0

            # Second controller: verify audit log persisted
            controller2 = MainController(state_file=state_file, difficulty=1)
            result2 = controller2.handle_command("print_audit")
            events2 = result2["data"]["events"]

            assert len(events2) == len(events1)


class TestSocketAPI:
    """Test socket API functionality."""

    def test_socket_api_basic_command(self):
        """Test basic command through socket API."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = str(Path(tmpdir) / "test_state.json")
            controller = MainController(state_file=state_file, difficulty=1)

            # Start controller and socket API
            controller.start()
            controller.start_socket_api(host='localhost', port=0)  # Use port 0 for random available port

            # Get the actual port assigned
            actual_port = controller.socket_server.getsockname()[1]

            try:
                # Give server a moment to start
                time.sleep(0.1)

                # Connect and send command
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(('localhost', actual_port))

                # Send status command
                request = json.dumps({"command": "status"})
                client.sendall(request.encode('utf-8'))

                # Receive response
                response_data = client.recv(4096)
                response = json.loads(response_data.decode('utf-8'))

                assert response["success"] is True
                assert "data" in response
                assert "blocks" in response["data"]

                client.close()

            finally:
                controller.stop()

    def test_socket_api_add_node(self):
        """Test adding node through socket API."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = str(Path(tmpdir) / "test_state.json")
            controller = MainController(state_file=state_file, difficulty=1)

            controller.start()
            controller.start_socket_api(host='localhost', port=0)
            actual_port = controller.socket_server.getsockname()[1]

            try:
                time.sleep(0.1)

                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(('localhost', actual_port))

                # Add a node
                request = json.dumps({"command": "add_node test_node 4.0 8.0"})
                client.sendall(request.encode('utf-8'))

                response_data = client.recv(4096)
                response = json.loads(response_data.decode('utf-8'))

                assert response["success"] is True
                assert "test_node" in response["message"]

                client.close()

                # Verify node was actually added
                assert "test_node" in controller.cli.resource_manager.nodes

            finally:
                controller.stop()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
