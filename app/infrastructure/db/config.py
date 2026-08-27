from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mini_marketplace"
    jwt_secret: str = "your-secret-key-change-me"
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()