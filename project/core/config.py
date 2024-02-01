from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", case_sensitive=True, env_file=".env")

    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: list[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | list[str]) -> str | list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_SCHEME: str
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    
    DATABASE_URI: str | None = None

    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: str | None, values: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme=values.data.get("POSTGRES_SCHEME"),
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
            port=values.data.get("POSTGRES_PORT"),
        ).unicode_string()

settings = Settings()
