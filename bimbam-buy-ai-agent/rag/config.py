"""
rag/config.py
-----------------------------------------------------------------------------
Configuración centralizada del pipeline RAG avanzado. Todo es sobreescribible
por variable de entorno / archivo .env para no tocar código en distintos
entornos (local, Docker, OCI).
-----------------------------------------------------------------------------
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Datos y vector store ---------------------------------------------------
_data_dir = os.getenv("DATA_DIR", str(BASE_DIR / "data"))
DATA_DIR = Path(_data_dir)
if not DATA_DIR.is_absolute():
    DATA_DIR = BASE_DIR / DATA_DIR
PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", BASE_DIR / "chroma_db"))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "bimbam_buy_kb")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# --- Recuperación (retrieval) ------------------------------------------------
VECTOR_TOP_K = int(os.getenv("VECTOR_TOP_K", "10"))       # candidatos por búsqueda semántica
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "10"))            # candidatos por búsqueda por keywords
RRF_K = int(os.getenv("RRF_K", "60"))                       # constante de amortiguación de RRF
RERANK_TOP_N = int(os.getenv("RERANK_TOP_N", "4"))          # candidatos finales tras reranking

# --- OCR ---------------------------------------------------------------------
OCR_MIN_CHARS_PER_PAGE = int(os.getenv("OCR_MIN_CHARS_PER_PAGE", "20"))
OCR_LANG = os.getenv("OCR_LANG", "spa")  # idioma de tesseract (español)

# --- LLM / Embeddings ---------------------------------------------------------
LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER", "google" if os.getenv("GOOGLE_API_KEY") else "openai"
).lower()

_default_llm_model = (
    "gemini-1.5-flash"
    if LLM_PROVIDER == "google"
    else ("command-r" if LLM_PROVIDER == "cohere" else "gpt-4o-mini")
)
LLM_MODEL = os.getenv("LLM_MODEL", _default_llm_model)
if LLM_PROVIDER == "google" and ("gpt" in LLM_MODEL.lower() or not LLM_MODEL):
    LLM_MODEL = "gemini-1.5-flash"

_default_emb_provider = "local" if os.getenv("RENDER") else LLM_PROVIDER
EMBEDDINGS_PROVIDER = os.getenv("EMBEDDINGS_PROVIDER", _default_emb_provider).lower()

_default_emb_model = (
    "models/embedding-001"
    if EMBEDDINGS_PROVIDER == "google"
    else ("embed-multilingual-v3.0" if EMBEDDINGS_PROVIDER == "cohere" else "text-embedding-3-small")
)
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", _default_emb_model)

# --- Embeddings locales (ONNX, sin API externa) -------------------------------
# Usados cuando EMBEDDINGS_PROVIDER=local. Ver rag/embeddings_local.py y
# rag/local_embeddings/ (download.py + embedder.py).
LOCAL_EMBEDDINGS_MODEL_REPO = os.getenv("LOCAL_EMBEDDINGS_MODEL_REPO", "Xenova/all-MiniLM-L6-v2")
LOCAL_EMBEDDINGS_MODEL_PATH = Path(
    os.getenv("LOCAL_EMBEDDINGS_MODEL_PATH", BASE_DIR / "models" / LOCAL_EMBEDDINGS_MODEL_REPO)
)

# Modelo de reranking (cross-encoder multilingüe, funciona bien en español)
RERANKER_MODEL = os.getenv(
    "RERANKER_MODEL", "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
)
# En entornos con memoria limitada (como Render Free Tier a 512MB), desactivamos por defecto
# el cross-encoder PyTorch para prevenir OOM (502 Bad Gateway), usando directamente el ranking RRF.
ENABLE_RERANKER = os.getenv(
    "ENABLE_RERANKER", "false" if os.getenv("RENDER") else "true"
).lower() in ("true", "1", "yes")

# --- Memoria conversacional ---------------------------------------------------
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "6"))

# --- Monitoreo -----------------------------------------------------------------
_MONITORING_DATA_DIR = BASE_DIR / "monitoring_data"
_MONITORING_DATA_DIR.mkdir(exist_ok=True)
MONITORING_DB_URL = (
    os.getenv("MONITORING_DB_URL", "").strip()
    or f"sqlite:///{_MONITORING_DATA_DIR / 'monitoring.db'}"
)

# --- Voz -------------------------------------------------------------------------
STT_MODEL = os.getenv("STT_MODEL", "whisper-1")
TTS_MODEL = os.getenv("TTS_MODEL", "tts-1")
TTS_VOICE = os.getenv("TTS_VOICE", "alloy")
