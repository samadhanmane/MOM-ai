import React, { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { Hero } from "./components/Hero";
import { SourceSelector } from "./components/SourceSelector";
import { ProcessingScreen } from "./components/ProcessingScreen";
import { AnalysisDashboard } from "./components/AnalysisDashboard";
import type { AnalyzePayload, AnalysisStatus, AnalysisResult } from "./types/analysis";
import { api } from "./services/api";

type ViewState = "home" | "processing" | "dashboard";

export const App: React.FC = () => {
  const [viewState, setViewState] = useState<ViewState>("home");
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean>(true);

  // Check Backend Health on mount
  useEffect(() => {
    const verifyHealth = async () => {
      try {
        await api.checkHealth();
        setIsBackendHealthy(true);
      } catch (err) {
        setIsBackendHealthy(false);
      }
    };
    verifyHealth();
  }, []);

  // Polling loop when in "processing" state
  useEffect(() => {
    let intervalId: any = null;

    if (viewState === "processing" && analysisId) {
      const pollStatus = async () => {
        try {
          const statusData = await api.getAnalysisStatus(analysisId);
          setAnalysisStatus(statusData);

          if (statusData.status === "completed") {
            clearInterval(intervalId);
            // Fetch final analysis result
            const resultData = await api.getAnalysisResult(analysisId);
            setAnalysisResult(resultData);
            setViewState("dashboard");
          } else if (statusData.status === "error") {
            clearInterval(intervalId);
            setError(statusData.message || "Pipeline processing encountered an error.");
          }
        } catch (err: any) {
          console.error("Polling error:", err);
        }
      };

      // Initial poll immediately
      pollStatus();
      intervalId = setInterval(pollStatus, 3000);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [viewState, analysisId]);

  const handleStartAnalysis = async (payload: AnalyzePayload) => {
    setIsLoading(true);
    setError(null);

    try {
      const initialResponse = await api.startAnalysis(payload);
      setAnalysisId(initialResponse.analysis_id);
      setAnalysisStatus({
        analysis_id: initialResponse.analysis_id,
        status: "processing_audio",
        message: initialResponse.message,
      });
      setViewState("processing");
    } catch (err: any) {
      console.error("Analysis trigger error:", err);
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Failed to connect to backend server. Make sure the FastAPI backend is running on http://localhost:8000."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setViewState("home");
    setAnalysisId(null);
    setAnalysisStatus(null);
    setAnalysisResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 relative overflow-hidden flex flex-col">
      {/* Background Decorative Glow Blobs */}
      <div className="glow-blob-purple top-[-100px] left-[-100px]" />
      <div className="glow-blob-cyan bottom-[-150px] right-[-150px]" />

      {/* Navbar Header */}
      <Navbar 
        onNewAnalysis={viewState !== "home" ? handleReset : undefined} 
        isBackendHealthy={isBackendHealthy}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 relative z-10">
        {viewState === "home" && (
          <div className="space-y-10">
            <Hero />
            <SourceSelector 
              onAnalyze={handleStartAnalysis} 
              isLoading={isLoading} 
              error={error} 
            />
          </div>
        )}

        {viewState === "processing" && (
          <ProcessingScreen 
            status={analysisStatus} 
            onCompleted={() => {
              if (analysisId) {
                api.getAnalysisResult(analysisId).then((res) => {
                  setAnalysisResult(res);
                  setViewState("dashboard");
                });
              }
            }} 
            onError={(errMsg) => setError(errMsg)}
          />
        )}

        {viewState === "dashboard" && analysisResult && (
          <AnalysisDashboard 
            result={analysisResult} 
            onReset={handleReset} 
          />
        )}
      </main>

      {/* Simple Footer */}
      <footer className="glass-panel border-t border-white/5 py-6 px-6 text-center text-xs text-slate-500 mt-auto">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>© {new Date().getFullYear()} AI Video Assistant. Enterprise Meeting Intelligence.</span>
          <span className="text-slate-400 font-medium">Whisper • Sarvam AI • Mistral • ChromaDB</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
