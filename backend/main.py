
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Add the ai-engine directory so the backend can import RAGEngine.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AI_ENGINE_PATH = PROJECT_ROOT / "ai-engine"

sys.path.insert(0, str(AI_ENGINE_PATH))

from rag_engine import RAGEngine  # noqa: E402

# Import authentication router
from backend.routers.auth import router as auth_router


# Initialize FastAPI application
app = FastAPI(
    title="MediAssist AI API",
    description="API for document-grounded medical question answering.",
    version="0.1.0",
)

# Register authentication routes
app.include_router(auth_router)

rag_engine = None


# Request and response schemas for RAG
class AskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="Question to answer using the available documents.",
    )


class SourceResponse(BaseModel):
    reference: int
    source: str
    page: int | None
    distance: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]


# Initialize RAG engine when application starts
@app.on_event("startup")
def initialize_rag_engine():
    global rag_engine

    try:
        rag_engine = RAGEngine()

        print("RAG engine initialized.")
        print(
            "ChromaDB path:",
            rag_engine.store.persist_directory,
        )
        print(
            "Collection count:",
            rag_engine.store.count(),
        )

    except Exception as exc:
        print(f"RAG engine initialization failed: {exc}")


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "rag_engine_ready": rag_engine is not None,
    }


# Existing RAG question-answering endpoint
@app.post("/api/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    if rag_engine is None:
        raise HTTPException(
            status_code=503,
            detail="The RAG engine is not ready. Check server logs and configuration.",
        )

    try:
        result = rag_engine.ask(request.question)

        return AskResponse(
            answer=result["answer"],
            sources=result["sources"],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(f"Question processing failed: {exc}")

        raise HTTPException(
            status_code=500,
            detail="The question could not be processed.",
        ) from exc
