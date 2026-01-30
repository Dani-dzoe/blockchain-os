# Blockchain OS - Quick Start Guide

## Installation

```bash
# Clone or navigate to the project
cd /home/fredyk/Documents/Projects/blockchain-os

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install pytest
```

## Usage Examples

### 1. Quick Demo (One-Shot)

Run the built-in demo to see all features:

```bash
python main.py
```

This demonstrates:
- Node creation
- Resource allocation/release  
- Blockchain mining with proof-of-work
- Consensus voting
- Chain validation
- Audit logging

### 2. Interactive REPL (Persistent State)

Start the controller for interactive use:

```bash
python controller.py
```

Example session:

```
blockchain-os> add_node node1 4.0 8.0 16.0 10.0
Node 'node1' added. Token: bb8c92ec...

blockchain-os> add_node node2 4.0 8.0 16.0 10.0
Node 'node2' added. Token: 1279ab47...

blockchain-os> request_resource node1 CPU 2.0
[Consensus voting shown...]
Allocation accepted and committed in block 1

blockchain-os> status
{'time': '2026-01-30T18:31:02', 'nodes': ['node1', 'node2'], 'blocks': 2, 'difficulty': 2}

blockchain-os> view_chain
[Displays full blockchain with all blocks]

blockchain-os> validate_chain
Chain is valid

blockchain-os> print_audit
[Shows all audit events]

blockchain-os> exit
```

**State is automatically saved to `system_state.json`!**

### 3. Socket API (Programmatic Access)

Start controller as a server:

```bash
python controller.py --mode socket --port 9999
```

Connect from Python:

```python
import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 9999))

# Add node
request = json.dumps({"command": "add_node node1 4.0 8.0"})
sock.sendall(request.encode('utf-8'))
response = json.loads(sock.recv(4096).decode('utf-8'))
print(response)

# Check status
request = json.dumps({"command": "status"})
sock.sendall(request.encode('utf-8'))
response = json.loads(sock.recv(4096).decode('utf-8'))
print(response['data'])

sock.close()
```

### 4. Combined Mode (REPL + Socket API)

Run both interfaces simultaneously:

```bash
python controller.py --mode both --port 9999
```

Use the REPL interactively while allowing programmatic access via socket.

## Testing

Run all tests:

```bash
pytest -v
```

Run specific test suites:

```bash
# Core blockchain/consensus tests
pytest test/test_core.py -v

# Persistence and orchestrator tests
pytest test/test_persistence.py -v
```

## Available Commands

### Node Management
- `add_node <id> [cpu] [memory] [storage] [bandwidth]` - Create a node
  - Example: `add_node node1 4.0 8.0 16.0 10.0`

### Resource Operations
- `request_resource <id> <resource> <amount>` - Allocate resource
  - Example: `request_resource node1 CPU 2.0`
  - Resources: CPU, Memory, Storage, Bandwidth
  
- `release_resource <id> <resource> <amount>` - Release resource
  - Example: `release_resource node1 CPU 1.0`

### Blockchain Operations
- `view_chain` - Display all blocks in the blockchain
- `validate_chain` - Verify blockchain integrity

### System Information
- `status` - Show system state (nodes, blocks, difficulty)
- `print_audit` - Display audit log of all operations
- `help` - List all commands

## Command-Line Options

```bash
python controller.py [OPTIONS]

Options:
  --state-file PATH    Path to JSON state file (default: system_state.json)
  --difficulty N       Mining difficulty, 0-10 (default: 2)
  --mode MODE         Operation mode: repl, socket, or both (default: repl)
  --host HOST         Socket API host (default: localhost)
  --port PORT         Socket API port (default: 9999)
```

Examples:

```bash
# Custom state file
python controller.py --state-file my_state.json

# Higher difficulty (more mining work)
python controller.py --difficulty 4

# Socket-only mode
python controller.py --mode socket --port 8888

# Combined mode with custom settings
python controller.py --mode both --difficulty 3 --port 9999
```

## Understanding the Output

### Consensus Voting

When you request resources, you'll see consensus voting:

```
======================================================================
[CONSENSUS REQUEST INITIATED]
  Block Index: 1
  Block Hash: 002d8004...
  Transactions: 1
======================================================================

[STEP 1: PRE-VALIDATION]
  ✓ Block passed pre-validation

[STEP 2: COLLECTING VOTES]
  ✓ node1: APPROVE
  ✓ node2: APPROVE

[STEP 3: VOTE COUNTING]
  Votes FOR:     2
  Votes AGAINST: 0
  Abstentions:   0
  Total Votes:   2

[STEP 4: CONSENSUS DECISION]
  Required for Approval: 2
  Received:              2
  ✓ CONSENSUS REACHED - Block ACCEPTED
======================================================================
```

This shows:
1. **Pre-validation**: Block structure is valid
2. **Voting**: Each node votes APPROVE/REJECT
3. **Counting**: Tally votes
4. **Decision**: Majority determines acceptance

### Blockchain Display

When you run `view_chain`, you'll see:

```
==== Blockchain ====

Block 0 | timestamp=1769797862.948
  Hash: 00c4ce74d5f3aff833ab62768063d233f6e686ceea961543ceac16a0977c408a
  Previous: 0
  Nonce: 76
  (no transactions - genesis block)

Block 1 | timestamp=1769797862.950
  Hash: 002d80045fd94d48e04f59b11396d9a7e0acc893bd52dda826b6b60ad38542af
  Previous: 00c4ce74d5f3aff833ab62768063d233f6e686ceea961543ceac16a0977c408a
  Nonce: 452
  Transactions (1):
    - {'node_id': 'node1', 'resource_type': 'CPU', 'amount': 2.0, ...}
```

Each block shows:
- **Index**: Position in chain
- **Hash**: Block's unique identifier (starts with 00 due to PoW)
- **Previous**: Links to parent block (creates chain)
- **Nonce**: Proof-of-work value
- **Transactions**: Operations in this block

### State Persistence

The `system_state.json` file contains:

```json
{
  "nodes": [
    {
      "node_id": "node1",
      "quotas": {"CPU": 4.0, "Memory": 8.0, ...},
      "allocated": {"CPU": 2.0, "Memory": 0.0, ...},
      "status": "active"
    }
  ],
  "chain": [
    {"index": 0, "hash": "00c4ce...", ...},
    {"index": 1, "hash": "002d80...", ...}
  ],
  "audit_events": [
    {"timestamp": 1769797862.948, "node_id": "node1", ...}
  ]
}
```

This file is:
- **Automatically saved** after every operation
- **Atomically written** (crash-safe)
- **Loaded on startup** (persistent across restarts)

## Troubleshooting

### "No module named pytest"
```bash
source venv/bin/activate
pip install pytest
```

### "Permission denied" when running scripts
```bash
chmod +x script.sh
```

### State file corruption
Delete `system_state.json` to start fresh:
```bash
rm system_state.json
```

### Socket API connection refused
Make sure controller is running in socket mode:
```bash
python controller.py --mode socket --port 9999
```

## Architecture Overview

```
MainController (controller.py)
├── REPL Interface
├── Socket API
└── IntegratedCLI (cli/cli.py)
    ├── Blockchain (core/blockchain.py)
    ├── ConsensusEngine (consensus/consensus.py)
    ├── ResourceManager (resources/resource_manager.py)
    ├── AuthManager (auth/auth.py)
    ├── AuditLogger (logger/audit_logger.py)
    └── Persistence (persistence.py)
```

## Next Steps

1. **Explore the code**: All modules are well-documented
2. **Run tests**: `pytest -v` to see comprehensive test coverage
3. **Experiment**: Try different difficulty levels, create multiple nodes
4. **Extend**: Add new resource types, implement custom consensus rules
5. **Document**: Use for your course project presentation

## Key Features Demonstrated

✅ Blockchain immutability via cryptographic hashing  
✅ Proof-of-work mining (adjustable difficulty)  
✅ Distributed consensus (majority voting)  
✅ Resource management (quotas and allocations)  
✅ Authentication (node tokens)  
✅ Audit logging (immutable event trail)  
✅ State persistence (JSON, atomic writes)  
✅ Long-running orchestrator (REPL + Socket API)  
✅ Comprehensive test suite (17 tests)  

---

**Ready to explore blockchain-based operating systems!** 🚀
