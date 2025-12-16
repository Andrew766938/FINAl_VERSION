import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_NAME: str = "betony.db"
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"),
        extra="ignore"  # Ignore extra fields
    )
    
    @property
    def get_db_url(self):
        return f"sqlite+aiosqlite:///{self.DB_NAME}"

    @property
    def auth_data(self):
        return {"secret_key": self.SECRET_KEY, "algorithm": self.ALGORITHM}


try:
    settings = Settings()
except Exception as e:
    print(f"Warning: Could not load settings from .env, using defaults: {e}")
    settings = Settings(
        DB_NAME="betony.db",
        SECRET_KEY="your-secret-key-change-this-in-production",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30
    )
