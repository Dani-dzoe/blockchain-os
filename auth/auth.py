"""
Simple Authentication & Identity module for the demo.

This module provides an `AuthManager` that can register nodes (issue simple
identity tokens) and verify tokens. The tokens here are simple deterministic
strings for demonstration only — do not use in production systems.
"""

from __future__ import annotations

from typing import Dict
import hashlib


class AuthManager:
    """Manage simple identity tokens for nodes.

    For educational purposes tokens are deterministic hashes of the node_id
    combined with an optional secret. Real systems should use secure
    asymmetric keys and proper authentication protocols.
    """

    def __init__(self, secret: str = "demo-secret") -> None:
        self.secret = secret
        # map node_id -> token
        self.tokens: Dict[str, str] = {}

    def issue_token(self, node_id: str) -> str:
        """Issue and store a token for `node_id`.

        The token is a SHA-256 hex digest of node_id + secret for reproducibility.
        """
        if not node_id or not node_id.strip():
            raise ValueError("node_id cannot be empty")
        raw = f"{node_id}:{self.secret}".encode("utf-8")
        token = hashlib.sha256(raw).hexdigest()
        self.tokens[node_id] = token
        return token

    def verify_token(self, token: str) -> bool:
        """Verify if the provided token is known/issued."""
        return token in self.tokens.values()

    def get_token_for(self, node_id: str) -> str:
        """Get the stored token for a node, issue if missing."""
        if node_id not in self.tokens:
            return self.issue_token(node_id)
        return self.tokens[node_id]

    def revoke_token(self, node_id: str) -> None:
        """Revoke a previously issued token for a node."""
        if node_id in self.tokens:
            del self.tokens[node_id]
