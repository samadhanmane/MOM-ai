import React from "react";
import { Sparkles, Cpu, ShieldCheck, Zap } from "lucide-react";

export const Hero: React.FC = () => {
  return (
    <div className="text-center space-y-6 max-w-4xl mx-auto pt-6 pb-4">
      {/* Badge */}
      <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-panel border border-indigo-500/30 text-indigo-300 text-xs font-semibold uppercase tracking-wider shadow-lg shadow-indigo-500/10">
        <Sparkles className="w-4 h-4 text-indigo-400 animate-pulse" />
        <span>Enterprise Meeting Intelligence & RAG Platform</span>
      </div>

      {/* Main Title */}
      <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight sm:leading-none">
        Turn Any Video Into{" "}
        <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
          Actionable Intelligence
        </span>
      </h1>

      {/* Subtitle */}
      <p className="text-slate-400 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
        Upload a meeting recording or paste a YouTube URL. Get transcripts, executive summaries, decisions, action items, and an interactive RAG meeting assistant.
      </p>

      {/* Feature Highlights Pills */}
      <div className="flex flex-wrap items-center justify-center gap-6 pt-2 text-xs font-medium text-slate-400">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/60 border border-white/5">
          <Cpu className="w-4 h-4 text-indigo-400" />
          <span>Local Whisper & Sarvam AI STT</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/60 border border-white/5">
          <Zap className="w-4 h-4 text-purple-400" />
          <span>Mistral LCEL Pipeline</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/60 border border-white/5">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          <span>Chroma Vector RAG</span>
        </div>
      </div>
    </div>
  );
};
