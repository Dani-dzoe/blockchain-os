"""
Core Blockchain Components

This package contains the fundamental building blocks of the blockchain system:
- Blockchain: Chain management and validation
- Block: Individual block structure with proof-of-work
- Node: Participant entities with resource quotas
- Transaction: System operations represented as blockchain transactions

All components are designed for educational clarity and easy understanding.
"""

from .blockchain import Blockchain, Block
from .node import Node
from .transaction import Transaction

__all__ = ['Blockchain', 'Block', 'Node', 'Transaction']

