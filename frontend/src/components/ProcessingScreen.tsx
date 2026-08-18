import React, { useEffect } from "react";
import { CheckCircle2, Loader2, AlertTriangle, FileAudio, Mic, FileText, Lightbulb, Database, Sparkles } from "lucide-react";
import type { AnalysisStage, AnalysisStatus } from "../types/analysis";

interface ProcessingScreenProps {
  status: AnalysisStatus | null;
  onCompleted: () => void;
  onError: (err: string) => void;
}

interface StageStep {
  key: AnalysisStage;
  label: string;
  description: string;
  icon: React.ElementType;
}

const STAGES: StageStep[] = [
  {
    key: "processing_audio",
    label: "01 Audio Processing",
    description: "Downloading & converting audio to 16kHz WAV format",
    icon: FileAudio,
  },
  {
    key: "transcribing",
    label: "02 Transcribing",
    description: "Speech-to-text transcription via Whisper/Sarvam AI",
    icon: Mic,
  },
  {
    key: "summarizing",
    label: "03 Summarizing",
    description: "Generating executive summary & video title",
    icon: FileText,
  },
  {
    key: "extracting_insights",
    label: "04 Extracting Insights",
    description: "Mining action items, key decisions & open questions",
    icon: Lightbulb,
  },
  {
    key: "building_rag",
    label: "05 Knowledge Base",
    description: "Generating vector embeddings & ChromaDB indexing",
    icon: Database,
  },
];

export const ProcessingScreen: React.FC<ProcessingScreenProps> = ({ status, onCompleted, onError }) => {
  const currentStage = status?.status || "processing_audio";

  useEffect(() => {
    if (status?.status === "completed") {
      onCompleted();
    } else if (status?.status === "error") {
      onError(status.message || "An unexpected error occurred during processing.");
    }
  }, [status, onCompleted, onError]);

  const getStageState = (stageKey: AnalysisStage): "completed" | "current" | "waiting" => {
    if (currentStage === "completed") return "completed";
    if (currentStage === "error") return "waiting";

    const stageOrder: AnalysisStage[] = [
      "uploading",
      "processing_audio",
      "transcribing",
      "summarizing",
      "extracting_insights",
      "building_rag",
      "completed",
    ];

    const currentIndex = stageOrder.indexOf(currentStage);
    const targetIndex = stageOrder.indexOf(stageKey);

    if (targetIndex < currentIndex) return "completed";
    if (targetIndex === currentIndex) return "current";
    return "waiting";
  };

  return (
    <div className="w-full max-w-3xl mx-auto glass-panel rounded-3xl p-8 sm:p-10 border border-white/10 shadow-2xl relative z-10 space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5 animate-spin" />
          <span>Real-time AI Pipeline</span>
        </div>
        <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          AI is analyzing your video...
        </h2>
        <p className="text-slate-400 text-sm max-w-md mx-auto">
          Please stay on this page while our models transcribe, analyze, and build your meeting intelligence.
        </p>
      </div>

      {/* Stage Tracker Steps */}
      <div className="space-y-4 pt-2">
        {STAGES.map((step) => {
          const state = getStageState(step.key);
          const Icon = step.icon;

          return (
            <div
              key={step.key}
              className={`p-4 rounded-2xl border transition-all flex items-center gap-4 ${
                state === "current"
                  ? "bg-indigo-600/15 border-indigo-500/60 shadow-lg shadow-indigo-500/10"
                  : state === "completed"
                  ? "bg-slate-900/60 border-slate-800 text-slate-300"
                  : "bg-slate-900/20 border-slate-900 text-slate-600"
              }`}
            >
              {/* Icon Container */}
              <div
                className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${
                  state === "current"
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-500/30"
                    : state === "completed"
                    ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                    : "bg-slate-800/50 text-slate-600"
                }`}
              >
                {state === "current" ? (
                  <Loader2 className="w-6 h-6 animate-spin" />
                ) : state === "completed" ? (
                  <CheckCircle2 className="w-6 h-6" />
                ) : (
                  <Icon className="w-6 h-6" />
                )}
              </div>

              {/* Text info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h4 className={`text-sm font-semibold ${state === "current" ? "text-white" : state === "completed" ? "text-slate-200" : "text-slate-500"}`}>
                    {step.label}
                  </h4>
                  {state === "current" && (
                    <span className="text-[11px] font-medium text-indigo-400 px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 animate-pulse">
                      In Progress
                    </span>
                  )}
                  {state === "completed" && (
                    <span className="text-[11px] font-medium text-emerald-400">
                      Done
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-400 mt-0.5 truncate">
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Real-time backend status message bar */}
      {status?.message && (
        <div className="p-4 rounded-2xl bg-slate-900/90 border border-white/5 flex items-center gap-3 text-xs text-indigo-300">
          <Loader2 className="w-4 h-4 animate-spin text-indigo-400 shrink-0" />
          <span className="truncate">Current Status: {status.message}</span>
        </div>
      )}

      {/* Error display if failed */}
      {status?.status === "error" && (
        <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 flex items-center gap-3 text-red-300 text-sm">
          <AlertTriangle className="w-5 h-5 shrink-0 text-red-400" />
          <span>{status.message || "Pipeline processing encountered an error."}</span>
        </div>
      )}
    </div>
  );
};
