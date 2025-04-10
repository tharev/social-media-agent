"""
API Key Management module for securely storing and retrieving API keys.

This module provides functionality for managing API keys for various services
used by the social media agent system.
"""

import logging
import json
import os
import base64
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger("llm_integration.api_key_manager")

class APIKeyManager:
    """
    API Key Manager for securely storing and retrieving API keys.
    
    This class provides functionality for:
    - Storing API keys securely
    - Retrieving API keys for use by various components
    - Validating API keys
    - Managing different sets of keys for different environments
    """
    
    def __init__(self, config_path: str = None, master_password: str = None):
        """
        Initialize the API Key Manager.
        
        Args:
            config_path: Path to the configuration file
            master_password: Master password for encryption/decryption
        """
        self.config_path = config_path or os.path.join("config", "api_keys.json")
        self.master_password = master_password
        self.keys = {}
        self.cipher_suite = None
        
        # Initialize encryption
        self._initialize_encryption()
        
        # Load keys if config exists
        if os.path.exists(self.config_path):
            self.load_keys()
        
        logger.info("API Key Manager initialized")
    
    def _initialize_encryption(self) -> None:
        """
        Initialize the encryption system.
        """
        if not self.master_password:
            # Use environment variable if available
            self.master_password = os.environ.get("API_KEY_MASTER_PASSWORD", "default_password")
        
        # Generate a key from the password
        password = self.master_password.encode()
        salt = b'social_media_agent_salt'  # In production, this should be stored securely
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.cipher_suite = Fernet(key)
    
    def add_key(self, service: str, key_type: str, key_value: str) -> bool:
        """
        Add an API key.
        
        Args:
            service: Service name (e.g., 'openai', 'twitter')
            key_type: Type of key (e.g., 'api_key', 'access_token')
            key_value: The actual API key
            
        Returns:
            bool: Success status
        """
        if not service or not key_type or not key_value:
            logger.error("Missing required parameters")
            return False
        
        if service not in self.keys:
            self.keys[service] = {}
        
        # Encrypt the key
        encrypted_key = self.cipher_suite.encrypt(key_value.encode()).decode()
        
        # Store the encrypted key
        self.keys[service][key_type] = encrypted_key
        
        # Save to file
        return self.save_keys()
    
    def get_key(self, service: str, key_type: str) -> Optional[str]:
        """
        Get an API key.
        
        Args:
            service: Service name
            key_type: Type of key
            
        Returns:
            str: The API key or None if not found
        """
        if service not in self.keys or key_type not in self.keys[service]:
            logger.warning(f"Key not found: {service}.{key_type}")
            return None
        
        # Get the encrypted key
        encrypted_key = self.keys[service][key_type]
        
        # Decrypt the key
        try:
            decrypted_key = self.cipher_suite.decrypt(encrypted_key.encode()).decode()
            return decrypted_key
        except Exception as e:
            logger.error(f"Error decrypting key: {e}")
            return None
    
    def remove_key(self, service: str, key_type: str) -> bool:
        """
        Remove an API key.
        
        Args:
            service: Service name
            key_type: Type of key
            
        Returns:
            bool: Success status
        """
        if service not in self.keys or key_type not in self.keys[service]:
            logger.warning(f"Key not found: {service}.{key_type}")
            return False
        
        # Remove the key
        del self.keys[service][key_type]
        
        # If no keys left for the service, remove the service
        if not self.keys[service]:
            del self.keys[service]
        
        # Save to file
        return self.save_keys()
    
    def get_service_keys(self, service: str) -> Dict:
        """
        Get all keys for a service.
        
        Args:
            service: Service name
            
        Returns:
            Dict: Dictionary of key types and values
        """
        if service not in self.keys:
            logger.warning(f"Service not found: {service}")
            return {}
        
        # Get all keys for the service
        service_keys = {}
        for key_type, encrypted_key in self.keys[service].items():
            try:
                decrypted_key = self.cipher_suite.decrypt(encrypted_key.encode()).decode()
                service_keys[key_type] = decrypted_key
            except Exception as e:
                logger.error(f"Error decrypting key: {e}")
                service_keys[key_type] = None
        
        return service_keys
    
    def get_all_services(self) -> List[str]:
        """
        Get a list of all services with stored keys.
        
        Returns:
            List[str]: List of service names
        """
        return list(self.keys.keys())
    
    def save_keys(self) -> bool:
        """
        Save keys to the configuration file.
        
        Returns:
            bool: Success status
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.keys, f, indent=2)
            
            logger.info(f"Saved API keys to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving API keys: {e}")
            return False
    
    def load_keys(self) -> bool:
        """
        Load keys from the configuration file.
        
        Returns:
            bool: Success status
        """
        try:
            with open(self.config_path, 'r') as f:
                self.keys = json.load(f)
            
            logger.info(f"Loaded API keys from {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading API keys: {e}")
            return False
    
    def validate_key(self, service: str, key_type: str) -> bool:
        """
        Validate an API key.
        
        Args:
            service: Service name
            key_type: Type of key
            
        Returns:
            bool: Whether the key is valid
        """
        key = self.get_key(service, key_type)
        if not key:
            return False
        
        # Implement service-specific validation
        if service == "openai":
            import requests
            headers = {"Authorization": f"Bearer {key}"}
            try:
                response = requests.get("https://api.openai.com/v1/models", headers=headers)
                return response.status_code == 200
            except Exception as e:
                logger.error(f"Error validating OpenAI key: {e}")
                return False
        
        # For other services, just check if the key exists
        return True
    
    def get_config_for_service(self, service: str) -> Dict:
        """
        Get a configuration dictionary for a service with decrypted keys.
        
        Args:
            service: Service name
            
        Returns:
            Dict: Configuration dictionary with decrypted keys
        """
        service_keys = self.get_service_keys(service)
        
        # Create a configuration dictionary
        config = {
            "service": service
        }
        
        # Add all keys to the configuration
        config.update(service_keys)
        
        return config
