from typing import Dict, Any, Optional
import threading

class SessionService:
    def __init__(self):
        self._lock = threading.Lock()
        self._analysis_sessions: Dict[str, Dict[str, Any]] = {}
        self._rag_sessions: Dict[str, Any] = {}

    def create_session(self, analysis_id: str, status: str = "uploading", message: str = "Initializing session") -> Dict[str, Any]:
        with self._lock:
            session = {
                "analysis_id": analysis_id,
                "status": status,
                "message": message,
                "result": None,
                "error": None
            }
            self._analysis_sessions[analysis_id] = session
            return session

    def update_status(self, analysis_id: str, status: str, message: str) -> None:
        with self._lock:
            if analysis_id in self._analysis_sessions:
                self._analysis_sessions[analysis_id]["status"] = status
                self._analysis_sessions[analysis_id]["message"] = message

    def set_result(self, analysis_id: str, result: Dict[str, Any]) -> None:
        with self._lock:
            if analysis_id in self._analysis_sessions:
                self._analysis_sessions[analysis_id]["status"] = "completed"
                self._analysis_sessions[analysis_id]["message"] = "Analysis completed successfully"
                self._analysis_sessions[analysis_id]["result"] = result

    def set_error(self, analysis_id: str, error_message: str) -> None:
        with self._lock:
            if analysis_id in self._analysis_sessions:
                self._analysis_sessions[analysis_id]["status"] = "error"
                self._analysis_sessions[analysis_id]["message"] = error_message
                self._analysis_sessions[analysis_id]["error"] = error_message

    def get_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            session = self._analysis_sessions.get(analysis_id)
            if not session:
                return None
            return {
                "analysis_id": session["analysis_id"],
                "status": session["status"],
                "message": session["message"],
                "error": session.get("error")
            }

    def get_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            session = self._analysis_sessions.get(analysis_id)
            if not session:
                return None
            if session["status"] != "completed":
                return {
                    "analysis_id": analysis_id,
                    "status": session["status"],
                    "message": session["message"]
                }
            res = session["result"].copy() if session["result"] else {}
            res["analysis_id"] = analysis_id
            res["status"] = "completed"
            return res

    def store_rag_chain(self, analysis_id: str, rag_chain: Any) -> None:
        with self._lock:
            self._rag_sessions[analysis_id] = rag_chain

    def get_rag_chain(self, analysis_id: str) -> Any:
        with self._lock:
            return self._rag_sessions.get(analysis_id)

session_service = SessionService()
