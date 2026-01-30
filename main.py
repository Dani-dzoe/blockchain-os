"""
Main demo runner for the Blockchain-Based Distributed Operating System.

This script demonstrates an end-to-end flow using the integrated CLI
controller that links the project's components. It is intended for a
quick local demo (single-process, in-memory):

- Add a node
- Request resources
- Release resources
- View and validate the blockchain
- Print audit log

Run: python3 main.py

Note: This demo starts with a clean state each time (removes system_state.json)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from cli.cli import IntegratedCLI
from logger.audit_logger import print_audit_log


def demo_sequence():
    # Clean state file before starting to ensure fresh demo
    state_file = Path("system_state.json")
    if state_file.exists():
        print("Cleaning previous state for fresh demo...\n")
        state_file.unlink()

    cli = IntegratedCLI(difficulty=2)

    print("Starting demo sequence...\n")

    # Add a node with quotas
    print(cli.add_node('demo-node', {'CPU': 4.0, 'Memory': 8.0}))

    # Request some resources
    print(cli.request_resource('demo-node', 'CPU', 2.0))
    print(cli.request_resource('demo-node', 'Memory', 3.0))

    # Release some resource
    print(cli.release_resource('demo-node', 'CPU', 1.0))

    # View chain
    chain = cli.view_chain()
    print('\nBlockchain:')
    print(json.dumps(chain, indent=2))

    # Validate chain
    ok, reason = cli.validate_chain()
    print('\nChain valid?', ok, '-', reason)

    # Print audit log
    print('\nAudit log:')
    print_audit_log()


if __name__ == '__main__':
    demo_sequence()


