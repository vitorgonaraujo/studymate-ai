import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "")
    CHROMA_PATH = os.getenv("CHROMA_PATH", "storage/chroma")
    UPLOAD_PATH = os.getenv("UPLOAD_PATH", "storage/uploads")
    SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "studymate_session")
    SESSION_COOKIE_MAX_AGE = int(os.getenv("SESSION_COOKIE_MAX_AGE", "31536000"))
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    DOCUMENT_TTL_HOURS = int(os.getenv("DOCUMENT_TTL_HOURS", "72"))
    MAX_DOCUMENTS_PER_SESSION = int(os.getenv("MAX_DOCUMENTS_PER_SESSION", "3"))
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
    CLEANUP_INTERVAL_MINUTES = int(os.getenv("CLEANUP_INTERVAL_MINUTES", "60"))
    FRONTEND_ORIGINS = [
        value.strip()
        for value in os.getenv(
            "FRONTEND_ORIGINS", "http://localhost:4200,http://localhost:5173"
        ).split(",")
        if value.strip()
    ]


settings = Settings()
