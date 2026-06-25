from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "SafePILA API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # File upload
    MAX_FILE_SIZE: int = 25 * 1024 * 1024  # 25MB
    ALLOWED_CONTENT_TYPES: List[str] = ["application/pdf"]

    # Scoring weights (sum should be 100)
    WEIGHT_METADATA: int = 35
    WEIGHT_DATES: int = 30
    WEIGHT_STRUCTURE: int = 35
    WEIGHT_AI: int = 15

    # Semaphore thresholds
    SCORE_GREEN_MAX: int = 20
    SCORE_YELLOW_MAX: int = 50

    # Date tolerance in minutes
    DATE_TOLERANCE_MINUTES: int = 5

    # Known PDF editors (malicious list)
    BLACKLISTED_PRODUCERS: List[str] = [
        # Editors online gratuitos
        "ilovepdf", "smallpdf", "pdf24", "sejda", "pdfescape",
        "pdf candy", "sodapdf", "hipdf", "pdf.io", "pdf2go",
        "combinepdf", "mergepdf", "splitpdf", "rotatepdf",
        "pdfresizer", "pdfcompressor", "pdf_unlocker",
        # Editors de escritorio
        "foxit phantompdf", "nitro", "pdf-xchange", "pdfxchange",
        "pdf architect", "pdfsam", "pdftk", "ghostscript",
        "pdfshuffler", "pdfarranger", "briss", "mutool",
        # Conversores
        "convertio", "zamzar", "cloudconvert", "online-convert",
        # Editores de imagen a PDF
        "photoshop", "gimp", "paint.net", "canva",
        "picmonkey", "befunky", "fotor", "lunapic",
        # Herramientas de manipulación
        "qpdf", "poppler", "mupdf", "pdftops", "pdftotext",
        "pdfimages", "pdfinfo", "pdffonts",
    ]

    # Known AI producers
    AI_PRODUCERS: List[str] = [
        "chatgpt", "openai", "midjourney", "dall-e", "dalle",
        "adobe firefly", "canva ai", "stable diffusion", "stability ai",
        "runway", "pika", "luma", "sora", "gemini", "claude",
        "bing image creator", "copilot", "dall-e-2", "dall-e-3",
        "leonardo ai", "playground ai", "nightcafe", "deepai",
        "craiyon", "starryai", "wombo", "synthesia",
        "descript", "runway ml", "rephrase ai",
    ]

    # Synthetic font indicators
    SYNTHETIC_FONTS: List[str] = [
        "dejavu", "liberation", "nimbus", "fpdf", "reportlab",
        "weasyprint", "wkhtmltopdf", "pdfkit", "jspdf", "pdfmake",
        "msttcore", "arial", "helvetica", "courier",
        "times new roman", "georgia", "verdana",
    ]

    # Suspicious patterns in metadata
    SUSPICIOUS_CREATOR_PATTERNS: List[str] = [
        "microsoft word", "microsoft excel", "microsoft powerpoint",
        "google docs", "google sheets", "libreoffice",
        "openoffice", "apple pages", "apple numbers",
        "apache", "latex", "overleaf",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()