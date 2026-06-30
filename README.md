# Medium link
https://medium.com/@banasree.mani/building-a-production-ready-rag-system-end-to-end-dc5ad6f5b415
# Pet Care RAG Assistant

A production-style Retrieval-Augmented Generation (RAG) application for pet care knowledge retrieval and question answering.

The project combines Hybrid Search, Cross-Encoder Reranking, Dynamic Prompt Management, Feedback Analytics, Evaluation Frameworks, and Observability to demonstrate how modern AI applications can be built beyond simple chatbot prototypes.

---

# Features

## AI & RAG

* Retrieval-Augmented Generation (RAG)
* Hybrid Search

  * Dense Vector Search
  * BM25 Keyword Search
* Cross-Encoder Reranking
* Dynamic Prompt Management using Langfuse
* Context-Aware Question Answering
* Hallucination Reduction through Grounded Retrieval

## Evaluation

* Mean Reciprocal Rank (MRR)
* Normalized Discounted Cumulative Gain (nDCG)
* Keyword Coverage
* Answer Accuracy
* Answer Completeness
* Answer Relevance

## Observability

* Langfuse Tracing
* Prompt Versioning
* Prompt Experiments
* Retrieval Metadata Tracking
* LLM Response Time Monitoring
* Source Document Tracking

## User Feedback

* Helpful / Not Helpful Feedback
* Feedback Comments
* Feedback Analytics Dashboard
* Trace ID Correlation
* Negative Feedback Analysis

## Safety

* Input Guardrails
* Out-of-Scope Question Detection
* Safety Filtering
* Medical Advice Restrictions

---

# Architecture

```text
+-------------------+
|   Gradio UI       |
+---------+---------+
          |
          v
+-------------------+
|   FastAPI Layer   |
+---------+---------+
          |
          v
+-------------------+
|    Guardrails     |
+---------+---------+
          |
          v
+-------------------+
|  Hybrid Retriever |
| Vector + BM25     |
+---------+---------+
          |
          v
+-------------------+
| Cross Encoder     |
| Reranker          |
+---------+---------+
          |
          v
+-------------------+
| Dynamic Prompt    |
| (Langfuse)        |
+---------+---------+
          |
          v
+-------------------+
| Ollama / Llama3.2 |
+---------+---------+
          |
          v
+-------------------+
| Final Response    |
+-------------------+

Feedback Flow
----------------------------------

User Feedback
      |
      v
feedback.jsonl
      |
      v
Feedback Dashboard
      |
      v
Negative Feedback Analysis

Observability Flow
----------------------------------

Application
      |
      v
Langfuse
      |
      v
Traces
Prompts
Experiments
Evaluations
```

---

# Technology Stack

## Backend

* Python 3.11
* FastAPI
* Pydantic

## Frontend

* Gradio

## LLM

* Ollama
* Llama 3.2

## Retrieval

* LangChain
* ChromaDB
* HuggingFace Embeddings
* BM25

## Ranking

* Cross Encoder Reranker
* Sentence Transformers

## Observability

* Langfuse

## Deployment

* Docker
* Docker Compose

---

# Project Structure

```text
pet-rag-project/

├── app/
│   ├── main.py
│   ├── mypetanswer.py
│   ├── guardrails.py
│   ├── hybrid_retriever.py
│   ├── reranker.py
│   ├── vector_store.py
│   ├── evaluation_service.py
│
├── evaluation/
│   ├── eval.py
│   ├── retrieval_tests.py
│   └── answer_tests.py
│
├── feedback/
│   └── feedback.jsonl
│
├── vector_db/
│
├── knowledge-base/
│
├── gradio_ui.py
├── evaluator.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Running Locally

## Clone Repository

```bash
git clone <repository-url>

cd pet-rag-project
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Start Ollama

```bash
ollama serve

ollama pull llama3.2
```

## Run API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run UI

```bash
python gradio_ui.py
```

## Run Evaluator

```bash
python evaluator.py
```

---

# Docker Deployment

## Build

```bash
docker compose build
```

## Start

```bash
docker compose up -d
```

## Logs

```bash
docker compose logs -f
```

## Stop

```bash
docker compose down
```

---

# API Endpoints

## Health

```http
GET /health
```

## Ask Question

```http
POST /ask
```

Request:

```json
{
  "question": "What should I feed my puppy?"
}
```

Response:

```json
{
  "answer": "...",
  "trace_id": "...",
  "sources": [],
  "contexts": []
}
```

## Submit Feedback

```http
POST /feedback
```

Request:

```json
{
  "question": "...",
  "answer": "...",
  "rating": "thumbs_up",
  "trace_id": "...",
  "comment": "Helpful answer"
}
```

## Feedback Summary

```http
GET /feedback/summary
```

---

# Evaluation Metrics

## Retrieval Metrics

### Mean Reciprocal Rank (MRR)

Measures how highly the correct document is ranked.

### nDCG

Measures ranking quality of retrieved documents.

### Keyword Coverage

Measures retrieval completeness.

---

## Answer Metrics

### Accuracy

Is the answer factually correct?

### Completeness

Does the answer fully address the question?

### Relevance

Is the answer relevant to the user query?

---

# Feedback Analytics Dashboard

The dashboard provides:

* Total Feedback
* Positive Feedback Count
* Negative Feedback Count
* Positive Rate
* Recent Feedback
* Top Negative Questions
* Recent Negative Feedback
* Trace ID Correlation

---

# Langfuse Integration

The project uses Langfuse for:

* Prompt Management
* Prompt Versioning
* Dynamic Prompts
* Tracing
* LLM Observability
* Experimentation
* Evaluation Analysis

---

# Future Enhancements

* Authentication & Authorization
* Admin Dashboard
* Prompt A/B Testing
* Multi-Model Routing
* Query Classification
* Feedback-to-Prompt Learning Loop
* Automated Evaluation Scheduling
* Prometheus Integration
* Grafana Dashboards
* Kubernetes Deployment

---

# Author

Banasree Ghosh

Technical Architect | Distributed Systems | AI Engineering | Platform Architecture
