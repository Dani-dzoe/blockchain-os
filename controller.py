"""
Main Controller - Orchestration Layer
Integrates existing modules from the team's GitHub repository.
Assumes other team members have already implemented:
- cli_interface.py
- blockchain_manager.py  
- resource_manager.py
- consensus_module.py
- auth_module.py
"""

import sys
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Import existing modules from team's codebase
# These are assumed to be already implemented by other team members
try:
    from cli_interface import CLIInterface
    from blockchain_manager import BlockchainManager
    from resource_manager import ResourceManager
    from consensus_module import ConsensusModule
    from auth_module import AuthenticationManager
except ImportError as e:
    print(f"Error: Missing module - {e}")
    print("Please ensure all team modules are in the same directory")
    sys.exit(1)

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MainController:
    """
    Orchestrates the interaction between all system modules.
    This is the ONLY file you need to create - others exist in the repo.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize controller with existing modules.
        
        Args:
            config: System configuration from CLI or config file
        """
        self.config = config or {}
        self.is_running = False
        
        # Initialize existing modules (already implemented by team)
        logger.info("Initializing system with existing modules...")
        
        # Authentication (already implemented)
        self.auth = AuthenticationManager(
            secret_key=self.config.get('secret_key', 'default-key')
        )
        
        # Blockchain (already implemented)
        self.blockchain = BlockchainManager(
            difficulty=self.config.get('difficulty', 4)
        )
        
        # Resource Manager (already implemented)
        self.resource_manager = ResourceManager(
            max_cpu=self.config.get('max_cpu', 80.0)
        )
        
        # Consensus Module (already implemented)
        self.consensus = ConsensusModule(
            peers=self.config.get('peers', [])
        )
        
        # CLI Interface (already implemented)
        self.cli = CLIInterface()
        
        logger.info("All modules loaded successfully")
    
    def start(self):
        """Start all system components."""
        if self.is_running:
            return
        
        logger.info("Starting system orchestration...")
        self.is_running = True
        
        # Start resource monitoring
        self.resource_manager.start()
        
        # Connect to network peers
        self.consensus.connect()
        
        logger.info("System started. Ready for transactions.")
    
    def stop(self):
        """Stop all system components gracefully."""
        if not self.is_running:
            return
        
        logger.info("Stopping system...")
        
        # Stop components in reverse order
        self.consensus.disconnect()
        self.resource_manager.stop()
        self.is_running = False
        
        logger.info("System stopped")
    
    def process_transaction(self, tx_data: Dict[str, Any]) -> bool:
        """
        Main transaction processing pipeline.
        
        Flow: Auth → Resource Check → Blockchain → Consensus
        
        Returns:
            bool: True if transaction was processed successfully
        """
        logger.info(f"Processing transaction: {tx_data.get('type', 'unknown')}")
        
        # 1. Authenticate (using existing auth module)
        if not self._authenticate_transaction(tx_data):
            logger.error("Authentication failed")
            return False
        
        # 2. Check resources (using existing resource manager)
        if not self.resource_manager.can_process():
            logger.error("Insufficient resources")
            return False
        
        # 3. Add to blockchain (using existing blockchain module)
        tx_id = self.blockchain.add_transaction(tx_data)
        if not tx_id:
            logger.error("Failed to add to blockchain")
            return False
        
        logger.info(f"Transaction added: {tx_id}")
        
        # 4. Trigger consensus if needed (using existing consensus module)
        if self._should_trigger_consensus():
            self.consensus.sync_transaction(tx_data)
        
        return True
    
    def _authenticate_transaction(self, tx_data: Dict[str, Any]) -> bool:
        """
        Use existing auth module to authenticate transaction.
        
        Args:
            tx_data: Transaction data containing auth info
            
        Returns:
            bool: True if authenticated
        """
        # Extract auth from transaction (adjust based on actual implementation)
        token = tx_data.get('token')
        user = tx_data.get('user')
        
        if token:
            return self.auth.verify_token(token)
        elif user:
            # Alternative auth method if implemented
            return self.auth.validate_user(user)
        
        return False  # No auth provided
    
    def _should_trigger_consensus(self) -> bool:
        """
        Determine if consensus should be triggered.
        Based on block size or other criteria.
        """
        # Check if block is full (adjust threshold as needed)
        pending = len(self.blockchain.pending_transactions)
        block_size = self.config.get('block_size', 3)
        
        return pending >= block_size
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get system status from all modules.
        
        Returns:
            Dict containing status of all components
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'running': self.is_running,
            'blockchain': {
                'blocks': len(self.blockchain.chain),
                'pending': len(self.blockchain.pending_transactions)
            },
            'resources': self.resource_manager.get_status(),
            'consensus': {
                'peers': len(self.consensus.connected_peers),
                'synced': self.consensus.is_synced
            }
        }
    
    def run_interactive(self):
        """Run interactive CLI mode."""
        self.start()
        
        try:
            # Use existing CLI interface
            self.cli.set_controller(self)
            self.cli.run()
        except KeyboardInterrupt:
            logger.info("Interactive mode stopped by user")
        finally:
            self.stop()


def main():
    """Entry point - minimal, just starts the controller."""
    import argparse
    
    parser = argparse.ArgumentParser(description='System Orchestration Controller')
    parser.add_argument('--cli', action='store_true', help='Run in interactive mode')
    parser.add_argument('--config', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Load config if provided
    config = {}
    if args.config:
        try:
            import json
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return
    
    # Create and run controller
    controller = MainController(config)
    
    if args.cli:
        controller.run_interactive()
    else:
        # Start and keep running
        controller.start()
        try:
            # Keep alive - real systems would have more complex lifecycle
            import time
            while controller.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            controller.stop()


if __name__ == "__main__":
    main()