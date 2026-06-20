gradio Q/A ui : http://127.0.0.1:7860/
evaluation metric ui: http://127.0.0.1:7861/
Swagger ui : http://127.0.0.1:8000/

docker compose down

docker compose build --no-cache

docker compose up

Good news: Docker, FastAPI, Gradio, Chroma are all working.

Verify Ollama on your host

On your laptop run:

ollama list

curl http://localhost:11434/api/tags

The next steps after Ollama connectivity are:

1. Docker Compose
✓ done

2. FastAPI
✓ done

3. Ollama container connectivity
(current task)

4. Logging

5. Guardrails

6. Langfuse monitoring

7. JWT authentication

8. CI/CD

9. Kubernetes deployment

We have---------
✓ RAG
✓ Evaluation metrics (MRR, nDCG)
✓ FastAPI
✓ Gradio UI
✓ Chroma DB
✓ Docker
✓ Ollama integration
✓ Docker Compose

Even better: measure latency

//------again
docker compose down
docker compose up --build

If you changed only Python code and not requirements.txt or Dockerfile, you can also use:

docker compose up --build -d

docker compose logs -f pet-rag-api

Quick tip

For development, add this volume mount to the API service:

volumes:
  - ./app:/app/app

Then code changes are reflected immediately and you won't need a full image rebuild every time.

For now, since you're still learning the deployment flow, continue with:

docker compose down
docker compose up --build

// first feedback store in jsonl file, later will store in db
test feedback:
{
  "question": "How often should I groom my dog?",
  "answer": "You should groom based on coat type...",
  "rating": "thumbs_up",
  "comment": "Good answer"
}

How would you improve your RAG system?

You can answer:

I implemented a feedback collection API to capture user ratings and comments. Initially feedback is stored in JSONL files for simplicity. In production I would persist feedback into a database and use it to identify retrieval failures, low-quality answers, hallucinations, and opportunities to improve the knowledge base and evaluation datasets.

//----------------------------------
Final flow
User asks question
↓
FastAPI /ask
↓
Answer returned
↓
Question + Answer stored in feedback_state
↓
User clicks 👍
↓
FastAPI /feedback
↓
feedback.jsonl updated
↓
"Feedback saved: thumbs_up"

//-------------------------------------------

I would move to Guardrails because that is one of the key requirements explicitly mentioned in the job description ("safe and trustworthy AI behavior", "handling uncertainty", "preventing unsafe or medical-diagnostic outputs").

Your current retrieval is only:

Vector search

Upgrade to:

Vector search + keyword search


“After building RAG, feedback, and guardrails, I improved retrieval quality by adding hybrid search using semantic vector retrieval plus BM25 keyword search, then validated the improvement using MRR and nDCG.”

//--------------------------------------------//
In requirements.txt:

rank-bm25
Step 2: Create app/hybrid_retriever.py

This file will:

Load documents
Run vector search
Run BM25 keyword search
Merge results
Return top chunks
Step 3: Update mypetanswer.py

//------------------------------------------------------//

Better design

For local Docker demo:

Retrieval evaluation: run all 50 tests
Answer evaluation: run 3 to 5 tests only

For production:

Run answer evaluation as a background batch job
Store results
Dashboard reads saved results

So your immediate fix is:

Limit answer evaluation to 5 tests
//--------------------------------------------//

Next add reranker.

You now have:

✓ RAG
✓ FastAPI
✓ Docker
✓ Gradio UI
✓ Feedback
✓ Guardrails
✓ Hybrid retrieval
✓ Evaluation dashboard

Now improve retrieval quality with:

Vector search top 20
↓
Reranker
↓
Best 5 chunks
↓
//------------------------------------------------//
For an AI Engineer interview, your project already demonstrates:

✅ RAG
✅ Hybrid Search (Vector + BM25)
✅ Reranking
✅ Evaluation Metrics (MRR, nDCG)
✅ LLM-as-a-Judge
✅ FastAPI
✅ Docker
✅ Gradio
✅ Feedback Collection
✅ Guardrails

This is already stronger than what many candidates bring.

The next major production-grade additions I'd prioritize are:

Cross-encoder reranker (you're doing this now)
Observability (Prometheus/Grafana)
LangSmith tracing
Feedback-driven evaluation
CI/CD pipeline
Authentication for /admin/evaluator
Streaming responses from FastAPI to UI

Those would move the project from "good RAG demo" to "production-ready AI platform."

//-------recommended order-------------//
1. Basic API logging
2. Metrics endpoint
3. Prometheus metrics
4. LangSmith or Langfuse tracing

Track every RAG request:

question
retrieved sources
reranker scores
answer
latency
feedback
model name

Add to requirements.txt:

langfuse
//------------------
cross-encoder/ms-marco-MiniLM-L-6-v2 is one of the most popular reranking models used in production RAG systems. It is not an LLM. It is a specialized ranking model whose only job is to answer:

"Given this question and this document chunk, how relevant is this chunk?"

//------current RAG architecture pipeline---------------//
User Question
       │
       ▼
Vector Search
(all-MiniLM-L6-v2)
       │
       ▼
Top 20 Chunks
       │
       ▼
BM25 Hybrid
       │
       ▼
Cross Encoder
(ms-marco-MiniLM-L-6-v2)
       │
       ▼
Top 5 Chunks
       │
       ▼
Llama 3.2

//-------------------------
Langfuse is an open-source LLM engineering and observability platform. It is primarily used to monitor, debug, and optimize Generative AI and Large Language Model (LLM) applications

//-------------------------------------------
✓ RAG
✓ Docker
✓ Ollama
✓ Hybrid Search
✓ Reranker
✓ Evaluation Dashboard
✓ Feedback API
✓ Langfuse Tracing

NEXT:

✓ Langfuse Scores
✓ Feedback Analytics
✓ Prompt Management
✓ Production Monitoring Dashboard

From your screenshot I can see:

✅ Trace created
✅ Question tracked
✅ Retrieved document count = 5
✅ Sources captured
✅ Latency captured (2m48s)
✅ Metadata visible in Langfuse

//---------------------------------
What this gives you

Today Langfuse is showing:

Question
Sources
Reranker scores
Response time

After this change Langfuse will also store:

Metric	Example
MRR	0.675
nDCG	0.681
Coverage	72.5
Accuracy	4.0
Completeness	3.0
Relevance	4.8

//------------------
Step 1 — LLM Span
That gives Langfuse a separate child span for the LLM call.
Step 2 — Langfuse Scores for Evaluation
Step 3 — Feedback Scores

Change file: app/main.py
Step 4 — Feedback Analytics
Step 5 — Prompt Management / make prompt dynamic

What it gives you is:

✅ Prompt versioning
✅ Prompt history
✅ No redeploy for prompt changes
✅ Traceability in Langfuse
✅ Enterprise-grade AI operations

Langfuse available
    ↓
Use managed prompt

Langfuse unavailable
    ↓
Use local prompt
//--------------------
User
  ↓
FastAPI
  ↓
Hybrid Retrieval
  ↓
Reranker
  ↓
Langfuse Prompt
  ↓
LLM
  ↓
Answer

//--------------------
You now have:

✅ Retrieval Metrics (MRR, nDCG, Coverage)
✅ Answer Metrics (Accuracy, Completeness, Relevance)
✅ User Feedback Collection
✅ Feedback Analytics Dashboard
✅ Langfuse Tracing
✅ Dynamic Prompt Management
✅ Hybrid Search
✅ Reranking

//-------------------------------

Langfuse is for AI observability:

Question → retrieved docs → reranker scores → prompt → answer → latency → feedback

It helps debug RAG quality.

Prometheus/Grafana is for application/platform monitoring:

API requests/minute
500 error rate
CPU/memory
container health
endpoint latency
traffic spikes
service uptime

//---------------------------
Without trace_id:

Feedback
   ↓
Question

With trace_id:

Feedback
   ↓
Trace
   ↓
Prompt version
Retrieved docs
Reranker scores
Latency
Model
Token usage
Output