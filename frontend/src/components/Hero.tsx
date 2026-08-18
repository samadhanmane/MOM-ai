import React from "react";
import { Sparkles, Cpu, ShieldCheck, Zap } from "lucide-react";

export const Hero: React.FC = () => {
  return (
    <div className="text-center space-y-6 max-w-4xl mx-auto pt-8 pb-4 relative z-10">
      {/* Top Badge */}
      <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full glass-panel border border-indigo-500/30 text-indigo-300 text-xs font-semibold uppercase tracking-wider shadow-xl shadow-indigo-500/10">
        <Sparkles className="w-4 h-4 text-indigo-400 animate-pulse" />
        <span>MOM AI — Autonomous Meeting Intelligence & RAG</span>
      </div>

      {/* Main Headline */}
      <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight sm:leading-[1.15]">
        Turn Any Video & Audio Into{" "}
        <span className="text-gradient-purple">
          Actionable Intelligence
        </span>
      </h1>

      {/* Subtitle */}
      <p className="text-slate-300 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
        Upload meeting recordings or paste a YouTube URL. Extract structured summaries, action items, key decisions, open questions, and search meeting context with AI RAG.
      </p>

      {/* Feature Highlights */}
      <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6 pt-3 text-xs font-medium text-slate-300">
        <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900/80 border border-white/10 shadow-sm">
          <Cpu className="w-4 h-4 text-indigo-400" />
          <span>Whisper & Sarvam AI STT</span>
        </div>
        <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900/80 border border-white/10 shadow-sm">
          <Zap className="w-4 h-4 text-purple-400" />
          <span>Mistral LCEL Pipeline</span>
        </div>
        <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900/80 border border-white/10 shadow-sm">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          <span>Chroma Vector RAG Engine</span>
        </div>
      </div>
    </div>
  );
};
