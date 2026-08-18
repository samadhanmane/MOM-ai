import axios from "axios";
import type { AnalysisResult, AnalysisStatus, AnalyzePayload } from "../types/analysis";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 mins timeout
});

export const api = {
  async checkHealth(): Promise<{ status: string; service: string }> {
    const response = await apiClient.get("/api/health");
    return response.data;
  },

  async startAnalysis(payload: AnalyzePayload): Promise<{ analysis_id: string; status: string; message: string }> {
    if (payload.file) {
      const formData = new FormData();
      formData.append("file", payload.file);
      formData.append("language", payload.language);

      const response = await apiClient.post("/api/analyze", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    } else if (payload.source) {
      const response = await apiClient.post("/api/analyze", {
        source: payload.source,
        language: payload.language,
      });
      return response.data;
    }

    throw new Error("Either a file or a YouTube source URL must be provided.");
  },

  async getAnalysisStatus(analysisId: string): Promise<AnalysisStatus> {
    const response = await apiClient.get(`/api/analysis/${analysisId}/status`);
    return response.data;
  },

  async getAnalysisResult(analysisId: string): Promise<AnalysisResult> {
    const response = await apiClient.get(`/api/analysis/${analysisId}`);
    return response.data;
  },

  async sendChatMessage(analysisId: string, question: string): Promise<{ answer: string }> {
    const response = await apiClient.post("/api/chat", {
      analysis_id: analysisId,
      question: question,
    });
    return response.data;
  },
};
