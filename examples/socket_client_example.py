#!/usr/bin/env python3
"""
Socket API Client Example

This script demonstrates how to interact with the blockchain OS controller
via the socket API.

Usage:
    1. Start controller: python controller.py --mode socket --port 9999
    2. Run this client: python socket_client_example.py
"""

import socket
import json
import time


class BlockchainOSClient:
    """Simple client for the Blockchain OS socket API."""

    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        """Connect to the controller."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"✓ Connected to {self.host}:{self.port}")

    def disconnect(self):
        """Disconnect from the controller."""
        if self.sock:
            self.sock.close()
            self.sock = None
            print("✓ Disconnected")

    def send_command(self, command):
        """Send a command and receive response."""
        request = json.dumps({"command": command})
        self.sock.sendall(request.encode('utf-8'))

        response_data = self.sock.recv(4096)
        response = json.loads(response_data.decode('utf-8'))

        return response

    def print_response(self, response):
        """Pretty print a response."""
        if response['success']:
            print(f"✓ {response['message']}")
            if 'data' in response:
                print(f"  Data: {json.dumps(response['data'], indent=2)}")
        else:
            print(f"✗ {response['message']}")


def main():
    """Demo the socket API client."""
    print("=" * 60)
    print("Blockchain OS - Socket API Client Demo")
    print("=" * 60)
    print()

    client = BlockchainOSClient(host='localhost', port=9999)

    try:
        # Connect
        print("[1] Connecting to controller...")
        client.connect()
        print()

        # Get initial status
        print("[2] Getting system status...")
        response = client.send_command("status")
        client.print_response(response)
        print()

        # Add nodes
        print("[3] Adding nodes...")
        response = client.send_command("add_node node1 4.0 8.0 16.0 10.0")
        client.print_response(response)

        response = client.send_command("add_node node2 4.0 8.0 16.0 10.0")
        client.print_response(response)
        print()

        # Request resource
        print("[4] Requesting resource allocation...")
        response = client.send_command("request_resource node1 CPU 2.0")
        client.print_response(response)
        print()

        # Get updated status
        print("[5] Getting updated system status...")
        response = client.send_command("status")
        client.print_response(response)
        print()

        # Validate chain
        print("[6] Validating blockchain...")
        response = client.send_command("validate_chain")
        client.print_response(response)
        print()

        # View chain
        print("[7] Viewing blockchain...")
        response = client.send_command("view_chain")
        if response['success']:
            chain = response['data']['chain']
            print(f"✓ Blockchain has {len(chain)} blocks")
            for block in chain:
                print(f"  Block {block['index']}: hash={block['hash'][:16]}... "
                      f"txs={len(block['transactions'])}")
        print()

        # Print audit log
        print("[8] Retrieving audit log...")
        response = client.send_command("print_audit")
        if response['success']:
            events = response['data']['events']
            print(f"✓ Audit log has {len(events)} events")
            for evt in events[:3]:  # Show first 3
                print(f"  [{evt['timestamp']:.2f}] {evt['node_id']}: "
                      f"{evt['action']} -> {evt['outcome']}")
        print()

        print("=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)

    except ConnectionRefusedError:
        print()
        print("✗ Connection refused!")
        print()
        print("Please start the controller first:")
        print("  python controller.py --mode socket --port 9999")
        print()
        return 1

    except Exception as e:
        print(f"✗ Error: {e}")
        return 1

    finally:
        client.disconnect()

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
