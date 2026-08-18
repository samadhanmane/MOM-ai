import uuid
import os
import shutil
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel

from backend.services.session_service import session_service
from backend.services.pipeline_service import execute_analysis_pipeline

router = APIRouter(prefix="/api", tags=["Analysis"])

ALLOWED_EXTENSIONS = {".mp4", ".mp3", ".wav", ".m4a", ".webm", ".mov"}
TEMP_UPLOAD_DIR = "temp_uploads"
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

class YouTubeAnalysisRequest(BaseModel):
    source: str
    language: Optional[str] = "english"

@router.post("/analyze")
async def analyze_input(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    source: Optional[str] = Form(None),
    language: Optional[str] = Form("english"),
    json_payload: Optional[YouTubeAnalysisRequest] = None
):
    """
    Starts analysis pipeline for either uploaded audio/video file or YouTube URL.
    Returns analysis_id immediately for status polling.
    """
    target_source = None
    target_language = language or "english"
    is_temp = False

    # Case A: JSON Payload (YouTube URL)
    if json_payload and json_payload.source:
        target_source = json_payload.source.strip()
        target_language = json_payload.language or "english"

    # Case B: Form data YouTube URL
    elif source:
        target_source = source.strip()

    # Case C: File upload
    elif file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        
        safe_filename = f"{uuid.uuid4().hex}_{os.path.basename(file.filename)}"
        temp_path = os.path.join(TEMP_UPLOAD_DIR, safe_filename)
        
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            target_source = temp_path
            is_temp = True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save uploaded file: {str(e)}"
            )

    if not target_source:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either a file upload or a valid YouTube source URL."
        )

    analysis_id = str(uuid.uuid4())
    session_service.create_session(
        analysis_id=analysis_id,
        status="processing_audio",
        message="Starting video/audio analysis pipeline..."
    )

    # Launch pipeline in background thread
    background_tasks.add_task(
        execute_analysis_pipeline,
        analysis_id=analysis_id,
        source=target_source,
        language=target_language,
        is_temp_file=is_temp
    )

    return {
        "analysis_id": analysis_id,
        "status": "processing_audio",
        "message": "Analysis initiated. Poll /api/analysis/{analysis_id}/status for updates."
    }

@router.get("/analysis/{analysis_id}/status")
def get_analysis_status(analysis_id: str):
    """
    Returns current stage status for the given analysis session.
    """
    status_info = session_service.get_status(analysis_id)
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis session not found."
        )
    return status_info

@router.get("/analysis/{analysis_id}")
def get_analysis_result(analysis_id: str):
    """
    Returns the completed analysis results for the given analysis session.
    """
    result = session_service.get_result(analysis_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis session not found."
        )
    if result.get("status") != "completed":
        return result
    return result
