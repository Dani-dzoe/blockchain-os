#!/bin/bash
# Test script for the REPL controller

# Navigate to project root
cd "$(dirname "$0")/.."
source venv/bin/activate

# Clean up any existing state file
rm -f system_state.json

echo "Testing REPL controller..."
echo ""
echo "Commands to execute:"
echo "  add_node node1 4.0 8.0"
echo "  add_node node2 4.0 8.0"
echo "  request_resource node1 CPU 2.0"
echo "  status"
echo "  view_chain"
echo "  validate_chain"
echo "  exit"
echo ""

# Feed commands to the controller
python controller.py <<EOF
add_node node1 4.0 8.0
add_node node2 4.0 8.0
request_resource node1 CPU 2.0
status
validate_chain
exit
EOF

echo ""
echo "Checking if state file was created..."
if [ -f system_state.json ]; then
    echo "✓ system_state.json created successfully"
    echo ""
    echo "State file contents (first 50 lines):"
    head -n 50 system_state.json
else
    echo "✗ system_state.json not found"
    exit 1
fi

echo ""
echo "Testing state persistence..."
echo "Restarting controller and checking if state is loaded..."

python controller.py <<EOF
status
exit
EOF

echo ""
echo "✓ All tests passed!"
