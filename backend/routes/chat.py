from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from backend.services.session_service import session_service
from core.rag_engine import ask_question

router = APIRouter(prefix="/api", tags=["Chat"])

class ChatRequest(BaseModel):
    analysis_id: str
    question: str

@router.post("/chat")
def chat_with_meeting(payload: ChatRequest):
    """
    RAG Chat endpoint to ask questions about a processed meeting transcript.
    """
    if not payload.analysis_id or not payload.analysis_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="analysis_id is required."
        )

    if not payload.question or not payload.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty."
        )

    rag_chain = session_service.get_rag_chain(payload.analysis_id)
    if not rag_chain:
        # Check if session exists at all
        status_info = session_service.get_status(payload.analysis_id)
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis session not found."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"RAG knowledge base is not ready yet. Current status: {status_info.get('status')}"
        )

    try:
        answer = ask_question(rag_chain, payload.question.strip())
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process RAG chat question: {str(e)}"
        )
