import logging
from typing import List

from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
TOP_N = 5

reranker = CrossEncoder(RERANKER_MODEL)


def rerank_documents(question: str, docs: List[Document], top_n: int = TOP_N) -> List[Document]:
    if not docs:
        logger.info("Reranker received 0 documents")
        return []

    pairs = [(question, doc.page_content) for doc in docs]

    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(scores, docs),
        key=lambda x: x[0],
        reverse=True
    )

    final_docs = []

    for rank, (score, doc) in enumerate(ranked[:top_n], start=1):
        doc.metadata["reranker_score"] = float(score)
        logger.info(
            f"Reranker Rank {rank} | Score={score:.4f} | Source={doc.metadata.get('source', 'unknown')}"
        )
        final_docs.append(doc)

    return final_docs