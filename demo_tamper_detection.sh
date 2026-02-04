#!/bin/bash
# Automated Tamper Detection Demo Script
# Run this to demonstrate the security features of the blockchain OS

set -e

REPO_DIR="/home/fredyk/Documents/Projects/blockchain-os"
cd "$REPO_DIR"

echo "════════════════════════════════════════════════════════════════"
echo "    BLOCKCHAIN OS - SECURITY & TAMPER DETECTION DEMO"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Step 1: Clean state
echo "[STEP 1] Creating clean system state..."
rm -f system_state.json
echo "✓ Previous state cleared"
echo ""

# Step 2: Create initial state
echo "[STEP 2] Creating legitimate blockchain..."
python3 controller.py << 'STEP2_COMMANDS'
add_node alice 4.0 8.0
add_node bob 4.0 8.0
request_resource alice CPU 2.0
request_resource bob Memory 4.0
validate_chain
exit
STEP2_COMMANDS
echo "✓ Blockchain created with 5 blocks"
echo ""

# Step 3: Display state before tampering
echo "[STEP 3] State BEFORE tampering:"
python3 << 'STEP3_COMMANDS'
import json
with open('system_state.json', 'r') as f:
    data = json.load(f)
print(f"  Alice's CPU allocation: {data['nodes'][0]['allocated']['CPU']}")
print(f"  File checksum: {data['checksum'][:16]}...")
print(f"  Total blocks: {len(data['chain'])}")
STEP3_COMMANDS
echo ""

# Step 4: Tamper with the file
echo "[STEP 4] TAMPERING WITH FILE..."
python3 << 'STEP4_COMMANDS'
import json
with open('system_state.json', 'r') as f:
    data = json.load(f)

# Save original checksum
original_checksum = data['checksum']

# Tamper: Change alice's CPU from 2.0 to 999.0
data['nodes'][0]['allocated']['CPU'] = 999.0
print(f"  ✓ Changed alice's CPU allocation from 2.0 to 999.0")

# Save with OLD/WRONG checksum
with open('system_state.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"  ✓ Kept original checksum (NOT updating it)")
print(f"    Stored:   {original_checksum[:16]}...")
print(f"  ✓ File saved - tampering complete!")
STEP4_COMMANDS
echo ""

# Step 5: State after tampering (file-level)
echo "[STEP 5] State AFTER tampering (file-level check):"
python3 << 'STEP5_COMMANDS'
import json
with open('system_state.json', 'r') as f:
    data = json.load(f)
print(f"  Alice's CPU allocation: {data['nodes'][0]['allocated']['CPU']} ❌ CHANGED!")
print(f"  File checksum (OLD):    {data['checksum'][:16]}...")
STEP5_COMMANDS
echo ""

# Step 6: Restart system and detect tampering
echo "[STEP 6] RESTARTING SYSTEM (tampering detection)..."
echo ""
python3 controller.py << 'STEP6_COMMANDS'
validate_chain
exit
STEP6_COMMANDS
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "                     DEMO COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✅ What was demonstrated:"
echo "   1. Created legitimate blockchain with 2 nodes and 2 transactions"
echo "   2. Validated the blockchain (showed ✅ Chain is valid)"
echo "   3. Manually edited system_state.json to change alice's CPU"
echo "   4. Restarted the system"
echo "   5. System DETECTED the tampering on startup:"
echo "      - File integrity check FAILED"
echo "      - Checksum mismatch detected"
echo "      - Validate_chain command reported tampering"
echo ""
echo "🔒 Security features demonstrated:"
echo "   • SHA-256 checksum detects file modifications"
echo "   • Blockchain hashing prevents transaction tampering"
echo "   • Immutable audit trail"
echo "   • Multi-layer defense (checksum + blockchain + consensus)"
echo ""
echo "════════════════════════════════════════════════════════════════"
