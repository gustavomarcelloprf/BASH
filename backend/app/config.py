from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dash.db"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    ANTHROPIC_API_KEY: str = ""
    DEBUG: bool = False
    # Comma-separated list of allowed frontend origins, e.g.:
    # CORS_ORIGINS=https://myapp.vercel.app,http://localhost:5173
    CORS_ORIGINS: str = "http://localhost:5173"
    FRONTEND_URL: str = ""
    COLUMN_MAPPING: dict = {
        "data": "Data",
        "colaborador": "Nome",
        "projeto": "Projeto",
        "horas": "Horas",
    }

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
