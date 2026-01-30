# Blockchain-Based Distributed Operating System

This repository contains a Python-based educational simulation of a blockchain-backed
distributed operating system. The goal is to demonstrate key OS concepts (resource
management, process coordination, authentication, auditing) combined with basic
blockchain ideas (blocks, hashing, immutability, consensus) in a small, easy-to-read
codebase suitable for classroom demos.

**Key Features:**
- ✅ **Persistent State**: All system state (nodes, blockchain, audit logs) is saved to JSON and survives restarts
- ✅ **Long-running Controller**: Interactive REPL and socket-based API for programmatic access
- ✅ **Atomic Persistence**: State writes are atomic to prevent corruption
- ✅ **Complete Test Suite**: Unit tests for core functionality, persistence, and orchestration

This is a single-process simulation (no real networking). The emphasis is on clarity,
readability, and teaching — not production readiness.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Usage Modes](#usage-modes)
- [How It Works](#how-it-works)
- [Testing](#testing)
- [Implementation Details](#implementation-details)
- [Limitations](#limitations)

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              MainController (Orchestrator)          │
│  - REPL Interface (Interactive CLI)                 │
│  - Socket API (Programmatic Access)                 │
│  - Persistence Management (JSON State)              │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │    IntegratedCLI          │
        │  (Component Coordinator)  │
        └─────────────┬─────────────┘
                      │
        ┌─────────────┴─────────────────────────────┐
        │                                           │
┌───────▼─────────┐  ┌──────────────┐  ┌──────────▼────────┐
│   Blockchain    │  │  Consensus   │  │ ResourceManager   │
│  - Blocks       │  │  - Voting    │  │  - Quotas         │
│  - Hashing      │  │  - Approval  │  │  - Allocations    │
│  - Validation   │  │              │  │                   │
└─────────────────┘  └──────────────┘  └───────────────────┘
        │                    │                    │
┌───────▼─────────┐  ┌──────▼───────┐  ┌────────▼──────────┐
│  Transactions   │  │  AuthManager │  │  AuditLogger      │
│  - Operations   │  │  - Tokens    │  │  - Event Log      │
└─────────────────┘  └──────────────┘  └───────────────────┘
                      │
              ┌───────▼────────┐
              │  Persistence   │
              │  (JSON State)  │
              └────────────────┘
```

## Project Structure

```
blockchain-os/
├── 📄 README.md                  # Main project documentation
├── 📄 requirements.txt           # Python dependencies
├── 🐍 main.py                    # Simple demo script
├── 🐍 controller.py              # MainController orchestrator (REPL + Socket API)
├── 🐍 persistence.py             # Atomic JSON save/load
│
├── 📦 core/                      # Core blockchain components
│   ├── blockchain.py             # Blockchain & Block classes
│   ├── node.py                   # Node entity (quotas, allocations)
│   ├── transaction.py            # Transaction class
│   └── __init__.py
│
├── 📦 cli/                       # Command-line interface
│   ├── cli.py                    # IntegratedCLI (component coordinator)
│   └── __init__.py
│
├── 📦 consensus/                 # Consensus mechanism
│   ├── consensus.py              # ConsensusEngine (majority voting)
│   └── __init__.py
│
├── 📦 resources/                 # Resource management
│   ├── resource_manager.py       # ResourceManager (allocation control)
│   └── __init__.py
│
├── 📦 auth/                      # Authentication
│   ├── auth.py                   # AuthManager (identity tokens)
│   └── __init__.py
│
├── 📦 logger/                    # Audit logging
│   ├── audit_logger.py           # Event logging utilities
│   └── __init__.py
│
├── 📁 test/                      # Test suite (17 tests)
│   ├── test_core.py              # Core blockchain/consensus tests
│   ├── test_persistence.py       # Persistence & orchestrator tests
│   └── test_basic_flow.py        # Integration tests
│
├── 📁 docs/                      # Documentation
│   ├── GETTING_STARTED.md        # Quick start guide (30 seconds)
│   ├── QUICKSTART.md             # Detailed usage guide
│   ├── IMPLEMENTATION_SUMMARY.md # Technical implementation details
│   └── PROJECT_STATUS.md         # Project completion report
│
├── 📁 scripts/                   # Utility scripts
│   ├── validate_all.sh           # Comprehensive system validation
│   ├── test_repl.sh              # REPL functionality testing
│   └── cleanup_project.sh        # Project cleanup utility
│
└── 📁 examples/                  # Usage examples
    └── socket_client_example.py  # Socket API client demonstration
```

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

### 1. Simple Demo (One-shot)

Run the built-in demo that shows all features in a single process:

```bash
python3 main.py
```

This demonstrates:
- Node creation
- Resource allocation/release
- Blockchain mining and validation
- Consensus voting
- Audit logging

### 2. Interactive REPL (Recommended)

Start the long-running controller with persistent state:

```bash
python3 controller.py
```

This starts an interactive shell where you can execute commands:

```
=== Blockchain OS Controller (REPL Mode) ===
Type 'help' for available commands

blockchain-os> help
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

blockchain-os> add_node node1 4.0 8.0
Node 'node1' added. Token: a1b2c3...

blockchain-os> add_node node2 4.0 8.0
Node 'node2' added. Token: d4e5f6...

blockchain-os> request_resource node1 CPU 2.0
[Consensus voting process shown...]
Allocation accepted and committed in block 1 (hash=0012ab...)
Node status: {'node_id': 'node1', 'quotas': {'CPU': 4.0, ...}, 'allocated': {'CPU': 2.0}}

blockchain-os> status
{'time': '2026-01-30T10:30:45', 'nodes': ['node1', 'node2'], 'blocks': 2, 'difficulty': 2}

blockchain-os> exit
```

**State is automatically saved to `system_state.json` after every operation!**

### 3. Socket API Mode (Programmatic Access)

Start the controller as a background server:

```bash
python3 controller.py --mode socket --port 9999
```

Then connect from another terminal or application:

```python
import socket
import json

# Connect to controller
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 9999))

# Send command
request = json.dumps({"command": "status"})
sock.sendall(request.encode('utf-8'))

# Receive response
response = json.loads(sock.recv(4096).decode('utf-8'))
print(response)
# {'success': True, 'message': 'System status', 'data': {...}}

sock.close()
```

### 4. Combined Mode (REPL + Socket API)

Run both interfaces simultaneously:

```bash
python3 controller.py --mode both --port 9999
```

## Usage Modes

### Command-Line Arguments

```bash
python3 controller.py [OPTIONS]

Options:
  --state-file PATH       Path to JSON state file (default: system_state.json)
  --difficulty N          Mining difficulty (leading zeros, default: 2)
  --mode MODE            Operation mode: repl, socket, or both (default: repl)
  --host HOST            Socket API host (default: localhost)
  --port PORT            Socket API port (default: 9999)
```

### Available Commands

All commands work in both REPL and Socket API modes:

#### Node Management
```bash
add_node <node_id> [cpu] [memory] [storage] [bandwidth]
# Example: add_node node1 4.0 8.0 16.0 10.0
```

#### Resource Operations
```bash
request_resource <node_id> <resource> <amount>
# Example: request_resource node1 CPU 2.0

release_resource <node_id> <resource> <amount>
# Example: release_resource node1 CPU 1.0
```

**Supported resources:** CPU, Memory, Storage, Bandwidth

#### Blockchain Operations
```bash
view_chain          # Display all blocks
validate_chain      # Verify blockchain integrity
```

#### System Information
```bash
status              # Show system state
print_audit         # Show audit log
help                # List all commands
```

## How It Works

### Blockchain Implementation

#### 1. Block Structure

Each block contains:
- **Index**: Position in chain (0 = genesis)
- **Timestamp**: Creation time
- **Transactions**: List of OS operations
- **Previous Hash**: Link to parent block
- **Nonce**: Proof-of-work value
- **Hash**: SHA-256 of block contents

```python
{
  "index": 1,
  "timestamp": 1706612345.678,
  "transactions": [
    {"node_id": "node1", "resource_type": "CPU", "amount": 2.0, ...}
  ],
  "previous_hash": "0012abc...",
  "nonce": 42,
  "hash": "0034def..."
}
```

#### 2. Hashing & Immutability

- Each block's hash is computed from ALL its contents
- Changing ANY field breaks the hash
- Each block stores the previous block's hash
- Tampering with an old block invalidates all subsequent blocks

```python
# Block hash includes:
SHA-256(index + timestamp + transactions + previous_hash + nonce)
```

#### 3. Proof-of-Work (Mining)

Simple PoW requires finding a nonce that produces a hash with N leading zeros:

```python
# Difficulty = 2 means hash must start with "00"
while not hash.startswith("00"):
    nonce += 1
    hash = compute_hash(block)
```

This makes tampering computationally expensive.

#### 4. Chain Validation

The `validate_chain` command:
1. Recomputes each block's hash
2. Verifies it matches the stored hash
3. Checks each block links to its parent
4. Ensures no gaps or tampering

### Operating System Concepts

#### 1. Resource Management

Nodes have **quotas** (limits) and **allocations** (current usage):

```python
node = {
  "node_id": "node1",
  "quotas": {"CPU": 4.0, "Memory": 8.0},
  "allocated": {"CPU": 2.0, "Memory": 0.0}
}
```

Resource requests are validated:
- ✅ Amount > 0
- ✅ New allocation ≤ quota
- ❌ Reject if would exceed quota

#### 2. Consensus (Distributed Agreement)

When a transaction is proposed:
1. **Proposal**: Block is created with transaction
2. **Broadcast**: All nodes receive the block
3. **Voting**: Each node validates and votes
4. **Consensus**: Block accepted if **majority approves**
5. **Commit**: Resource allocation applied and block added to chain

```
Proposed Block → [Node1: APPROVE] [Node2: APPROVE] [Node3: REJECT]
Result: 2/3 = Majority → Block ACCEPTED
```

#### 3. Authentication

Each node receives a unique token on creation:

```python
token = SHA-256(node_id + secret)
```

Tokens verify node identity before allowing operations.

#### 4. Audit Logging

All operations are logged with:
- Timestamp
- Node ID
- Action (add_node, request_resource, etc.)
- Outcome (accepted/rejected)
- Details

Logs are stored in-memory AND persisted to JSON.

### Persistence Architecture

#### Atomic Writes

State is saved atomically to prevent corruption:

```python
1. Write to temporary file: .tmp_state_XXXXX.json
2. Atomic rename: .tmp_state_XXXXX.json → system_state.json
```

If the process crashes during write, the temp file is discarded and the original state remains intact.

#### State Contents

The JSON file contains:

```json
{
  "nodes": [
    {"node_id": "node1", "quotas": {...}, "allocated": {...}}
  ],
  "chain": [
    {"index": 0, "hash": "genesis", ...},
    {"index": 1, "hash": "0012ab...", ...}
  ],
  "audit_events": [
    {"timestamp": 123.45, "node_id": "node1", "action": "add_node", ...}
  ]
}
```

#### Auto-Save Behavior

State is automatically saved after:
- ✅ Adding a node
- ✅ Successful resource allocation
- ✅ Successful resource release
- ✅ Any blockchain modification

No manual save command needed!

## Testing

### Run All Tests

```bash
pytest -v
```

### Run Specific Test Suites

```bash
# Core blockchain/consensus tests
pytest test/test_core.py -v

# Persistence & orchestrator tests
pytest test/test_persistence.py -v
```

### Test Coverage

The test suite verifies:

✅ **Blockchain tampering detection**
✅ **Consensus majority voting**
✅ **Resource allocation/release rules**
✅ **Atomic persistence (crash safety)**
✅ **State recovery after restart**
✅ **Orchestrator command handling**
✅ **Socket API basic functionality**
✅ **Audit log persistence**

## Implementation Details

### Component Responsibilities

| Component | File | Purpose |
|-----------|------|---------|
| **MainController** | `controller.py` | Orchestrates all modules, provides REPL & Socket API |
| **IntegratedCLI** | `cli/cli.py` | Coordinates blockchain, consensus, resources, auth |
| **Blockchain** | `core/blockchain.py` | Block creation, hashing, chain validation |
| **Node** | `core/node.py` | Node entity with quotas and allocations |
| **Transaction** | `core/transaction.py` | Represents OS operations |
| **ConsensusEngine** | `consensus/consensus.py` | Simulated majority voting |
| **ResourceManager** | `resources/resource_manager.py` | Enforces allocation rules |
| **AuthManager** | `auth/auth.py` | Issues and verifies node tokens |
| **AuditLogger** | `logger/audit_logger.py` | Records system events |
| **Persistence** | `persistence.py` | Atomic JSON save/load |

### Design Patterns

- **Orchestrator Pattern**: MainController coordinates all components
- **Atomic Operations**: State changes are all-or-nothing
- **Command Pattern**: Commands abstracted for REPL and Socket API
- **Persistence Pattern**: Automatic save after state-changing operations

### Code Quality

- ✅ Clear separation of concerns
- ✅ Comprehensive docstrings
- ✅ Type hints where applicable
- ✅ Educational comments
- ✅ Error handling with meaningful messages
- ✅ Test coverage for critical paths

## Limitations

### Educational Scope

This is an **educational demonstration**, not production software:

- **Single-process**: All nodes simulated in one Python process
- **No networking**: Communication is in-memory method calls
- **Simple consensus**: Deterministic voting, no Byzantine fault tolerance
- **Basic auth**: Tokens are for demo only, not cryptographically secure
- **Low difficulty**: PoW set to 2 leading zeros (fast for demos)
- **No concurrency**: Single-threaded execution

### What This Project Demonstrates

✅ How blockchain provides immutability  
✅ How consensus enables distributed agreement  
✅ How OS resources can be managed via blockchain  
✅ How audit logs provide accountability  
✅ How persistence enables long-running systems  

### What This Project Does NOT Do

❌ Real peer-to-peer networking  
❌ Byzantine fault tolerance  
❌ Production-grade security  
❌ High-performance implementation  
❌ Advanced consensus algorithms (PBFT, Raft, etc.)  

## Academic Context

This project demonstrates the following OS and distributed systems concepts:

1. **Resource Management**: CPU, memory, storage allocation with quotas
2. **Process Coordination**: Consensus-based decision making
3. **Security**: Authentication tokens and access control
4. **Auditing**: Immutable logs via blockchain
5. **Persistence**: State management and crash recovery
6. **Distributed Agreement**: Majority voting consensus

## Future Enhancements

Possible extensions for advanced students:

- [ ] Real network communication (sockets/HTTP)
- [ ] Multiple processes/containers as separate nodes
- [ ] Advanced consensus (PBFT, Raft)
- [ ] Smart contracts for resource policies
- [ ] Merkle trees for efficient validation
- [ ] Block compression and pruning
- [ ] Web-based UI dashboard
- [ ] Metrics and monitoring

## Authors & Contact

**Group 49 - DCIT 301 Operating Systems Fundamentals**  
University of Ghana, 2025/2026

### Component Authors
- **CLI Interface**: Frederick Kwaku Kankam (22015587)
- **Node Management**: Kwesi Adom
- **Transaction Module**: Idan
- **Blockchain Core**: (Multiple contributors)
- **Consensus Module**: Shadrack
- **Resource Management**: Shadrack
- **Authentication**: (Multiple contributors)
- **Audit Logger**: Daniel
- **Main Controller**: Selina Adu

## License & Safety

This code is provided for **teaching and demonstration only**.

⚠️ **DO NOT USE** the authentication, consensus, or blockchain code in production systems.

⚠️ This implementation prioritizes clarity over security and performance.

---

**Enjoy exploring blockchain-based operating systems!**

For questions or issues, please consult your course instructor.
