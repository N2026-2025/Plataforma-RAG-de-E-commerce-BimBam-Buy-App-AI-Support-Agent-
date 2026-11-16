"""
rag/reranker.py
-----------------------------------------------------------------------------
Reranking con cross-encoder, siguiendo el patrón de
llm-zoomcamp (06-best-practices/lessons/03-reranking.md):

Un cross-encoder recibe la pregunta y CADA candidato juntos (a diferencia
de los embeddings, que los codifican por separado) y produce un score de
relevancia mucho más preciso. Es más lento que la búsqueda vectorial/BM25,
por eso se aplica solo sobre el pool reducido que ya filtró la etapa de
recuperación híbrida (stage 1), no sobre toda la base de conocimiento.

Pipeline de dos etapas:
    Stage 1 (recall):    Hybrid Search (BM25 + vectorial) + RRF -> ~10-20 candidatos
    Stage 2 (precisión): Cross-Encoder reranking               -> top-N final para el LLM
-----------------------------------------------------------------------------
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import List

from langchain_core.documents import Document

from rag.config import ENABLE_RERANKER, RERANK_TOP_N, RERANKER_MODEL

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_cross_encoder():
    """Carga (una sola vez, cacheada) el modelo cross-encoder de reranking."""
    from sentence_transformers import CrossEncoder

    return CrossEncoder(RERANKER_MODEL)


def rerank(query: str, candidates: List[Document], top_n: int = RERANK_TOP_N) -> List[Document]:
    """Reordena `candidates` por relevancia real respecto a `query` y devuelve
    los `top_n` mejores, cada uno con el score de reranking en su metadata
    (`rerank_score`) para trazabilidad/observabilidad.

    Si ENABLE_RERANKER está desactivado (por defecto en entornos con memoria
    limitada como Render Free Tier a 512MB) o si falla la carga del modelo,
    utiliza directamente el ranking RRF de la etapa híbrida previa (BM25 + Vector).
    """
    if not candidates:
        return []

    if not ENABLE_RERANKER:
        reranked_docs = []
        for i, doc in enumerate(candidates[:top_n]):
            doc.metadata["rerank_score"] = float(doc.metadata.get("rrf_score", 1.0 / (i + 1)))
            reranked_docs.append(doc)
        return reranked_docs

    try:
        model = _get_cross_encoder()
        pairs = [(query, doc.page_content) for doc in candidates]
        scores = model.predict(pairs)

        scored = list(zip(candidates, scores))
        scored.sort(key=lambda pair: pair[1], reverse=True)

        reranked_docs = []
        for doc, score in scored[:top_n]:
            doc.metadata["rerank_score"] = float(score)
            reranked_docs.append(doc)

        return reranked_docs
    except Exception as exc:
        logger.warning("Reranking omitido por error o recursos insuficientes: %s. Usando ranking RRF.", exc)
        reranked_docs = []
        for i, doc in enumerate(candidates[:top_n]):
            doc.metadata["rerank_score"] = float(doc.metadata.get("rrf_score", 1.0 / (i + 1)))
            reranked_docs.append(doc)
        return reranked_docs
