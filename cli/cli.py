"""
Integrated CLI for the blockchain-based distributed operating system demo.

This CLI wires together the project's modules:
- core.node.Node
- core.transaction.Transaction
- core.blockchain.Blockchain
- resources.resource_manager.ResourceManager
- auth.auth.AuthManager
- consensus.consensus.ConsensusEngine
- logger.audit_logger

It accepts commands to add nodes, request/release resources, view and validate
the blockchain. All state is stored in memory for the lifetime of the process.
"""

from __future__ import annotations

import argparse
import sys
import time
from typing import List, Optional, Dict, Any, Tuple

from core.node import Node
from core.transaction import Transaction
from core.blockchain import Blockchain, Block
from resources.resource_manager import ResourceManager
from auth.auth import AuthManager
from consensus.consensus import ConsensusEngine, validate_block_structure
from logger.audit_logger import log_event, print_audit_log
from logger.audit_logger import set_events, get_events
from persistence import save_state, load_state, DEFAULT_STATE_FILE


class IntegratedCLI:
    """Controller-oriented CLI that links the project's components.

    This class keeps in-memory instances of the modules and exposes methods
    called by the command-line interface. It demonstrates the intended
    interactions between components in a clear and modular way.
    """

    def __init__(self, difficulty: int = 2, state_file: str = None):
        # Core components
        self.blockchain = Blockchain(difficulty=difficulty)
        self.resource_manager = ResourceManager()
        self.auth = AuthManager()
        # consensus engine is created once there are nodes; keep None until then
        self.consensus: Optional[ConsensusEngine] = None
        # Persistence
        self.state_file = DEFAULT_STATE_FILE if state_file is None else DEFAULT_STATE_FILE.parent.joinpath(state_file)
        # Track if file has been tampered with
        self.file_tampered = False
        self.tamper_message = ""
        # Attempt to load existing state
        self._load_state()

    # ---------------- Node management ----------------
    def add_node(self, node_id: str, quotas: Dict[str, float]) -> str:
        """Register a new node with quotas, issue token, and record in blockchain.

        Returns a short human-readable message.
        """
        node_id = node_id.strip()
        if not node_id:
            raise ValueError("node_id cannot be empty")
        if node_id in self.resource_manager.nodes:
            raise ValueError(f"Node '{node_id}' already exists")

        # Create the node
        node = Node(node_id=node_id, quotas=quotas)
        self.resource_manager.register_node(node)
        token = self.auth.get_token_for(node_id)

        # Recreate consensus engine with updated node list
        self._update_consensus_engine()

        # Create a transaction to record node addition in blockchain
        # Note: We use 'CPU' as resource_type since Transaction requires a valid resource
        # The transaction_type 'add_node' indicates this is node registration, not resource allocation
        tx = Transaction(
            node_id=node_id,
            resource_type='CPU',  # Placeholder - actual meaning is in transaction_type
            amount=0.0,
            transaction_type='add_node'
        )

        # Create and mine a block for this transaction
        index = len(self.blockchain.chain)
        prev_hash = self.blockchain.chain[-1].hash if self.blockchain.chain else '0'
        block = Block(index=index, timestamp=time.time(), transactions=[tx.to_dict()], previous_hash=prev_hash)
        block.hash = self.blockchain.proof_of_work(block)

        # If we have consensus engine (multiple nodes), get approval
        if self.consensus:
            approved, details = self.consensus.request_consensus(block, validate_block_structure)
            if not approved:
                # Rollback: remove the node that was just added
                del self.resource_manager.nodes[node_id]
                log_event(node_id, 'add_node', 'rejected_by_consensus', {'reason': details.get('reason')})
                self._save_state()
                raise RuntimeError(f"Node addition rejected by consensus: {details}")

        # Add block to blockchain
        self.blockchain.chain.append(block)

        msg = f"Node '{node_id}' added. Token: {token}"
        log_event(node_id, 'add_node', 'created', {'quotas': quotas, 'block_hash': block.hash})
        # Persist state
        self._save_state()
        return msg

    def _update_consensus_engine(self):
        """Recreate consensus engine from current registered nodes."""
        node_list = list(self.resource_manager.nodes.values())
        if not node_list:
            self.consensus = None
            return
        # Create a new consensus engine (vote threshold default majority)
        self.consensus = ConsensusEngine(node_list)
        # After updating consensus, save the state
        self._save_state()

    # ---------------- Resource operations ----------------
    def request_resource(self, node_id: str, resource: str, amount: float) -> str:
        """Process a resource allocation request: validate, propose block, run consensus, apply.

        This function demonstrates the pipeline: validate inputs -> build transaction ->
        build block and mine -> ask consensus -> on approval apply to resource manager and append to chain.
        """
        # Basic validations
        if node_id not in self.resource_manager.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        if resource not in self.resource_manager.nodes[node_id].quotas:
            raise ValueError(f"Invalid resource: {resource}")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

        # Check node-level quota
        if not self.resource_manager.can_allocate(node_id, resource, amount):
            raise ValueError(f"Allocation would exceed quota for {node_id}")

        # Build transaction (validated by Transaction class)
        tx = Transaction(node_id=node_id, resource_type=resource, amount=amount, transaction_type='allocate')

        # Build a candidate block (not appended yet)
        index = len(self.blockchain.chain)
        prev_hash = self.blockchain.chain[-1].hash if self.blockchain.chain else '0'
        block = Block(index=index, timestamp=time.time(), transactions=[tx.to_dict()], previous_hash=prev_hash)
        # Mine block (compute nonce and hash)
        block.hash = self.blockchain.proof_of_work(block)

        # Ensure we have a consensus engine
        if not self.consensus:
            raise RuntimeError("No consensus nodes available; add nodes before proposing blocks")

        # Ask for consensus with a simple pre-validation function
        approved, details = self.consensus.request_consensus(block, validate_block_structure)
        if not approved:
            log_event(node_id, 'request_resource', 'rejected', {'reason': details.get('reason')})
            raise RuntimeError(f"Consensus rejected the block: {details}")

        # On approval, apply allocation and append block to blockchain
        self.resource_manager.apply_allocation(node_id, resource, amount)
        self.blockchain.chain.append(block)
        log_event(node_id, 'request_resource', 'accepted', {'resource': resource, 'amount': amount, 'block_hash': block.hash})
        self._save_state()
        return f"Allocation accepted and committed in block {block.index} (hash={block.hash})"

    def release_resource(self, node_id: str, resource: str, amount: float) -> str:
        """Process a resource release request similar to request_resource."""
        if node_id not in self.resource_manager.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        if not self.resource_manager.nodes[node_id].can_release(resource, amount):
            raise ValueError(f"Node {node_id} does not have {amount} {resource} allocated")

        tx = Transaction(node_id=node_id, resource_type=resource, amount=amount, transaction_type='release')

        index = len(self.blockchain.chain)
        prev_hash = self.blockchain.chain[-1].hash if self.blockchain.chain else '0'
        block = Block(index=index, timestamp=time.time(), transactions=[tx.to_dict()], previous_hash=prev_hash)
        block.hash = self.blockchain.proof_of_work(block)

        if not self.consensus:
            raise RuntimeError("No consensus nodes available; add nodes before proposing blocks")

        approved, details = self.consensus.request_consensus(block, validate_block_structure)
        if not approved:
            log_event(node_id, 'release_resource', 'rejected', {'reason': details.get('reason')})
            raise RuntimeError(f"Consensus rejected the block: {details}")

        # Apply release and append block
        self.resource_manager.apply_release(node_id, resource, amount)
        self.blockchain.chain.append(block)
        log_event(node_id, 'release_resource', 'accepted', {'resource': resource, 'amount': amount, 'block_hash': block.hash})
        self._save_state()
        return f"Release accepted and committed in block {block.index} (hash={block.hash})"

    # ---------------- Viewing and validation ----------------
    def view_chain(self) -> List[Dict[str, Any]]:
        """Return a serialized view of the blockchain for printing."""
        return self.blockchain.to_dict()

    def validate_chain(self) -> Tuple[bool, str]:
        """Validate blockchain integrity and file integrity.

        Checks:
        1. File was not tampered with on load
        2. Blockchain structural integrity (hashes, links, PoW)
        3. File checksum to detect manual tampering since last load

        Returns (ok, reason).
        """
        # Check if tampering was detected on load
        if self.file_tampered:
            return False, f"🚨 FILE TAMPERING DETECTED ON LOAD:\n   {self.tamper_message}"

        # Check blockchain structural integrity
        bc_ok, bc_reason = self.blockchain.is_chain_valid()

        # Check file integrity (checksum) again
        from persistence import verify_data_integrity, load_state
        loaded = load_state(self.state_file)
        file_ok, file_reason = loaded.get('integrity_ok', True), loaded.get('integrity_msg', 'OK')

        if not bc_ok:
            return False, f"Blockchain invalid: {bc_reason}"

        if not file_ok:
            return False, f"🚨 FILE TAMPERING DETECTED:\n   {file_reason}"

        return True, "✅ Chain is valid"

    # ---------------- Persistence ----------------
    def _load_state(self):
        data = load_state(self.state_file)

        # Check file integrity
        if not data.get('integrity_ok', True):
            self.file_tampered = True
            self.tamper_message = data.get('integrity_msg', 'Unknown error')
            print(f"\n⚠️  ⚠️  ⚠️  SECURITY ALERT ⚠️  ⚠️  ⚠️")
            print(f"FILE INTEGRITY CHECK FAILED!")
            print(f"The state file may have been tampered with.")
            print(f"Details: {self.tamper_message}\n")

        # Load nodes
        nodes = data.get('nodes', [])
        from core.node import Node as CoreNode
        for nd in nodes:
            node = CoreNode.from_dict(nd)
            try:
                self.resource_manager.register_node(node)
            except ValueError:
                # ignore duplicates on load
                pass
        # Load chain
        chain_data = data.get('chain', [])
        if chain_data:
            self.blockchain = Blockchain.from_dict(chain_data, difficulty=self.blockchain.difficulty)
        # Load audit events
        audit_events = data.get('audit_events', [])
        if audit_events:
            set_events(audit_events)
        # Update consensus engine after load
        self._update_consensus_engine()

    def _save_state(self):
        nodes = [n.to_dict() for n in self.resource_manager.nodes.values()]
        chain = self.blockchain.to_dict()
        audit_events = get_events()
        save_state(self.state_file, nodes=nodes, chain=chain, audit_events=audit_events)

# ---------------- Command-line wiring ----------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='blockchain-os-integrated', description='Integrated CLI for the blockchain OS demo')
    sub = p.add_subparsers(dest='command', required=True)

    p_add = sub.add_parser('add_node', help='Register a node with quotas')
    p_add.add_argument('node_id')
    p_add.add_argument('--cpu', type=float, default=0.0)
    p_add.add_argument('--memory', type=float, default=0.0)
    p_add.add_argument('--storage', type=float, default=0.0)
    p_add.add_argument('--bandwidth', type=float, default=0.0)

    p_req = sub.add_parser('request_resource', help='Request allocation')
    p_req.add_argument('node_id')
    p_req.add_argument('resource', choices=['CPU', 'Memory', 'Storage', 'Bandwidth'])
    p_req.add_argument('amount', type=float)

    p_rel = sub.add_parser('release_resource', help='Release allocated resource')
    p_rel.add_argument('node_id')
    p_rel.add_argument('resource', choices=['CPU', 'Memory', 'Storage', 'Bandwidth'])
    p_rel.add_argument('amount', type=float)

    sub.add_parser('view_chain', help='Print blockchain')
    sub.add_parser('validate_chain', help='Validate blockchain integrity')
    sub.add_parser('print_audit', help='Print audit log events')

    return p


def pretty_print_chain(serialized_chain: List[Dict[str, Any]]):
    print('\n==== Blockchain (most recent last) ====')
    for b in serialized_chain:
        print(f"\nBlock {b['index']} | ts={b['timestamp']:.3f} | hash={b['hash']}")
        print(f"  previous_hash: {b['previous_hash']}")
        txs = b.get('transactions', [])
        if not txs:
            print('  (no transactions)')
        for tx in txs:
            print('  -', tx)
    print('\n====================================\n')


def run_cli(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    cli = IntegratedCLI(difficulty=2)

    try:
        if args.command == 'add_node':
            quotas = {'CPU': args.cpu, 'Memory': args.memory, 'Storage': args.storage, 'Bandwidth': args.bandwidth}
            msg = cli.add_node(args.node_id, quotas)
            print(msg)

        elif args.command == 'request_resource':
            msg = cli.request_resource(args.node_id, args.resource, args.amount)
            print(msg)
            # Show allocation
            print('Allocation state:', cli.resource_manager.get_status()['nodes'].get(args.node_id))

        elif args.command == 'release_resource':
            msg = cli.release_resource(args.node_id, args.resource, args.amount)
            print(msg)
            print('Allocation state:', cli.resource_manager.get_status()['nodes'].get(args.node_id))

        elif args.command == 'view_chain':
            serialized = cli.view_chain()
            pretty_print_chain(serialized)

        elif args.command == 'validate_chain':
            ok, reason = cli.validate_chain()
            if ok:
                print('Blockchain validation: OK -', reason)
            else:
                print('Blockchain validation: FAILED -', reason)
                return 2

        elif args.command == 'print_audit':
            print_audit_log()

        else:
            parser.print_help()
            return 1

    except ValueError as ve:
        print('Input error:', ve)
        return 2
    except RuntimeError as re:
        print('Runtime error:', re)
        return 3
    except Exception as e:
        print(f'Unexpected error ({type(e).__name__}):', e)
        return 4

    return 0


if __name__ == '__main__':
    sys.exit(run_cli(sys.argv[1:]))
