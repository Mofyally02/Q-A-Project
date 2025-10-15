import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/qa_system")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # RabbitMQ Configuration
    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user: str = os.getenv("RABBITMQ_USER", "guest")
    rabbitmq_password: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    
    # API Keys
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
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "your-encryption-key-here")
    
    # CORS Configuration
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
    
    # Application Settings
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    
    # AI Processing Settings
    min_confidence_score: float = 0.7
    max_question_length: int = 5000
    max_file_size_mb: int = 5
    ai_content_threshold: float = 0.1  # 10% max AI content
    uniqueness_threshold: float = 0.9  # 90% min uniqueness
    
    class Config:
        env_file = ".env"

settings = Settings()
