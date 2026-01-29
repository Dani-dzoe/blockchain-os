"""
Consensus Package for Blockchain-Based Distributed Operating System

This package provides consensus mechanisms for distributed agreement on blocks.
"""

from .consensus import ConsensusEngine, validate_block_structure

__all__ = ['ConsensusEngine', 'validate_block_structure']