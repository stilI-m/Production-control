from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    project_name: str = 'Production Control API'
    version: str = '1.0.0'
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/production_control"
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra="ignore")
settings = Settings()