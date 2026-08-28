from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mini_marketplace"
    jwt_secret: str = "your-secret-key-change-me-to-something-longer-32-bytes"


settings = Settings()