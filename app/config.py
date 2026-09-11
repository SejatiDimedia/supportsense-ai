from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "SupportSense-AI"
    app_port: int = 8000
    log_level: str = "INFO"

    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3.2:latest"
    embedding_model: str = "nomic-embed-text"

    chroma_persist_dir: str = "./data/chroma"
    n8n_webhook_url: str = "http://localhost:5678/webhook/escalation"
    database_url: str = "sqlite:///./data/support_assistant.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
