import os
from pathlib import Path
from langchain_core import messages
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, convert_to_messages
from langchain_core.documents import Document
from langchain_ollama import ChatOllama
import logging
from dotenv import load_dotenv
import time

from numpy import info
from app.guardrails import check_guardrails

from app.vector_store import vectorstore
from app.hybrid_retriever import hybrid_retrieve
from app.reranker import rerank_documents
from langfuse import observe, get_client
import uuid


#from week5.day3 import SYSTEM_PROMPT_TEMPLATE


load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#MODEL = "gpt-4.1-nano"
#MODEL = "ollama/llama3.2"#ChatOllama(model="llama3.2")

#from langchain_openai import ChatOpenAI




DB_NAME = str(Path(__file__).parent.parent / "vector_db")

#embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
RETRIEVAL_K = 6

SYSTEM_PROMPT = """
You are a knowledgeable, friendly assistant representing the company pet care department.
You are chatting with a user about pet care.
If relevant, use the given context to answer any question.
If you don't know the answer, say so.
Context:
{context}
"""

#vectorstore = Chroma(persist_directory=DB_NAME, embedding_function=embeddings)
retriever = vectorstore.as_retriever()
#llm = ChatOpenAI(temperature=0, model_name=MODEL)
#llm = ChatOllama(model="llama3.2", temperature=0)

# for docker setup-----
# llm = ChatOllama(
#     model="llama3.2",
#     temperature=0,
#     base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434")
# )

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

if LLM_PROVIDER == "groq":
    llm = ChatOpenAI(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"

        
    )
    logger.info("----------groq")
else:
    llm = ChatOllama(
        model="llama3.2",
        temperature=0,
        base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434")
    )




#-----------------------------------

def fetch_context(question: str) -> list[Document]:
    """
    Retrieve relevant context documents for a question.
    """
    return retriever.invoke(question, k=RETRIEVAL_K)


def combined_question(question: str, history: list[dict] = []) -> str:
    """
    Combine all the user's messages into a single string.
    """
    prior = "\n".join(m["content"] for m in history if m["role"] == "user")
    return prior + "\n" + question


@observe(name="pet-rag-question")
#def answer_question(question: str, history: list[dict] = []) -> tuple[str, list[Document]]:
def answer_question(question: str, history: list[dict] = []) -> tuple[str, list[Document], str | None]:    

    logger.info(f"Question: {question}")

    langfuse = get_client()
    app_trace_id = str(uuid.uuid4())

    langfuse.update_current_span(
        input={"question": question},
        metadata={"app_trace_id": app_trace_id}
    )

    guardrail_result = check_guardrails(question)

    if guardrail_result["blocked"]:
        logger.info("Guardrail triggered")

        langfuse.update_current_span(
            output={
                "answer": guardrail_result["answer"],
                "blocked": True,
                "reason": "guardrail_triggered"
            }
        )

        langfuse.flush()

        #return guardrail_result["answer"], []
        

        return guardrail_result["answer"], [], app_trace_id

    combined = combined_question(question, history)

    docs = hybrid_retrieve(combined)

    logger.info(f"Retrieved Docs Before Rerank: {len(docs)}")

    docs = rerank_documents(combined, docs, top_n=5)

    logger.info(f"Retrieved Docs After Rerank: {len(docs)}")

    langfuse.update_current_span(
        metadata={
            "retrieved_doc_count": len(docs),
            "sources": [
                doc.metadata.get("source", "unknown")
                for doc in docs
            ],
            "reranker_scores": [
                doc.metadata.get("reranker_score")
                for doc in docs
            ]
        }
    )

    for doc in docs:
        logger.info(f"Source={doc.metadata.get('source','unknown')}")

    context = "\n\n".join(doc.page_content for doc in docs)

    #system_prompt = SYSTEM_PROMPT.format(context=context)
    #---------------------------------------
    try:
        langfuse = get_client()

        prompt = langfuse.get_prompt(
            "pet-rag-system-prompt"
        )

        system_prompt = prompt.compile(
            context=context
        )

    except Exception as e:

        logger.warning(
            f"Prompt fetch failed: {e}"
        )

        system_prompt = SYSTEM_PROMPT.format(
            context=context
        )

    #----------------------------------------------

    messages = [SystemMessage(content=system_prompt)]
    messages.extend(convert_to_messages(history))
    messages.append(HumanMessage(content=question))

    start = time.time()

    response = llm.invoke(messages)

    elapsed = time.time() - start

    langfuse.update_current_span(
        output={
            "answer": response.content,
            "doc_count": len(docs),
            "llm_response_time_seconds": round(elapsed, 2)
        }
    )

    langfuse.flush()

    logger.info(f"LLM Response Time={elapsed:.2f} seconds")
    logger.info(f"Response Length={len(response.content)} chars")
    

    #return response.content, docs
    return response.content, docs, app_trace_id


#----------------------------------------------------------//
# def answer_question(question: str, history: list[dict] = []) -> tuple[str, list[Document]]:
#     """
#     Answer the given question with RAG; return the answer and the context documents.
#     """
#     combined = combined_question(question, history)
#     docs = fetch_context(combined)
#     context = "\n\n".join(doc.page_content for doc in docs)
#     system_prompt = SYSTEM_PROMPT.format(context=context)
#     messages = [SystemMessage(content=system_prompt)]
#     messages.extend(convert_to_messages(history))
#     messages.append(HumanMessage(content=question))
#     response = llm.invoke(messages)
#     return response.content, docs

