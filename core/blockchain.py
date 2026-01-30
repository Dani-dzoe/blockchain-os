"""
Blockchain module for the educational distributed operating system demo.

This module provides a self-contained, well-documented `Blockchain` class that
supports:
- Creating blocks (each block contains index, timestamp, transactions,
  previous_hash, nonce, and hash).
- Computing SHA-256 hashes of blocks in a deterministic way.
- A simple proof-of-work (adjustable difficulty) which demonstrates why the
  nonce exists and how it contributes to immutability.
- Validating the entire chain by recomputing hashes and verifying previous
  hash pointers.

Important educational notes on immutability (see comments below and in
`is_chain_valid`):
- Each block stores the cryptographic hash of its contents (including the
  nonce). Changing any block's contents changes its hash.
- Every block also stores the previous block's hash. This links blocks into a
  chain: to change an old block you'd have to recompute every subsequent block's
  hash to restore consistency. If proof-of-work is used, recomputing requires
  repeating the expensive work (finding new nonces) for all subsequent blocks,
  which demonstrates computational immutability in real blockchains.

This implementation is intentionally simple and synchronous (in-memory).
It is sufficient for classroom demonstrations and unit tests.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Block:
    """Dataclass representing a single block in the blockchain.

    Fields:
        index: Height of the block (0 for genesis).
        timestamp: Time of block creation (epoch seconds, float).
        transactions: List of transaction dictionaries (or any JSON-serializable objects).
        previous_hash: Hex string of the previous block's hash ("0" for genesis).
        nonce: Integer used to vary the block hash (used for proof-of-work).
        hash: Hex string of this block's final hash (computed after mining).
    """

    index: int
    timestamp: float
    transactions: List[Dict[str, Any]] = field(default_factory=list)
    previous_hash: str = "0"
    nonce: int = 0
    hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize a block to a JSON-safe dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Block":
        """Create a Block instance from a dictionary (as produced by to_dict)."""
        return cls(
            index=int(data.get("index", 0)),
            timestamp=float(data.get("timestamp", 0.0)),
            transactions=data.get("transactions", []),
            previous_hash=data.get("previous_hash", "0"),
            nonce=int(data.get("nonce", 0)),
            hash=str(data.get("hash", "")),
        )


class Blockchain:
    """A minimal educational blockchain implementation.

    Usage summary:
        bc = Blockchain(difficulty=2)
        bc.create_genesis_block()
        bc.add_block([{"node":"A","op":"allocate","amt":1}])
        ok, reason = bc.is_chain_valid()

    The `difficulty` parameter controls how many leading zeros are required
    in the hex hash for proof-of-work. A small value (e.g., 2) is fine for
    classroom demos and won't consume much CPU.
    """

    def __init__(self, difficulty: int = 2) -> None:
        # Chain stored as a list of Block objects; index 0 is the genesis block.
        self.chain: List[Block] = []
        # Difficulty for the simple proof-of-work algorithm (number of leading zeros)
        self.difficulty = max(0, int(difficulty))
        # Create the genesis block on initialization for convenience
        self.create_genesis_block()

    # ---------------- Block creation and hashing ----------------
    def create_genesis_block(self) -> Block:
        """Create and append the genesis (first) block of the chain.

        The genesis block has index 0, previous_hash set to '0', and an empty
        transaction list. We compute its hash using the same mining procedure
        to keep behavior consistent.
        """
        genesis = Block(index=0, timestamp=time.time(), transactions=[], previous_hash="0")
        genesis.hash = self.proof_of_work(genesis)
        self.chain.append(genesis)
        return genesis

    def create_block(self, transactions: Optional[List[Dict[str, Any]]] = None) -> Block:
        """Create a new block that includes `transactions`, mine it, append to chain, and return it.

        The function determines the next block index and sets the previous_hash
        to the latest block's hash. Mining (finding a nonce such that the
        block's hash has the required number of leading zeros) is performed by
        `proof_of_work`.
        """
        transactions = transactions or []
        index = len(self.chain)
        previous_hash = self.chain[-1].hash if self.chain else "0"
        block = Block(index=index, timestamp=time.time(), transactions=transactions, previous_hash=previous_hash)
        # Find a valid nonce and compute the corresponding hash
        block.hash = self.proof_of_work(block)
        self.chain.append(block)
        return block

    def compute_hash(self, block: Block) -> str:
        """Compute a SHA-256 hash for a block's contents.

        The block is serialized in a canonical, deterministic way (JSON with
        keys sorted) so that recomputing the hash later will yield the same
        result unless the block's contents (including nonce) changed.

        The hash includes:
        - index
        - timestamp
        - transactions (serialized)
        - previous_hash
        - nonce

        Note: transactions must be JSON-serializable objects for deterministic
        hashing. In this educational implementation we assume they are.
        """
        # Construct a dictionary of block content in a stable order
        block_content = {
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": block.transactions,
            "previous_hash": block.previous_hash,
            "nonce": block.nonce,
        }
        # Deterministic serialization
        block_string = json.dumps(block_content, sort_keys=True).encode("utf-8")
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, block: Block) -> str:
        """Simple proof-of-work algorithm: increment the nonce until the resulting
        hash has `difficulty` leading zeros in hexadecimal representation.

        The nonce is stored in the block and the final hash is returned.

        This demonstrates why including a nonce helps secure immutability:
        if you change any content of a block, you must redo the proof-of-work
        (i.e., find a new nonce) to produce a valid hash, and for a chain that
        requirement cascades to all subsequent blocks.
        """
        assert isinstance(block.nonce, int), "block.nonce must be an integer"
        prefix = "0" * self.difficulty
        # Try successive nonces until we find a hash with required prefix
        while True:
            computed_hash = self.compute_hash(block)
            if computed_hash.startswith(prefix):
                return computed_hash
            block.nonce += 1

    # ---------------- Chain validation ----------------
    def is_chain_valid(self) -> Tuple[bool, str]:
        """Validate the blockchain integrity.

        This function performs the following checks:
        1. Recompute the hash of each block from its stored contents (index,
           timestamp, transactions, previous_hash, nonce) and ensure it
           matches the stored `hash` field.
        2. Ensure every block's `previous_hash` equals the `hash` of the
           preceding block (for index > 0).
        3. Ensure each block's hash meets the proof-of-work difficulty.

        If any check fails, the function returns (False, explanation).
        Otherwise it returns (True, "Chain is valid").

        Educational explanation of immutability checks performed here:
        - Because each block's hash covers the block's content and nonce, any
          change to a block will change its recomputed hash and be detected by
          step (1).
        - Because each block references the previous block's hash, changing an
          old block also invalidates the `previous_hash` fields of all
          subsequent blocks unless an attacker recomputes their hashes too.
        - If proof-of-work is enabled (difficulty > 0), recomputing a changed
          block's hash requires re-running the work for that block and every
          later block, which quickly becomes computationally expensive and
          demonstrates the chain's tamper-resistance.
        """
        if not self.chain:
            return False, "Chain is empty"

        prefix = "0" * self.difficulty

        for i, block in enumerate(self.chain):
            # Recompute the hash from block contents
            computed_hash = self.compute_hash(block)
            if block.hash != computed_hash:
                return False, f"Invalid hash at block {i}: stored={block.hash} recomputed={computed_hash}"

            # Check proof-of-work difficulty
            if not block.hash.startswith(prefix):
                return False, f"Block {i} does not meet difficulty prefix: {block.hash}"

            # Check previous hash link (skip genesis)
            if i == 0:
                if block.previous_hash != "0":
                    return False, "Genesis block previous_hash must be '0'"
            else:
                prev = self.chain[i - 1]
                if block.previous_hash != prev.hash:
                    return False, f"Block {i} previous_hash ({block.previous_hash}) does not match hash of block {i-1} ({prev.hash})"

        return True, "Chain is valid"

    # ---------------- Utility functions ----------------
    def to_dict(self) -> List[Dict[str, Any]]:
        """Serialize the entire chain to a list of dictionaries for inspection or tests."""
        result: List[Dict[str, Any]] = []
        for block in self.chain:
            result.append(block.to_dict())
        return result

    @classmethod
    def from_dict(cls, chain_data: List[Dict[str, Any]], difficulty: int = 2) -> "Blockchain":
        """Create a Blockchain from a list of block dictionaries.

        This performs minimal validation (loads blocks into chain). Use
        `is_chain_valid()` to verify integrity after loading.
        """
        bc = cls(difficulty=difficulty)
        # Replace genesis block with the first item if provided
        bc.chain = []
        for bdata in chain_data:
            block = Block.from_dict(bdata)
            bc.chain.append(block)
        return bc


# If used as a script, run a tiny self-test demonstrating creation and validation
if __name__ == "__main__":
    # Quick smoke test for demonstration; not a substitute for unit tests
    bc = Blockchain(difficulty=2)
    print("Created genesis block:", bc.chain[0].hash)
    bc.create_block([{"from": "nodeA", "type": "allocate", "amount": 1}])
    bc.create_block([{"from": "nodeB", "type": "allocate", "amount": 2}])
    ok, reason = bc.is_chain_valid()
    print("Chain valid?", ok, "-", reason)
    # Show a serialized view
    print(json.dumps(bc.to_dict(), indent=2))
