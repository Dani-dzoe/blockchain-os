# 🚀 Getting Started (30 seconds)

## TL;DR - Run the Demo Now

```bash
cd /home/fredyk/Documents/Projects/blockchain-os
source venv/bin/activate  # If not already activated
python main.py
```

That's it! You'll see a complete demonstration of the blockchain-based OS.

---

## Want Interactive Mode?

```bash
python controller.py
```

Then try these commands:
```
add_node alice 4.0 8.0
add_node bob 4.0 8.0
request_resource alice CPU 2.0
view_chain
validate_chain
status
exit
```

Your state is automatically saved to `system_state.json`!

---

## Need More Info?

- **Full Documentation**: See [README.md](README.md)
- **Quick Reference**: See [QUICKSTART.md](QUICKSTART.md)
- **Implementation Details**: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Project Status**: See [PROJECT_STATUS.md](PROJECT_STATUS.md)

---

## Run Tests

```bash
pytest -v
```

Expected: **17 passed** ✅

---

## Validate Everything

```bash
./validate_all.sh
```

This comprehensive script tests all features automatically.

---

## Architecture at a Glance

```
User Commands
     ↓
MainController (controller.py)
     ↓
IntegratedCLI (cli/cli.py)
     ↓
┌────────┬───────────┬─────────────┬──────┐
│Blockchain│Consensus│ResourceMgr│Auth│
└────────┴───────────┴─────────────┴──────┘
     ↓
Persistence (system_state.json)
```

---

## Key Features

✓ **Blockchain**: Immutable ledger with proof-of-work  
✓ **Consensus**: Majority voting for block approval  
✓ **Resources**: CPU, Memory, Storage, Bandwidth management  
✓ **Persistence**: Automatic state save/load (crash-safe)  
✓ **Testing**: 17 comprehensive tests  

---

## Need Help?

1. Check error messages (they're descriptive)
2. Read [QUICKSTART.md](QUICKSTART.md)
3. Run `./validate_all.sh` to diagnose issues
4. Consult your course instructor

---

**Ready to explore! 🎉**
