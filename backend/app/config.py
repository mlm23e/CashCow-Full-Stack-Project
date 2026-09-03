"""
CashCow Command Center

This file holds our centralized app settings and replaces the scattered os.environ.get() functions in database.py, main.py, and security.py. This class will read real environment variables from a .env file
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://mmarse:Michaelmarse0%21@localhost:5432/cashcow_dev"
    # no default value here because a wrong secret key value can cause the app to start up 
    # seemingly successfully but with a silent failure because it will pass an incorrect 
    # secret key value for our JWT
    secret_key : str
    frontend_origin : str = "http://localhost:5173"

    # tells pydantic settings to actually read from backend/.env and fill these fields from it
    model_config = SettingsConfigDict(env_file=".env")

# without the .env file setting values, this line will raise an error on startup
settings = Settings()