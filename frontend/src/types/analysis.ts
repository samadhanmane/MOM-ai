export type AnalysisStage = 
  | "uploading"
  | "processing_audio"
  | "transcribing"
  | "summarizing"
  | "extracting_insights"
  | "building_rag"
  | "completed"
  | "error";

export interface AnalysisStatus {
  analysis_id: string;
  status: AnalysisStage;
  message: string;
  error?: string;
}

export interface AnalysisResult {
  analysis_id: string;
  title: string;
  transcript: string;
  summary: string;
  action_items: string;
  key_decisions: string;
  open_questions: string;
  status: "completed";
}

export interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  timestamp: string;
}

export interface AnalyzePayload {
  file?: File;
  source?: string;
  language: "english" | "hinglish";
}
