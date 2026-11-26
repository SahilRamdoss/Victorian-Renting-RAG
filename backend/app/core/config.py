from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = ""
    embedding_dim: int = 1536

settings = Settings()