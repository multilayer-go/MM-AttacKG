"""Configuration loader for MM-AttacKG."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigLoader:
    """Load and manage configuration from YAML file and environment variables."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to config.yaml file. If None, searches in default locations.
        """
        self.config_path = config_path or self._find_config()
        self.config = self._load_config()
        self._load_env_vars()
    
    def _find_config(self) -> str:
        """Find config.yaml in default locations."""
        search_paths = [
            "config/config.yaml",
            "../config/config.yaml",
            "../../config/config.yaml",
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                return path
        
        # If not found, use example config
        example_path = "config/config.example.yaml"
        if os.path.exists(example_path):
            print(f"Warning: config.yaml not found. Using {example_path}")
            return example_path
        
        raise FileNotFoundError(
            "Configuration file not found. Please create config/config.yaml "
            "from config/config.example.yaml"
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_env_vars(self):
        """Load environment variables from .env file."""
        load_dotenv()
        
        # Override config with environment variables if present
        if os.getenv("DASHSCOPE_API_KEY"):
            self.config.setdefault('api', {}).setdefault('dashscope', {})['api_key'] = os.getenv("DASHSCOPE_API_KEY")
        
        if os.getenv("EVAL_API_KEY"):
            self.config.setdefault('api', {}).setdefault('eval', {})['api_key'] = os.getenv("EVAL_API_KEY")
        
        if os.getenv("DASHSCOPE_BASE_URL"):
            self.config.setdefault('api', {}).setdefault('dashscope', {})['base_url'] = os.getenv("DASHSCOPE_BASE_URL")
        
        if os.getenv("EVAL_API_URL"):
            self.config.setdefault('api', {}).setdefault('eval', {})['base_url'] = os.getenv("EVAL_API_URL")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key path.
        
        Args:
            key: Dot-separated key path (e.g., 'api.dashscope.api_key')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_api_config(self, provider: str) -> Dict[str, Any]:
        """
        Get API configuration for a specific provider.
        
        Args:
            provider: API provider name ('dashscope' or 'eval')
            
        Returns:
            API configuration dictionary
        """
        return self.config.get('api', {}).get(provider, {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration."""
        return self.config.get('processing', {})
    
    def get_pipeline_config(self) -> Dict[str, Any]:
        """Get pipeline configuration."""
        return self.config.get('pipeline', {})


# Global config instance
_config: Optional[ConfigLoader] = None


def get_config(config_path: Optional[str] = None) -> ConfigLoader:
    """
    Get global configuration instance.
    
    Args:
        config_path: Path to config file (optional)
        
    Returns:
        ConfigLoader instance
    """
    global _config
    if _config is None:
        _config = ConfigLoader(config_path)
    return _config


def reload_config(config_path: Optional[str] = None):
    """
    Reload configuration.
    
    Args:
        config_path: Path to config file (optional)
    """
    global _config
    _config = ConfigLoader(config_path)
