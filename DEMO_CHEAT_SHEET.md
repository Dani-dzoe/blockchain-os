# 🎬 Demo Cheat Sheet - Quick Reference

## ⚠️ IMPORTANT: Blockchain Always Starts with 1 Block!

**This is CORRECT behavior:**
- Fresh start = 1 block (genesis block)
- Blocks increase as you add operations
- `main.py` always fresh (deletes state)
- `controller.py` loads saved state

**Block count progression:**
1. Genesis: 1 block
2. Add alice: 2 blocks
3. Add bob: 3 blocks
4. Allocate: 4 blocks

---

## ⚡ Pre-Demo Setup (30 seconds)

```bash
cd /home/fredyk/Documents/Projects/blockchain-os
source venv/bin/activate
rm -f system_state.json  # Always start fresh for consistent demo
pytest -q  # Verify tests pass
```

---

## 📋 Demo Sequence

### 1️⃣ Quick Demo (3 min)
```bash
python main.py
```
**Show:** Node creation → Consensus → Mining → Validation → Audit

---

### 2️⃣ Interactive REPL (8 min)
```bash
python controller.py
```

**Commands to run:**
```
add_node alice 4.0 8.0 16.0 10.0
add_node bob 6.0 16.0 32.0 20.0
add_node charlie 2.0 4.0 8.0 5.0

request_resource alice CPU 2.0
request_resource bob Memory 8.0
request_resource charlie Storage 4.0

status
view_chain
validate_chain
print_audit

release_resource alice CPU 1.0  # Must request BEFORE releasing!

exit
```

**⚠️ Important:** You can only release resources that have been allocated!
- alice has 2.0 CPU → Can release up to 2.0
- bob has 8.0 Memory → Can release up to 8.0
view_chain
validate_chain
print_audit

release_resource alice CPU 1.0

exit
```

---

### 3️⃣ Persistence Demo (2 min)
```bash
ls -lh system_state.json
cat system_state.json | head -n 30

python controller.py
# In REPL:
status
view_chain
exit
```

---

### 4️⃣ Tamper Detection (3 min)
```bash
python
```

```python
import json
with open('system_state.json', 'r') as f:
    state = json.load(f)
state['chain'][1]['transactions'][0]['amount'] = 999.0
with open('system_state.json', 'w') as f:
    json.dump(state, f, indent=2)
exit()
```

```bash
python controller.py
# In REPL:
validate_chain  # Shows INVALID!
exit
```

---

### 5️⃣ Test Suite (2 min)
```bash
rm system_state.json
pytest -v
```
**Expected:** 18 passed

---

### 6️⃣ Socket API (Optional - 2 min)
**Terminal 1:**
```bash
python controller.py --mode socket --port 9999
```

**Terminal 2:**
```bash
python examples/socket_client_example.py
```

---

## 🎯 Key Points to Emphasize

### Blockchain
- ✅ SHA-256 hashing
- ✅ Proof-of-work mining
- ✅ Immutable chain
- ✅ Tamper detection

### Consensus
- ✅ Majority voting
- ✅ All nodes participate
- ✅ Democratic approval

### Resources
- ✅ Quotas enforced
- ✅ Allocation tracking
- ✅ Release capability

### Persistence
- ✅ Atomic writes
- ✅ Auto-save/load
- ✅ Crash-safe

---

## 💬 Key Phrases

**Opening:**
> "Blockchain-based distributed OS combining blockchain immutability with OS resource management"

**Consensus:**
> "Watch all nodes vote - majority rule ensures distributed agreement"

**Blockchain:**
> "Each block cryptographically linked - tampering breaks the chain"

**Persistence:**
> "Atomic writes ensure crash safety - state survives restarts"

**Tests:**
> "18 comprehensive tests verify all components work correctly"

---

## ⏱️ Timing

| Section | Time |
|---------|------|
| Intro | 2 min |
| Quick demo | 3 min |
| REPL | 8 min |
| Persistence | 2 min |
| Tamper | 3 min |
| Tests | 2 min |
| **Total** | **20 min** |

---

## 🎓 Achievements to Highlight

- ✅ 18 passing tests
- ✅ 3,500+ lines of code
- ✅ 7 documentation files
- ✅ 10 integrated modules
- ✅ Production-quality patterns
- ✅ Complete persistence
- ✅ Atomic operations
- ✅ Socket API

---

## 📞 Emergency Commands

**If something breaks:**
```bash
# Clean state and restart
rm -f system_state.json
pytest -q  # Verify system
python main.py  # Fallback demo
```

**If stuck in REPL:**
```
exit
# or Ctrl+D
```

**If process hangs:**
```
Ctrl+C
```

---

## ✅ Post-Demo

```bash
rm -f system_state.json
deactivate
```

---

**Print this and keep it handy during the demo!**
