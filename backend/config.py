from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    LANGCHAIN_API_KEY: str
    TAVILY_API_KEY: str = ""  # Optional - falls back to mock data
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # LangSmith
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_PROJECT: str = "workspace-assistant"
    
    # Pinecone
    PINECONE_HOST: str  # Required: Get from Pinecone console
    PINECONE_INDEX_NAME: str = "workspace-memory"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Compatibility - create config object with simplified attribute names
class Config:
    def __init__(self, settings_obj):
        self.settings = settings_obj
        self.openai_api_key = settings_obj.OPENAI_API_KEY
        self.openai_model = "gpt-4o"  # Default model
        self.temperature = 0.7
        self.pinecone_api_key = settings_obj.PINECONE_API_KEY
        self.pinecone_host = settings_obj.PINECONE_HOST
        self.tavily_api_key = settings_obj.TAVILY_API_KEY
        self.langsmith_api_key = settings_obj.LANGCHAIN_API_KEY

config = Config(settings)
