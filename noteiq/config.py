"""
Configuration management for NoteIQ
"""
import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# Load .env file if exists
load_dotenv()


@dataclass
class Config:
    """NoteIQ Configuration"""
    
    # OpenAI Configuration
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 1000
    
    # Storage Configuration
    storage_file: str = "notes.json"
    storage_backup_enabled: bool = True
    storage_backup_count: int = 5
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    
    # Streamlit Configuration
    streamlit_port: int = 8501
    streamlit_debug: bool = False
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Feature Flags
    enable_ai: bool = True
    enable_api: bool = True
    enable_cli: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.openai_api_key:
            self.enable_ai = False
    
    def is_ai_enabled(self) -> bool:
        """Check if AI features are enabled"""
        return self.enable_ai and bool(self.openai_api_key)
    
    def get_storage_path(self) -> str:
        """Get the storage file path"""
        return self.storage_file
    
    def set_api_key(self, api_key: str):
        """Set OpenAI API key"""
        self.openai_api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key
        self.enable_ai = bool(api_key)


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance"""
    return config


def update_config(**kwargs):
    """Update configuration values"""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)


def load_config_from_env():
    """Load configuration from environment variables"""
    global config
    
    # Load from environment
    config.openai_api_key = os.getenv("OPENAI_API_KEY", config.openai_api_key)
    config.openai_model = os.getenv("OPENAI_MODEL", config.openai_model)
    config.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", config.openai_temperature))
    config.storage_file = os.getenv("STORAGE_FILE", config.storage_file)
    config.api_host = os.getenv("API_HOST", config.api_host)
    config.api_port = int(os.getenv("API_PORT", config.api_port))
    config.log_level = os.getenv("LOG_LEVEL", config.log_level)
    
    # Update enable flags
    config.enable_ai = bool(config.openai_api_key)
    config.enable_api = os.getenv("ENABLE_API", "true").lower() == "true"
    config.enable_cli = os.getenv("ENABLE_CLI", "true").lower() == "true"