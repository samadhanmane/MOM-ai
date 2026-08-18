import os
import traceback
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarise, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain
from backend.services.session_service import session_service

def execute_analysis_pipeline(analysis_id: str, source: str, language: str = "english", is_temp_file: bool = False):
    """
    Executes the existing AI pipeline asynchronously, updating progress status in session_service.
    """
    try:
        # Step 1: Processing audio / video input
        session_service.update_status(
            analysis_id,
            status="processing_audio",
            message="Processing audio input and downloading/chunking source..."
        )
        chunks = process_input(source)

        # Step 2: Transcribing
        session_service.update_status(
            analysis_id,
            status="transcribing",
            message=f"Transcribing audio chunks using {'Sarvam AI' if language.lower() == 'hinglish' else 'Whisper'}..."
        )
        transcript = transcribe_all(chunks, language=language)

        # Step 3: Summarizing
        session_service.update_status(
            analysis_id,
            status="summarizing",
            message="Generating title and concise executive summary..."
        )
        title = generate_title(transcript)
        summary = summarise(transcript)

        # Step 4: Extracting Insights
        session_service.update_status(
            analysis_id,
            status="extracting_insights",
            message="Extracting action items, key decisions, and open questions..."
        )
        action_items = extract_action_items(transcript)
        decisions = extract_key_decisions(transcript)
        questions = extract_questions(transcript)

        # Step 5: Building RAG Knowledge Base
        session_service.update_status(
            analysis_id,
            status="building_rag",
            message="Building ChromaDB vector embeddings for interactive chat..."
        )
        rag_chain = build_rag_chain(transcript)

        # Store RAG chain in session service
        session_service.store_rag_chain(analysis_id, rag_chain)

        # Step 6: Complete
        result = {
            "analysis_id": analysis_id,
            "title": title,
            "transcript": transcript,
            "summary": summary,
            "action_items": action_items,
            "key_decisions": decisions,
            "open_questions": questions
        }
        session_service.set_result(analysis_id, result)

    except Exception as e:
        error_msg = f"Pipeline execution failed: {str(e)}"
        print(f"[Pipeline Error] {error_msg}")
        traceback.print_exc()
        session_service.set_error(analysis_id, error_msg)

    finally:
        # Clean up temporary uploaded file if applicable
        if is_temp_file and os.path.exists(source):
            try:
                os.remove(source)
            except Exception as clean_err:
                print(f"Failed to remove temporary file {source}: {clean_err}")
