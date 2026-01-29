"""
Command Line Interface for interacting with the distributed operating system.
Handles user input and displays system output.
"""

"""
cli/cli.py
==========

Command Line Interface (CLI) module for the Blockchain-Based
Distributed Operating System (Simulation).

Responsibilities:
- Define and configure CLI commands using argparse
- Validate user input
- Display clear, human-readable output
- Dispatch commands to the appropriate handlers

NOTE:
This module does NOT implement blockchain, consensus, or resource logic.
It only serves as the user-facing interface layer.
"""

import argparse
import sys


# ---------------------------------------------------------------------
# Command Handlers
# ---------------------------------------------------------------------

def add_node(args):
    """
    Handle the 'add_node' command.

    Example:
        python main.py add_node --node-id NODE1
    """
    try:
        node_id = args.node_id

        # Placeholder for controller integration
        # controller.add_node(node_id)

        print(f"[INFO] Node '{node_id}' successfully added to the system.")

    except Exception as e:
        print(f"[ERROR] Failed to add node: {e}")


def request_resource(args):
    """
    Handle the 'request_resource' command.

    Example:
        python main.py request_resource --node-id NODE1 --cpu 2 --storage 5
    """
    try:
        node_id = args.node_id
        cpu = args.cpu
        storage = args.storage

        if cpu is None and storage is None:
            raise ValueError("At least one resource (CPU or storage) must be requested.")

        # Placeholder for controller integration
        # controller.request_resource(node_id, cpu, storage)

        print("[INFO] Resource request submitted:")
        print(f"       Node ID   : {node_id}")
        print(f"       CPU Units : {cpu}")
        print(f"       Storage   : {storage}")
        print("[INFO] Awaiting consensus approval...")

    except Exception as e:
        print(f"[ERROR] Resource request failed: {e}")


def release_resource(args):
    """
    Handle the 'release_resource' command.

    Example:
        python main.py release_resource --node-id NODE1 --cpu 1 --storage 2
    """
    try:
        node_id = args.node_id
        cpu = args.cpu
        storage = args.storage

        if cpu is None and storage is None:
            raise ValueError("At least one resource (CPU or storage) must be released.")

        # Placeholder for controller integration
        # controller.release_resource(node_id, cpu, storage)

        print("[INFO] Resource release submitted:")
        print(f"       Node ID   : {node_id}")
        print(f"       CPU Units : {cpu}")
        print(f"       Storage   : {storage}")
        print("[INFO] Awaiting consensus approval...")

    except Exception as e:
        print(f"[ERROR] Resource release failed: {e}")


def view_chain(args):
    """
    Handle the 'view_chain' command.

    Displays the blockchain in a readable format.
    """
    try:
        # Placeholder for controller integration
        # chain = controller.get_blockchain()

        print("[INFO] Displaying blockchain:")
        print("--------------------------------------------------")
        print("Block 0 | Genesis Block")
        print("Block 1 | Sample Transaction Data")
        print("--------------------------------------------------")

    except Exception as e:
        print(f"[ERROR] Could not display blockchain: {e}")


def validate_chain(args):
    """
    Handle the 'validate_chain' command.

    Verifies blockchain integrity.
    """
    try:
        # Placeholder for controller integration
        # is_valid = controller.validate_blockchain()

        is_valid = True  # Demo placeholder

        if is_valid:
            print("[SUCCESS] Blockchain is valid and untampered.")
        else:
            print("[WARNING] Blockchain validation failed!")

    except Exception as e:
        print(f"[ERROR] Blockchain validation error: {e}")


# ---------------------------------------------------------------------
# Parser Configuration
# ---------------------------------------------------------------------

def create_parser():
    """
    Create and configure the argument parser for the CLI.

    Returns:
        argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Blockchain-Based Distributed Operating System (Simulation CLI)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(
        title="Available Commands",
        dest="command",
        help="Use '<command> --help' for more information"
    )

    # add_node command
    add_node_parser = subparsers.add_parser(
        "add_node",
        help="Add a new node to the distributed system"
    )
    add_node_parser.add_argument(
        "--node-id",
        required=True,
        help="Unique identifier for the node"
    )
    add_node_parser.set_defaults(func=add_node)

    # request_resource command
    request_parser = subparsers.add_parser(
        "request_resource",
        help="Request CPU and/or storage resources"
    )
    request_parser.add_argument("--node-id", required=True, help="Node ID")
    request_parser.add_argument("--cpu", type=int, help="CPU units requested")
    request_parser.add_argument("--storage", type=int, help="Storage units requested")
    request_parser.set_defaults(func=request_resource)

    # release_resource command
    release_parser = subparsers.add_parser(
        "release_resource",
        help="Release allocated resources"
    )
    release_parser.add_argument("--node-id", required=True, help="Node ID")
    release_parser.add_argument("--cpu", type=int, help="CPU units to release")
    release_parser.add_argument("--storage", type=int, help="Storage units to release")
    release_parser.set_defaults(func=release_resource)

    # view_chain command
    view_chain_parser = subparsers.add_parser(
        "view_chain",
        help="View the blockchain"
    )
    view_chain_parser.set_defaults(func=view_chain)

    # validate_chain command
    validate_chain_parser = subparsers.add_parser(
        "validate_chain",
        help="Validate blockchain integrity"
    )
    validate_chain_parser.set_defaults(func=validate_chain)

    return parser


# ---------------------------------------------------------------------
# Public Entry Function (called from main.py)
# ---------------------------------------------------------------------

def run_cli():
    """
    Entry point for running the CLI.

    This function should be called from main.py.
    """
    parser = create_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)

