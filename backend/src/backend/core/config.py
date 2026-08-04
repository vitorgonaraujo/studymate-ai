import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Configurações da aplicação.
    """

    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")

    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")

    LLM_MODEL: str = os.getenv("LLM_MODEL", "")

    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "storage/chroma")

    UPLOAD_PATH: str = os.getenv("UPLOAD_PATH", "storage/uploads")


settings = Settings()
