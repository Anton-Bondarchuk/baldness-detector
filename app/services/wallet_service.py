"""
Wallet Service for managing embedded wallets using Thirdweb SDK.
This service handles wallet creation and assignment to users.
"""

import asyncio
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import wallet_config
from app.oauth.infra.pg_user_repository import PgUserRepository

logger = logging.getLogger(__name__)

class WalletService:
    """Service for managing embedded wallets"""
    
    def __init__(self):
        self.thirdweb_secret_key = wallet_config.thirdweb_secret_key.get_secret_value()
        self.thirdweb_client_id = wallet_config.thirdweb_client_id
    
    async def create_wallet(self, user_id: str) -> str:
        """
        Create a new embedded wallet using Thirdweb SDK
        
        Args:
            user_id: Unique user identifier to generate deterministic wallet
            
        Returns:
            wallet_address: The public address of the created wallet
            
        Raises:
            Exception: If wallet creation fails
        """
        try:
            # Import thirdweb SDK (install with: pip install thirdweb-sdk)
            from thirdweb import ThirdwebSDK
            from thirdweb.types.settings.server_wallet import EmbeddedWalletOptions
            
            # Initialize Thirdweb SDK with embedded wallet
            sdk = ThirdwebSDK.from_private_key(
                private_key=self.thirdweb_secret_key,
                network="polygon",  # You can change network as needed
                client_id=self.thirdweb_client_id
            )
            
            # Create embedded wallet for the user
            wallet_options = EmbeddedWalletOptions(
                user_id=str(user_id),
                # Optional: add email or other identifier
            )
            
            embedded_wallet = sdk.get_embedded_wallet(wallet_options)
            wallet_address = await embedded_wallet.get_address()
            
            logger.info(f"Created wallet {wallet_address} for user {user_id}")
            return wallet_address
            
        except ImportError:
            # Fallback: Mock wallet creation for development/testing
            logger.warning("Thirdweb SDK not available, using mock wallet creation")
            return await self._create_mock_wallet(user_id)
        except Exception as e:
            logger.error(f"Failed to create wallet for user {user_id}: {str(e)}")
            raise Exception(f"Wallet creation failed: {str(e)}")
    
    async def _create_mock_wallet(self, user_id: str) -> str:
        """
        Create a mock wallet address for development/testing
        
        Args:
            user_id: User identifier
            
        Returns:
            Mock wallet address
        """
        import hashlib
        
        # Generate deterministic mock address based on user_id
        hash_object = hashlib.sha256(f"wallet_{user_id}".encode())
        mock_address = "0x" + hash_object.hexdigest()[:40]
        
        logger.info(f"Created mock wallet {mock_address} for user {user_id}")
        return mock_address
    
    async def create_and_assign_wallet(self, user_id: int, db_session: AsyncSession) -> Optional[str]:
        """
        Create a new wallet and assign it to the user
        
        Args:
            user_id: The user's database ID
            db_session: Database session
            
        Returns:
            wallet_address: The created wallet address, or None if creation failed
        """
        try:
            # Check if user already has a wallet
            user_repository = PgUserRepository(db_session)
            user = await user_repository.get_by_id(user_id)
            
            if not user:
                logger.error(f"User {user_id} not found")
                return None
                
            if user.wallet_address:
                logger.info(f"User {user_id} already has wallet {user.wallet_address}")
                return user.wallet_address
            
            # Create new wallet
            wallet_address = await self.create_wallet(str(user_id))
            
            # Update user record with wallet address
            await user_repository.update_wallet_address(user_id, wallet_address)
            
            logger.info(f"Successfully assigned wallet {wallet_address} to user {user_id}")
            return wallet_address
            
        except Exception as e:
            logger.error(f"Failed to create and assign wallet for user {user_id}: {str(e)}")
            return None

# Global wallet service instance
wallet_service = WalletService()

async def create_wallet_background_task(user_id: int, db_session: AsyncSession):
    """
    Background task to create and assign wallet to user
    This can be called asynchronously without blocking the auth response
    
    Args:
        user_id: The user's database ID
        db_session: Database session
    """
    try:
        wallet_address = await wallet_service.create_and_assign_wallet(user_id, db_session)
        if wallet_address:
            logger.info(f"Background wallet creation successful for user {user_id}: {wallet_address}")
        else:
            logger.error(f"Background wallet creation failed for user {user_id}")
    except Exception as e:
        logger.error(f"Background wallet creation error for user {user_id}: {str(e)}")
