"""
Main Controller - Orchestration Layer

This file acts as the single orchestrator for the blockchain-based distributed OS.
It uses the implemented modules (IntegratedCLI) and exposes both:
1. A simple interactive REPL for human interaction
2. A socket-based API for programmatic access

The controller maintains persistent state across invocations using JSON persistence.
"""

from __future__ import annotations

import logging
import argparse
import json
import socket
import threading
from typing import Dict, Any, Optional
from datetime import datetime

from cli.cli import IntegratedCLI

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MainController:
    """Orchestrates the interaction between all system modules.

    This controller wraps the `IntegratedCLI` which already wires the
    blockchain, resource manager, consensus, authentication, and audit
    logger. The controller provides both a REPL and a socket API for
    long-running process interaction with persistent state.
    """

    def __init__(self, state_file: str = None, difficulty: int = 2):
        self.config: Dict[str, Any] = {}
        self.is_running = False
        self.cli = IntegratedCLI(difficulty=difficulty, state_file=state_file)
        self.socket_server: Optional[socket.socket] = None
        self.socket_thread: Optional[threading.Thread] = None

    def start(self):
        """Start the controller."""
        if self.is_running:
            return
        logger.info("Starting main controller. Use 'help' for commands.")
        self.is_running = True

    def stop(self):
        """Stop the controller and clean up resources."""
        if not self.is_running:
            return
        logger.info("Stopping main controller")
        if self.socket_server:
            self.stop_socket_api()
        self.is_running = False

    def handle_command(self, command_str: str) -> Dict[str, Any]:
        """Process a command string and return result as a dictionary.

        This method provides a unified interface for both REPL and socket API.
        Returns a dict with 'success', 'message', and optional 'data' fields.
        """
        parts = command_str.strip().split()
        if not parts:
            return {"success": False, "message": "Empty command"}

        cmd = parts[0].lower()

        try:
            if cmd == 'add_node':
                if len(parts) < 2:
                    return {"success": False, "message": "Usage: add_node <node_id> [cpu] [memory] [storage] [bandwidth]"}
                node_id = parts[1]
                cpu = float(parts[2]) if len(parts) > 2 else 0.0
                memory = float(parts[3]) if len(parts) > 3 else 0.0
                storage = float(parts[4]) if len(parts) > 4 else 0.0
                bandwidth = float(parts[5]) if len(parts) > 5 else 0.0
                quotas = {'CPU': cpu, 'Memory': memory, 'Storage': storage, 'Bandwidth': bandwidth}
                msg = self.cli.add_node(node_id, quotas)
                return {"success": True, "message": msg}

            elif cmd == 'request_resource':
                if len(parts) != 4:
                    return {"success": False, "message": "Usage: request_resource <node_id> <resource> <amount>"}
                node_id, resource, amount = parts[1], parts[2], float(parts[3])
                msg = self.cli.request_resource(node_id, resource, amount)
                node_status = self.cli.resource_manager.get_status()['nodes'].get(node_id)
                return {"success": True, "message": msg, "data": {"node_status": node_status}}

            elif cmd == 'release_resource':
                if len(parts) != 4:
                    return {"success": False, "message": "Usage: release_resource <node_id> <resource> <amount>"}
                node_id, resource, amount = parts[1], parts[2], float(parts[3])
                msg = self.cli.release_resource(node_id, resource, amount)
                node_status = self.cli.resource_manager.get_status()['nodes'].get(node_id)
                return {"success": True, "message": msg, "data": {"node_status": node_status}}

            elif cmd == 'view_chain':
                chain_data = self.cli.view_chain()
                return {"success": True, "message": "Blockchain retrieved", "data": {"chain": chain_data}}

            elif cmd == 'validate_chain':
                ok, reason = self.cli.validate_chain()
                return {"success": True, "message": reason, "data": {"valid": ok}}

            elif cmd == 'print_audit':
                from logger.audit_logger import get_events
                events = get_events()
                return {"success": True, "message": "Audit log retrieved", "data": {"events": events}}

            elif cmd == 'status':
                st = {
                    'time': datetime.now().isoformat(),
                    'nodes': list(self.cli.resource_manager.nodes.keys()),
                    'blocks': len(self.cli.blockchain.chain),
                    'difficulty': self.cli.blockchain.difficulty,
                }
                return {"success": True, "message": "System status", "data": st}

            elif cmd == 'help':
                help_text = """
Available commands:
  add_node <id> [cpu] [memory] [storage] [bandwidth] - Register a new node
  request_resource <id> <resource> <amount>          - Request resource allocation
  release_resource <id> <resource> <amount>          - Release allocated resource
  view_chain                                          - Display blockchain
  validate_chain                                      - Validate blockchain integrity
  print_audit                                         - Show audit log
  status                                              - Show system status
  help                                                - Show this help message
  exit/quit                                           - Exit the controller
"""
                return {"success": True, "message": help_text.strip()}

            else:
                return {"success": False, "message": f"Unknown command: {cmd}. Type 'help' for available commands."}

        except Exception as e:
            logger.exception(f"Error processing command: {command_str}")
            return {"success": False, "message": f"Error: {type(e).__name__}: {str(e)}"}

    def repl(self):
        """Simple interactive REPL that accepts commands.

        Commands include:
            add_node <id> [cpu] [memory] [storage] [bandwidth]
            request_resource <id> <resource> <amount>
            release_resource <id> <resource> <amount>
            view_chain
            validate_chain
            print_audit
            status
            help
            exit
        """
        self.start()
        print("\n=== Blockchain OS Controller (REPL Mode) ===")
        print("Type 'help' for available commands\n")

        try:
            while self.is_running:
                try:
                    raw = input("blockchain-os> ")
                except EOFError:
                    print()  # newline on Ctrl-D
                    break

                if not raw.strip():
                    continue

                cmd = raw.strip().split()[0].lower()
                if cmd in ('exit', 'quit'):
                    print('Exiting controller.')
                    break

                result = self.handle_command(raw)

                if result["success"]:
                    print(result["message"])
                    if "data" in result and cmd not in ('help', 'status'):
                        # For certain commands, show additional data
                        if cmd == 'view_chain':
                            self._pretty_print_chain(result["data"]["chain"])
                        elif cmd == 'print_audit':
                            self._pretty_print_audit(result["data"]["events"])
                        elif cmd in ('request_resource', 'release_resource'):
                            if "node_status" in result["data"]:
                                print(f"Node status: {result['data']['node_status']}")
                else:
                    print(f"ERROR: {result['message']}")

        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            self.stop()

    def _pretty_print_chain(self, chain_data):
        """Pretty print blockchain data."""
        print('\n==== Blockchain ====')
        for block in chain_data:
            print(f"\nBlock {block['index']} | timestamp={block['timestamp']:.3f}")
            print(f"  Hash: {block['hash']}")
            print(f"  Previous: {block['previous_hash']}")
            print(f"  Nonce: {block['nonce']}")
            txs = block.get('transactions', [])
            if txs:
                print(f"  Transactions ({len(txs)}):")
                for tx in txs:
                    print(f"    - {tx}")
            else:
                print("  (no transactions)")
        print('\n====================\n')

    def _pretty_print_audit(self, events):
        """Pretty print audit events."""
        print('\n==== Audit Log ====')
        for evt in events:
            ts = evt.get('timestamp', 0)
            node = evt.get('node_id', 'unknown')
            action = evt.get('action', 'unknown')
            outcome = evt.get('outcome', 'unknown')
            details = evt.get('details', {})
            print(f"[{ts:.3f}] {node} | {action} -> {outcome} | {details}")
        print('===================\n')

    # Socket API methods
    def start_socket_api(self, host: str = 'localhost', port: int = 9999):
        """Start a socket-based API server for programmatic access.

        The server accepts JSON commands and returns JSON responses.
        """
        if self.socket_server:
            logger.warning("Socket API already running")
            return

        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_server.bind((host, port))
        self.socket_server.listen(5)

        logger.info(f"Socket API listening on {host}:{port}")

        self.socket_thread = threading.Thread(target=self._socket_accept_loop, daemon=True)
        self.socket_thread.start()

    def _socket_accept_loop(self):
        """Accept incoming socket connections and handle them."""
        while self.is_running and self.socket_server:
            try:
                client_sock, addr = self.socket_server.accept()
                logger.info(f"Socket connection from {addr}")
                # Handle each client in a separate thread
                client_thread = threading.Thread(
                    target=self._handle_socket_client,
                    args=(client_sock, addr),
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                if self.is_running:
                    logger.error(f"Error accepting socket connection: {e}")
                break

    def _handle_socket_client(self, client_sock: socket.socket, addr):
        """Handle a single socket client connection."""
        try:
            with client_sock:
                while self.is_running:
                    # Read command (expect JSON with 'command' field)
                    data = client_sock.recv(4096)
                    if not data:
                        break

                    try:
                        request = json.loads(data.decode('utf-8'))
                        command = request.get('command', '')

                        result = self.handle_command(command)
                        response = json.dumps(result) + '\n'
                        client_sock.sendall(response.encode('utf-8'))

                    except json.JSONDecodeError:
                        error = {"success": False, "message": "Invalid JSON"}
                        client_sock.sendall((json.dumps(error) + '\n').encode('utf-8'))

        except Exception as e:
            logger.error(f"Error handling socket client {addr}: {e}")

    def stop_socket_api(self):
        """Stop the socket API server."""
        if self.socket_server:
            logger.info("Stopping socket API")
            try:
                self.socket_server.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")
            self.socket_server = None
            self.socket_thread = None


def main():
    """Main entry point for the controller.

    Supports both REPL and socket API modes.
    """
    parser = argparse.ArgumentParser(description='Main controller for blockchain-based distributed OS')
    parser.add_argument('--state-file', help='Path to state file (JSON)', default=None)
    parser.add_argument('--difficulty', type=int, default=2, help='Mining difficulty (leading zero hex digits)')
    parser.add_argument('--mode', choices=['repl', 'socket', 'both'], default='repl',
                       help='Operation mode: repl (interactive), socket (API server), or both')
    parser.add_argument('--host', default='localhost', help='Socket API host (default: localhost)')
    parser.add_argument('--port', type=int, default=9999, help='Socket API port (default: 9999)')

    args = parser.parse_args()

    controller = MainController(state_file=args.state_file, difficulty=args.difficulty)

    try:
        if args.mode == 'socket':
            # Socket-only mode
            controller.start()
            controller.start_socket_api(args.host, args.port)
            print(f"Socket API running on {args.host}:{args.port}")
            print("Press Ctrl+C to stop")
            # Keep running until interrupted
            try:
                while controller.is_running:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down...")

        elif args.mode == 'both':
            # Start socket API in background, then run REPL
            controller.start()
            controller.start_socket_api(args.host, args.port)
            print(f"Socket API running on {args.host}:{args.port}")
            controller.repl()

        else:
            # REPL only (default)
            controller.repl()

    finally:
        controller.stop()


if __name__ == '__main__':
    main()

