================

System Logger & Audit Module for the Blockchain-Based Distributed OS.

PURPOSE:
--------
This module records important system events such as:
- Node creation
- Resource requests
- Resource releases
- Consensus outcomes
- Blockchain updates

WHY AUDITING MATTERS:
---------------------
In a traditional operating system, logs help administrators debug issues.
In a blockchain-based OS, logs serve an even bigger purpose:

1. Accountability:
   Every action is tied to a node ID and timestamp.

2. Transparency:
   Actions can be reviewed later to understand system behavior.

3. Security:
   Suspicious or invalid operations can be traced.

4. Immutability Alignment:
   Logged events can later be embedded into blockchain transactions
   to create a permanent audit trail.

NOTE:
-----
This logger is intentionally simple and educational.
It does NOT write to files or external systems.
All logs are stored in memory for easy demonstration.
"""

from datetime import datetime
from typing import List, Dict


class SystemLogger:
    """
    SystemLogger records and displays system events.

    Each log entry captures:
    - Timestamp
    - Node ID (if applicable)
    - Action performed
    - Outcome (SUCCESS / FAILURE / INFO)
    """

    def __init__(self):
        """
        Initialize the logger with an empty log store.
        """
        self._logs: List[Dict[str, str]] = []


    # -----------------------------------------------------------------
    # Logging Methods
    # -----------------------------------------------------------------

    def log_event(self, node_id: str, action: str, outcome: str):
        """
        Record a system event.

        Args:
            node_id (str): ID of the node performing the action
            action (str): Description of the action
            outcome (str): Result of the action (e.g., SUCCESS, FAILURE)

        Example:
            logger.log_event("NODE1", "REQUEST_CPU", "SUCCESS")
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = {
            "timestamp": timestamp,
            "node_id": node_id,
            "action": action,
            "outcome": outcome
        }

        self._logs.append(log_entry)

    def log_system_event(self, action: str, outcome: str):
        """
        Record a system-level event not tied to a specific node.

        Args:
            action (str): Description of the system action
            outcome (str): Result of the action
        """
        self.log_event(
            node_id="SYSTEM",
            action=action,
            outcome=outcome
        )

    # -----------------------------------------------------------------
    # Audit & Display Methods
    # -----------------------------------------------------------------

    def get_logs(self) -> List[Dict[str, str]]:
        """
        Retrieve all log entries.

        Returns:
            List of log dictionaries.
        """
        return self._logs

    def print_audit_log(self):
        """
        Print the audit log in a clean, readable format.

        This function is intended for CLI demonstrations and
        lecturer explanations.
        """
    `   if not self._logs:
            print("[AUDIT] No system events recorded.")
            return

        print("\n========== SYSTEM AUDIT LOG ==========")
        for index, log in enumerate(self._logs):
            print(f"Event #{index + 1}")
            print(f"  Time    : {log['timestamp']}")
            print(f"  Node ID : {log['node_id']}")
            print(f"  Action  : {log['action']}")
            print(f"  Outcome : {log['outcome']}")
            print("-------------------------------------")
        print("========== END OF AUDIT LOG ==========\n")

    # -----------------------------------------------------------------
    # Blockchain Audit Integration (Future Use)
    # -----------------------------------------------------------------

    def export_for_blockchain(self) -> List[Dict[str, str]]:
        """
        Prepare logs for inclusion in blockchain transactions.

        This demonstrates how system logs can become part of an
        immutable blockchain audit trail.

        Returns:
            A list of log entries suitable for blockchain storage.
        """
        return self._logs.copy()
