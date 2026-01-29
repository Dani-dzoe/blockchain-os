"""
Command Line Interface for the blockchain-based distributed operating system demo.

This module provides a beginner-friendly argparse-based CLI.
It keeps a simple in-memory simulation of nodes, resource allocations,
transactions, blocks, and a very small consensus mechanism (majority vote).

Design notes for students:
- This CLI intentionally simulates networking and consensus locally.
- Resource updates (allocate/release) are applied only after a simulated
  consensus step that approves a proposed block containing the transaction.
- The blockchain acts as an immutable audit log; each block records the
  transactions it contains and a hash linking to the previous block.

Commands provided:
- add_node: register a new simulated node with optional resource quotas
- request_resource: request allocation of a resource (CPU/Memory/Storage/Bandwidth)
- release_resource: release previously allocated resources
- view_chain: print the blockchain contents (blocks + transactions)
- validate_chain: check chain integrity by verifying hashes and links

The module is self-contained so it integrates cleanly into the rest of
the academic demo project (it avoids importing the other skeletal modules
which may be intentionally left incomplete for the exercise).

"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple


# -- Data models used only within this CLI (kept simple and educational) --

@dataclass
class NodeState:
    """Stores per-node information: identifier, quotas and current allocations.

    Quotas and allocations are simple dictionaries keyed by resource name
    (e.g., 'CPU', 'Memory', 'Storage', 'Bandwidth'). Values are numeric.
    """

    node_id: str
    quotas: Dict[str, float] = field(default_factory=dict)
    allocated: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        # Ensure all quota keys exist for the standard resources
        for r in Controller.VALID_RESOURCES:
            self.quotas.setdefault(r, 0.0)
            self.allocated.setdefault(r, 0.0)


@dataclass
class Transaction:
    """Represents a single resource operation to be recorded in a block.

    Fields:
        node_id: requester node
        resource_type: one of Controller.VALID_RESOURCES
        amount: positive number
        transaction_type: 'allocate' or 'release'
        timestamp: epoch float for ordering and reproducibility
    """

    node_id: str
    resource_type: str
    amount: float
    transaction_type: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "resource_type": self.resource_type,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "timestamp": self.timestamp,
        }

    def __str__(self) -> str:
        return (
            f"{self.transaction_type.upper():8} | {self.amount:>6} {self.resource_type:8} "
            f"| node={self.node_id} | ts={self.timestamp:.3f}"
        )


@dataclass
class Block:
    """Simple block structure for the demonstration blockchain.

    Fields:
        index: block height (0-based)
        timestamp: block creation time
        transactions: list of Transaction objects
        previous_hash: hex string of previous block's hash
        hash: computed hash for this block (set after creation)
    """

    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    hash: Optional[str] = None

    def compute_hash(self) -> str:
        """Computes a SHA-256 hash of this block's canonical representation.

        We create a deterministic JSON string of the block content (ordering
        matters). This simple scheme is sufficient for an educational demo.
        """
        block_content = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [t.to_dict() for t in self.transactions],
            "previous_hash": self.previous_hash,
        }
        serialized = json.dumps(block_content, sort_keys=True).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()


class ConsensusError(Exception):
    """Raised when consensus does not reach a majority approval."""


class Controller:
    """Central controller used by the CLI to manage simulated state.

    This class is intentionally simple and stores everything in memory. It
    demonstrates the ordering: validation -> consensus -> state update ->
    append block to chain.
    """

    VALID_RESOURCES = ["CPU", "Memory", "Storage", "Bandwidth"]

    def __init__(self):
        # map node_id -> NodeState
        self.nodes: Dict[str, NodeState] = {}
        # the blockchain (list of Block objects)
        self.chain: List[Block] = []

        # Initialize genesis block
        genesis = Block(index=0, timestamp=time.time(), transactions=[], previous_hash="0")
        genesis.hash = genesis.compute_hash()
        self.chain.append(genesis)

    # ---------------- Node management ----------------
    def add_node(self, node_id: str, quotas: Optional[Dict[str, float]] = None) -> None:
        """Register a new node with optional resource quotas.

        Raises ValueError on invalid input (empty id or duplicate node).
        """
        node_id = node_id.strip()
        if not node_id:
            raise ValueError("node_id cannot be empty")
        if node_id in self.nodes:
            raise ValueError(f"Node '{node_id}' already exists")

        quotas = quotas or {}
        # Normalize quotas and ensure they are non-negative numbers
        normalized = {}
        for r in self.VALID_RESOURCES:
            v = float(quotas.get(r, 0.0)) if quotas.get(r) is not None else 0.0
            if v < 0:
                raise ValueError(f"Quota for {r} must be non-negative")
            normalized[r] = v

        self.nodes[node_id] = NodeState(node_id=node_id, quotas=normalized)

    # ---------------- Transaction lifecycle ----------------
    def _validate_request(self, node_id: str, resource_type: str, amount: float, tx_type: str) -> None:
        """Internal validation for requests/releases.

        Ensures node exists, resource type is valid, amount is positive and
        that quotas/allocations make sense for the operation.
        Raises ValueError on invalid requests.
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' does not exist")
        if resource_type not in self.VALID_RESOURCES:
            raise ValueError(f"resource_type must be one of {self.VALID_RESOURCES}")
        if amount <= 0:
            raise ValueError("amount must be greater than zero")

        node = self.nodes[node_id]
        if tx_type == "allocate":
            if node.allocated[resource_type] + amount > node.quotas[resource_type]:
                raise ValueError(
                    f"Allocation rejected: would exceed quota ({node.allocated[resource_type]} + {amount} > {node.quotas[resource_type]})"
                )
        elif tx_type == "release":
            if amount > node.allocated[resource_type]:
                raise ValueError(
                    f"Release rejected: node only has {node.allocated[resource_type]} {resource_type} allocated"
                )
        else:
            raise ValueError("transaction_type must be 'allocate' or 'release'")

    def _create_block_with_single_tx(self, tx: Transaction) -> Block:
        """Create a new block containing a single transaction and compute its hash."""
        index = len(self.chain)
        previous_hash = self.chain[-1].hash or ""
        block = Block(index=index, timestamp=time.time(), transactions=[tx], previous_hash=previous_hash)
        block.hash = block.compute_hash()
        return block

    def _simulate_consensus(self, block: Block) -> bool:
        """Simulates a simple majority-vote consensus among registered nodes.

        For deterministic and predictable demo behavior, every node votes
        'yes' unless the block contains an operation that would be invalid
        when applied (this should not happen because we pre-validate). In
        a larger simulation you could randomize or introduce faults.
        """
        total = len(self.nodes)
        if total == 0:
            # No nodes => cannot reach consensus
            return False

        # For demo purposes, assume all nodes vote yes
        yes_votes = total
        # Majority needed strictly greater than half
        return yes_votes > (total // 2)

    def _apply_transaction(self, tx: Transaction) -> None:
        """Apply an already-approved transaction to node state.

        This modifies the in-memory allocations. Only called after consensus.
        """
        node = self.nodes[tx.node_id]
        if tx.transaction_type == "allocate":
            node.allocated[tx.resource_type] += tx.amount
        elif tx.transaction_type == "release":
            node.allocated[tx.resource_type] -= tx.amount
            # Guard against negative rounding issues
            if node.allocated[tx.resource_type] < 1e-12:
                node.allocated[tx.resource_type] = 0.0
        else:
            raise ValueError("Unknown transaction type when applying to state")

    def propose_and_commit(self, tx: Transaction) -> Tuple[bool, Optional[str]]:
        """Propose a block containing tx, run consensus, and commit on success.

        Returns (True, block_hash) on success. On consensus failure returns
        (False, reason).
        """
        # Create block
        block = self._create_block_with_single_tx(tx)

        # Simulate majority consensus
        approved = self._simulate_consensus(block)
        if not approved:
            return False, "Consensus failed: majority not reached"

        # Commit: apply transaction to state then append block to chain
        self._apply_transaction(tx)
        self.chain.append(block)
        return True, block.hash

    # ---------------- Public CLI-facing operations ----------------
    def request_resource(self, node_id: str, resource_type: str, amount: float) -> str:
        """Handle a resource allocation request from a node.

        Validates the request, proposes a block and runs consensus. On success
        returns a human-readable success message. Raises ValueError for input
        validation failures and ConsensusError if consensus fails.
        """
        # Validate inputs and quotas first
        self._validate_request(node_id, resource_type, amount, "allocate")

        tx = Transaction(node_id=node_id, resource_type=resource_type, amount=amount, transaction_type="allocate")

        approved, info = self.propose_and_commit(tx)
        if not approved:
            raise ConsensusError(info)

        return f"Resource allocated: {amount} {resource_type} to {node_id}. Block hash: {info}"

    def release_resource(self, node_id: str, resource_type: str, amount: float) -> str:
        """Handle releasing resources for a node (similar to request_resource)."""
        self._validate_request(node_id, resource_type, amount, "release")

        tx = Transaction(node_id=node_id, resource_type=resource_type, amount=amount, transaction_type="release")

        approved, info = self.propose_and_commit(tx)
        if not approved:
            raise ConsensusError(info)

        return f"Resource released: {amount} {resource_type} from {node_id}. Block hash: {info}"

    def view_chain(self) -> List[Block]:
        """Return the chain for printing. The genesis block is index 0."""
        return list(self.chain)

    def validate_chain(self) -> Tuple[bool, str]:
        """Validate the blockchain integrity by recomputing hashes and links.

        Returns (True, message) if valid, otherwise (False, explanation).
        """
        if not self.chain:
            return False, "Empty chain"
        for i, block in enumerate(self.chain):
            expected_hash = block.compute_hash()
            if block.hash != expected_hash:
                return False, f"Block {i} hash mismatch: expected {expected_hash} got {block.hash}"
            if i == 0:
                # genesis previous_hash should be '0'
                if block.previous_hash != "0":
                    return False, "Genesis block has invalid previous_hash"
            else:
                prev = self.chain[i - 1]
                if block.previous_hash != prev.hash:
                    return False, f"Block {i} previous_hash does not match hash of block {i-1}"
        return True, "Chain is valid"


# ---------------- Command-line interface wiring ----------------

def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argparse.ArgumentParser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="blockchain-os-cli",
        description="CLI demo for a blockchain-based distributed operating system",
    )

    sub = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # add_node
    p_add = sub.add_parser("add_node", help="Register a new node with optional resource quotas")
    p_add.add_argument("node_id", help="Unique identifier for the node")
    p_add.add_argument("--cpu", type=float, default=0.0, help="CPU quota for the node (numeric)")
    p_add.add_argument("--memory", type=float, default=0.0, help="Memory quota for the node")
    p_add.add_argument("--storage", type=float, default=0.0, help="Storage quota for the node")
    p_add.add_argument("--bandwidth", type=float, default=0.0, help="Bandwidth quota for the node")

    # request_resource
    p_req = sub.add_parser("request_resource", help="Request allocation of a resource for a node")
    p_req.add_argument("node_id", help="Node requesting the resource")
    p_req.add_argument("resource", choices=Controller.VALID_RESOURCES, help="Resource type to request")
    p_req.add_argument("amount", type=float, help="Amount to request (positive number)")

    # release_resource
    p_rel = sub.add_parser("release_resource", help="Release allocated resource for a node")
    p_rel.add_argument("node_id", help="Node releasing the resource")
    p_rel.add_argument("resource", choices=Controller.VALID_RESOURCES, help="Resource type to release")
    p_rel.add_argument("amount", type=float, help="Amount to release (positive number)")

    # view_chain
    sub.add_parser("view_chain", help="Print the blockchain (blocks and transactions)")

    # validate_chain
    sub.add_parser("validate_chain", help="Validate blockchain integrity by recomputing hashes")

    return parser


def pretty_print_chain(chain: List[Block]) -> None:
    """Prints the blockchain in a human-readable step-by-step format.

    This function is deliberately verbose to serve as an educational aid.
    """
    print("\n==== Blockchain (most recent last) ====")
    for block in chain:
        print(f"\nBlock {block.index} | ts={block.timestamp:.3f} | hash={block.hash}")
        print(f"  previous_hash: {block.previous_hash}")
        if not block.transactions:
            print("  (no transactions in this block)")
        for tx in block.transactions:
            print("  -", str(tx))
    print("\n====================================\n")


def run_cli(argv: Optional[List[str]] = None) -> int:
    """Entry point for the CLI. Parses args, executes commands and returns an exit code.

    The function returns 0 on success and non-zero on failures. This design allows
    easy invocation from other scripts or unit tests.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    controller = Controller()

    try:
        if args.command == "add_node":
            quotas = {
                "CPU": args.cpu,
                "Memory": args.memory,
                "Storage": args.storage,
                "Bandwidth": args.bandwidth,
            }
            controller.add_node(args.node_id, quotas=quotas)
            print(f"Node '{args.node_id}' added with quotas: {quotas}")

        elif args.command == "request_resource":
            msg = controller.request_resource(args.node_id, args.resource, args.amount)
            print(msg)
            # Show node allocation after successful commit for clarity
            node = controller.nodes[args.node_id]
            print(f"Current allocation for {args.node_id}: {node.allocated}")

        elif args.command == "release_resource":
            msg = controller.release_resource(args.node_id, args.resource, args.amount)
            print(msg)
            node = controller.nodes[args.node_id]
            print(f"Current allocation for {args.node_id}: {node.allocated}")

        elif args.command == "view_chain":
            chain = controller.view_chain()
            pretty_print_chain(chain)

        elif args.command == "validate_chain":
            ok, reason = controller.validate_chain()
            if ok:
                print("Blockchain validation: OK - ", reason)
            else:
                print("Blockchain validation: FAILED - ", reason)
                return 2

        else:
            # Should not happen because argparse enforces choices
            parser.print_help()
            return 1

    except ValueError as ve:
        print(f"Input error: {ve}")
        return 2
    except ConsensusError as ce:
        print(f"Consensus error: {ce}")
        return 3
    except Exception as e:
        # Catch-all for unexpected exceptions; print a helpful message but
        # avoid leaking sensitive info; include exception type and message.
        print(f"Unexpected error ({type(e).__name__}): {e}")
        return 4

    return 0


# When executed as a script, run the CLI with sys.argv[1:]
if __name__ == "__main__":
    exit_code = run_cli(sys.argv[1:])
    sys.exit(exit_code)
