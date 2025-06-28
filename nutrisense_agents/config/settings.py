from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

    # API Keys - optional for local development
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    OPENAI_MODEL: str = "gpt-4"

    # Supabase settings - optional for local development
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Groq settings - optional for local development
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama3-70b-8192"


settings = Settings()