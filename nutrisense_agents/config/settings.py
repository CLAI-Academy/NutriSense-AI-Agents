from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str
    OPENAI_MODEL: str

    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    
    #Groq settings
    GROQ_API_KEY: str
    GROQ_MODEL: str


settings = Settings()