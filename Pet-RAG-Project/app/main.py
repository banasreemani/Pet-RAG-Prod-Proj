from fastapi import FastAPI
from pydantic import BaseModel
from app.mypetanswer import answer_question

from datetime import datetime
from pathlib import Path
import json
from app.evaluation_service import run_retrieval_summary, run_answer_summary
import logging
from datetime import datetime, timezone
from langfuse import get_client

logger = logging.getLogger(__name__)


app = FastAPI(title="Pet RAG API")

class AskRequest(BaseModel):
    question: str

# class AskResponse(BaseModel):
#     answer: str
#     sources: list[str] = []
#     contexts: list[str] = []

class AskResponse(BaseModel):
    answer: str
    trace_id: str
    sources: list[str] = []
    contexts: list[str] = []

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: str
    comment: str | None = None
    trace_id: str | None = None #new add

@app.get("/metrics")
def metrics():
    return run_retrieval_summary()    

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics/retrieval")
def retrieval_metrics():
    return run_retrieval_summary()

@app.get("/metrics/answers")
def answer_metrics():
    return run_answer_summary()    

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    #answer, docs = answer_question(request.question)
    answer, docs, trace_id = answer_question(request.question)

    sources = []
    contexts = []

    for doc in docs:
        sources.append(doc.metadata.get("source", "unknown"))
        contexts.append(doc.page_content)
        print("DOCS RETURNED:", len(docs))
    print("FIRST DOC:", docs[0].page_content[:200] if docs else "NO DOCS")

    # return AskResponse(
    #     answer=answer,
    #     sources=sources,
    #     contexts=contexts
    # )

    return AskResponse(
    answer=answer,
    trace_id=trace_id,
    sources=sources,
    contexts=contexts
    )

# @app.post("/feedback")
# def feedback(request: FeedbackRequest):
#     feedback_file = Path("feedback/feedback.jsonl")
#     feedback_file.parent.mkdir(exist_ok=True)

#     record = {
#         "timestamp": datetime.utcnow().isoformat(),
#         "question": request.question,
#         "answer": request.answer,
#         "rating": request.rating,
#         "comment": request.comment
#     }

#     with feedback_file.open("a", encoding="utf-8") as f:
#         f.write(json.dumps(record) + "\n")

#     return {"status": "saved"}   

@app.post("/feedback")
def feedback(request: FeedbackRequest):
    feedback_file = Path("feedback/feedback.jsonl")
    feedback_file.parent.mkdir(exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": request.question,
        "answer": request.answer,
        "rating": request.rating,
        "trace_id": request.trace_id,
        "comment": request.comment
    }

    with feedback_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    langfuse = get_client()
    score_value = 1 if request.rating == "thumbs_up" else 0

    try:
        langfuse.create_score(
            name="user_feedback",
            value=score_value,
            comment=request.comment or ""
        )
        langfuse.flush()
    except Exception as e:
        logger.warning(f"Langfuse feedback score failed: {e}")

    return {"status": "saved"}


@app.get("/feedback/summary")
def feedback_summary():
    feedback_file = Path("feedback/feedback.jsonl")

    if not feedback_file.exists():
        return {
            "total": 0,
            "thumbs_up": 0,
            "thumbs_down": 0,
            "positive_rate": 0
        }

    thumbs_up = 0
    thumbs_down = 0
    total = 0

    with feedback_file.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            total += 1

            if record.get("rating") == "thumbs_up":
                thumbs_up += 1
            elif record.get("rating") == "thumbs_down":
                thumbs_down += 1

    positive_rate = (thumbs_up / total * 100) if total else 0

    return {
        "total": total,
        "thumbs_up": thumbs_up,
        "thumbs_down": thumbs_down,
        "positive_rate": round(positive_rate, 2)
    }

@app.get("/feedback/recent")
def feedback_recent(limit: int = 20):
    feedback_file = Path("feedback/feedback.jsonl")

    if not feedback_file.exists():
        return []

    records = []

    with feedback_file.open("r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    return records[-limit:]    