# Demo Troubleshooting Guide

## Common Issues and Solutions

### ❌ Issue 1: "Node does not have X resource allocated"

**Error Message:**
```
ValueError: Node alice does not have 1.0 CPU allocated
```

**Cause:**
You tried to release resources that weren't allocated to the node.

**Solution:**
1. Check what's actually allocated:
   ```
   status
   ```
   Look at the "Resource Utilization" section

2. Only release what's been allocated:
   ```
   request_resource alice CPU 2.0  # Allocate first
   release_resource alice CPU 1.0   # Then release (up to 2.0)
   ```

**Prevention:**
Always run `request_resource` BEFORE `release_resource` in your demo.

---

### ❌ Issue 2: "Node already exists"

**Error Message:**
```
ValueError: Node 'alice' already exists
```

**Cause:**
Trying to add a node that's already in the system (loaded from `system_state.json`).

**Solution:**
Clean the state file before starting:
```bash
rm -f system_state.json
python controller.py
```

**Prevention:**
Always run `rm -f system_state.json` before starting a fresh demo.

---

### ❌ Issue 3: Tests failing with "Node already exists"

**Cause:**
Tests are loading old state from `system_state.json`.

**Solution:**
Tests should use temporary directories (they already do in the fixed version).

If tests still fail:
```bash
rm -f system_state.json
pytest -q
```

---

### ❌ Issue 4: Blockchain starts with only 1 block after restart

**Cause:**
This is CORRECT behavior if you deleted `system_state.json` or ran `python main.py`.

**Understanding:**
- **Fresh start:** Always 1 block (genesis)
- **With persistence:** Same block count as before

**Solution:**
- For fresh demo: This is expected ✅
- To preserve blocks: Don't delete `system_state.json` between runs

---

### ❌ Issue 5: Consensus failing / Block rejected

**Possible Causes:**
1. Not enough nodes for majority
2. Invalid transaction
3. Resource quota exceeded

**Solution:**
Check the consensus output to see why votes were rejected.

Example debug:
```
add_node alice 4.0 8.0
request_resource alice CPU 10.0  # Too much! Quota is 4.0
# Will fail with quota exceeded error
```

Fix:
```
request_resource alice CPU 2.0  # Within quota
```

---

### ❌ Issue 6: "Unknown command" in REPL

**Cause:**
Typo in command or using wrong syntax.

**Solution:**
Use `help` to see available commands:
```
blockchain-os> help
```

Common typos:
- `add-node` ❌ → `add_node` ✅
- `requestresource` ❌ → `request_resource` ✅
- `viewchain` ❌ → `view_chain` ✅

---

### ❌ Issue 7: Import errors when running

**Error:**
```
ModuleNotFoundError: No module named 'cli'
```

**Cause:**
Not running from project directory or venv not activated.

**Solution:**
```bash
cd /home/fredyk/Documents/Projects/blockchain-os
source venv/bin/activate
python controller.py
```

---

### ❌ Issue 8: Tests not found

**Error:**
```
ERROR: file or directory not found: test
```

**Cause:**
Not in project root directory.

**Solution:**
```bash
cd /home/fredyk/Documents/Projects/blockchain-os
pytest -q
```

---

## 🎯 Quick Demo Reset

If anything goes wrong during your demo:

```bash
# Exit the REPL (if in it)
exit

# Clean state
rm -f system_state.json

# Restart fresh
python controller.py
```

---

## ✅ Pre-Demo Verification Checklist

Before presenting, verify everything works:

```bash
# 1. Clean state
rm -f system_state.json

# 2. Run tests
pytest -q
# Expected: 18 passed

# 3. Test main demo
python main.py > /dev/null 2>&1 && echo "✅ main.py works"

# 4. Test REPL
echo "status" | python controller.py > /dev/null 2>&1 && echo "✅ REPL works"

# 5. You're ready!
echo "🚀 System ready for demo!"
```

---

## 💡 Demo Best Practices

### DO:
✅ Always start with clean state (`rm -f system_state.json`)
✅ Request resources BEFORE releasing them
✅ Check `status` to see current allocations
✅ Use `help` if you forget a command
✅ Practice the demo once before presenting

### DON'T:
❌ Don't try to release unallocated resources
❌ Don't add duplicate nodes
❌ Don't skip the venv activation
❌ Don't exceed node quotas
❌ Don't run from wrong directory

---

## 🔍 Debugging Commands

If something seems wrong during demo:

```bash
# Check system status
status

# View blockchain
view_chain

# Validate chain integrity
validate_chain

# Check audit log
print_audit

# See available commands
help
```

---

## 📞 Emergency Recovery

If demo completely breaks:

```bash
# Kill any running processes
Ctrl+C

# Full reset
cd /home/fredyk/Documents/Projects/blockchain-os
rm -f system_state.json
source venv/bin/activate

# Verify tests still pass
pytest -q

# Restart demo
python controller.py
```

---

## 🎓 Common Questions from Audience

### Q: "Why did that command fail?"
**A:** Check the error message. Common reasons:
- Resource not allocated (can't release)
- Node already exists (clean state)
- Quota exceeded (request less)

### Q: "Can I undo a transaction?"
**A:** No - blockchain is immutable. But you can release resources to make them available again.

### Q: "What if I make a typo?"
**A:** Just type the command again correctly. The REPL will prompt you for the next command.

---

## ✅ Validation

After any fix, always validate:

```bash
pytest -q  # All tests should pass
```

If tests pass, your system is working correctly!

---

**Remember: Most issues are simple - wrong state, wrong order, or typos. Stay calm and follow this guide!** 🎯
