from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dash.db"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    OPENAI_API_KEY: str = ""
    DEBUG: bool = False
    COLUMN_MAPPING: dict = {
        "data": "Data",
        "colaborador": "Nome",
        "projeto": "Projeto",
        "horas": "Horas",
    }

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
