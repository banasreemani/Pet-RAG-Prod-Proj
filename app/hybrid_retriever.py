import logging
from rank_bm25 import BM25Okapi
from app.vector_store import vectorstore

logger = logging.getLogger(__name__)

RETRIEVAL_K = 20 #6


def hybrid_retrieve(question: str):
    logger.info("Hybrid search started")
    logger.info(f"Hybrid query: {question}")

    vector_docs = vectorstore.similarity_search(
        question,
        k=RETRIEVAL_K
    )

    logger.info(f"Vector docs retrieved: {len(vector_docs)}")

    corpus = [doc.page_content for doc in vector_docs]

    tokenized_corpus = [
        doc.lower().split()
        for doc in corpus
    ]

    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = question.lower().split()
    scores = bm25.get_scores(tokenized_query)

    ranked = sorted(
        zip(scores, vector_docs),
        key=lambda x: x[0],
        reverse=True
    )

    final_docs = [
        doc for score, doc in ranked[:RETRIEVAL_K]
    ]

    for i, (score, doc) in enumerate(ranked[:RETRIEVAL_K], start=1):
        logger.info(
            f"Hybrid Rank {i} | BM25 Score={score:.4f} | Source={doc.metadata.get('source', 'unknown')}"
        )

    logger.info("Hybrid search completed")

    return final_docs