"""
Core configuration module
Centralized settings management for AL-Tech Academy Q&A Platform
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database Configuration
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://username:password@localhost:5432/altech_qa"
    )
    auth_database_url: str = os.getenv(
        "AUTH_DATABASE_URL", 
        "postgresql://qa_user:qa_password@localhost:5432/qa_auth"
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # RabbitMQ Configuration
    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user: str = os.getenv("RABBITMQ_USER", "guest")
    rabbitmq_password: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    rabbitmq_vhost: str = os.getenv("RABBITMQ_VHOST", "/")
    
    # API Keys (External Services)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    xai_api_key: str = os.getenv("XAI_API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    stealth_api_key: str = os.getenv("STEALTH_API_KEY", "")
    turnitin_api_key: str = os.getenv("TURNITIN_API_KEY", "")
    
    # Poe API Keys for latest models
    poe_api_key_chatgpt: str = os.getenv("POE_API_KEY_CHATGPT", "")
    poe_api_key_claude: str = os.getenv("POE_API_KEY_CLAUDE", "")
    poe_api_key_gemini: str = os.getenv("POE_API_KEY_GEMINI", "")
    poe_api_key_grok: str = os.getenv("POE_API_KEY_GROK", "")
    poe_api_key_qwen: str = os.getenv("POE_API_KEY_QWEN", "")
    poe_api_key_deepseek: str = os.getenv("POE_API_KEY_DEEPSEEK", "")
    poe_api_key_gpt_oss: str = os.getenv("POE_API_KEY_GPT_OSS", "")
    poe_api_key_kimi: str = os.getenv("POE_API_KEY_KIMI", "")
    
    # AWS Configuration
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_s3_bucket: str = os.getenv("AWS_S3_BUCKET", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Security
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "your-encryption-key-here-change-in-production")
    
    # CORS Configuration
    cors_origins: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://localhost:5173,http://localhost:8080"
    ).split(",")
    
    # Application Settings
    app_name: str = os.getenv("APP_NAME", "AL-Tech Academy Q&A Platform")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # AI Processing Settings
    min_confidence_score: float = float(os.getenv("MIN_CONFIDENCE_SCORE", "0.7"))
    max_question_length: int = int(os.getenv("MAX_QUESTION_LENGTH", "5000"))
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
    ai_content_threshold: float = float(os.getenv("AI_CONTENT_THRESHOLD", "0.1"))  # 10% max AI content
    uniqueness_threshold: float = float(os.getenv("UNIQUENESS_THRESHOLD", "0.9"))  # 90% min uniqueness
    
    # WebSocket Settings
    websocket_ping_interval: int = int(os.getenv("WEBSOCKET_PING_INTERVAL", "30"))
    websocket_timeout: int = int(os.getenv("WEBSOCKET_TIMEOUT", "300"))
    
    # Rate Limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    rate_limit_per_hour: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # Admin Settings
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@altech.academy")
    admin_initial_password: str = os.getenv("ADMIN_INITIAL_PASSWORD", "")
    maintenance_mode: bool = os.getenv("MAINTENANCE_MODE", "False").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env that aren't in the model


# Global settings instance
settings = Settings()

