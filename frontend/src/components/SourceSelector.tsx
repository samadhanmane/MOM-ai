import React, { useState, useRef } from "react";
import { Upload, PlaySquare, FileAudio, FileVideo, X, Globe, Sparkles, AlertCircle, ArrowRight } from "lucide-react";
import type { AnalyzePayload } from "../types/analysis";

interface SourceSelectorProps {
  onAnalyze: (payload: AnalyzePayload) => void;
  isLoading: boolean;
  error?: string | null;
}

export const SourceSelector: React.FC<SourceSelectorProps> = ({ onAnalyze, isLoading, error }) => {
  const [mode, setMode] = useState<"file" | "youtube">("file");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [youtubeUrl, setYoutubeUrl] = useState<string>("");
  const [language, setLanguage] = useState<"english" | "hinglish">("english");
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateAndSetFile = (file: File) => {
    const validExts = [".mp4", ".mp3", ".wav", ".m4a", ".webm", ".mov"];
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!validExts.includes(ext)) {
      setValidationError(`Unsupported file type '${ext}'. Allowed: ${validExts.join(", ")}`);
      return;
    }
    setValidationError(null);
    setSelectedFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (mode === "file") {
      if (!selectedFile) {
        setValidationError("Please select or drop an audio/video file first.");
        return;
      }
      onAnalyze({ file: selectedFile, language });
    } else {
      if (!youtubeUrl.trim()) {
        setValidationError("Please enter a valid YouTube URL.");
        return;
      }
      if (!youtubeUrl.toLowerCase().includes("youtube.com") && !youtubeUrl.toLowerCase().includes("youtu.be")) {
        setValidationError("URL must be a valid YouTube link (e.g. https://www.youtube.com/watch?v=...)");
        return;
      }
      onAnalyze({ source: youtubeUrl.trim(), language });
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  return (
    <div className="w-full max-w-3xl mx-auto glass-panel rounded-3xl p-8 border border-white/10 shadow-2xl relative z-10">
      {/* Tab Controls */}
      <div className="flex p-1.5 bg-slate-900/90 rounded-2xl border border-white/5 mb-8">
        <button
          type="button"
          onClick={() => { setMode("file"); setValidationError(null); }}
          className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-medium text-sm transition-all ${
            mode === "file"
              ? "bg-indigo-600/90 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
              : "text-slate-400 hover:text-white hover:bg-white/5"
          }`}
        >
          <Upload className="w-4 h-4" />
          <span>Upload Audio / Video</span>
        </button>
        <button
          type="button"
          onClick={() => { setMode("youtube"); setValidationError(null); }}
          className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-medium text-sm transition-all ${
            mode === "youtube"
              ? "bg-indigo-600/90 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
              : "text-slate-400 hover:text-white hover:bg-white/5"
          }`}
        >
          <PlaySquare className="w-4 h-4 text-red-400" />
          <span>YouTube URL</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {mode === "file" ? (
          /* Drag and Drop Zone */
          <div className="space-y-4">
            {!selectedFile ? (
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
                  dragActive
                    ? "border-indigo-400 bg-indigo-500/10 scale-[1.01]"
                    : "border-slate-700/80 hover:border-indigo-500/50 hover:bg-slate-900/50"
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".mp4,.mp3,.wav,.m4a,.webm,.mov"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mx-auto mb-4 text-indigo-400">
                  <Upload className="w-8 h-8" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-1">
                  Drop your video or audio file here
                </h3>
                <p className="text-sm text-slate-400 mb-4">
                  or <span className="text-indigo-400 underline font-medium">browse files</span> from your computer
                </p>
                <p className="text-xs text-slate-500">
                  Supported formats: MP4, MP3, WAV, M4A, WEBM, MOV
                </p>
              </div>
            ) : (
              /* Selected File Preview Card */
              <div className="glass-panel p-5 rounded-2xl flex items-center justify-between border border-indigo-500/30 bg-indigo-500/5">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-indigo-500/20 text-indigo-300 flex items-center justify-center">
                    {selectedFile.type.startsWith("video") ? (
                      <FileVideo className="w-6 h-6" />
                    ) : (
                      <FileAudio className="w-6 h-6" />
                    )}
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white truncate max-w-xs sm:max-w-md">
                      {selectedFile.name}
                    </h4>
                    <p className="text-xs text-slate-400">
                      {formatFileSize(selectedFile.size)} • {selectedFile.type || "Audio/Video"}
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedFile(null)}
                  className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        ) : (
          /* YouTube URL Input */
          <div className="space-y-3">
            <label className="block text-sm font-medium text-slate-300">
              Paste YouTube Video Link
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                <PlaySquare className="w-5 h-5 text-red-500" />
              </div>
              <input
                type="url"
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="w-full pl-12 pr-4 py-4 rounded-2xl bg-slate-900/90 border border-slate-700/80 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all text-sm"
              />
            </div>
            <p className="text-xs text-slate-500">
              Supports public YouTube video links. Audio will be automatically extracted and processed.
            </p>
          </div>
        )}

        {/* Language Selector */}
        <div className="pt-2">
          <label className="block text-sm font-medium text-slate-300 mb-2 flex items-center gap-2">
            <Globe className="w-4 h-4 text-indigo-400" />
            <span>Select Transcription Language</span>
          </label>
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => setLanguage("english")}
              className={`p-4 rounded-2xl border text-left transition-all ${
                language === "english"
                  ? "bg-indigo-600/20 border-indigo-500/60 text-white"
                  : "bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700"
              }`}
            >
              <div className="font-semibold text-sm mb-0.5">English</div>
              <div className="text-xs text-slate-400">Standard Whisper model</div>
            </button>

            <button
              type="button"
              onClick={() => setLanguage("hinglish")}
              className={`p-4 rounded-2xl border text-left transition-all ${
                language === "hinglish"
                  ? "bg-indigo-600/20 border-indigo-500/60 text-white"
                  : "bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700"
              }`}
            >
              <div className="font-semibold text-sm mb-0.5">Hinglish / Hindi</div>
              <div className="text-xs text-slate-400">Sarvam AI STT Translation</div>
            </button>
          </div>
        </div>

        {/* Validation / Error Messages */}
        {(validationError || error) && (
          <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 flex items-center gap-3 text-red-300 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{validationError || error}</span>
          </div>
        )}

        {/* CTA Analyze Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-4 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold shadow-xl shadow-indigo-600/30 hover:shadow-indigo-600/50 transition-all flex items-center justify-center gap-2 group disabled:opacity-50 disabled:cursor-not-allowed text-base"
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Initiating AI Pipeline...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5 group-hover:scale-110 transition-transform" />
              <span>Analyze Video Intelligence</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </>
          )}
        </button>
      </form>
    </div>
  );
};
