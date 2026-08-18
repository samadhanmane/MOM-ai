import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { 
  FileText, Lightbulb, CheckSquare, HelpCircle, MessageSquare, Search, Copy, Check, Send, 
  Sparkles, Bot, User, ArrowLeft, ShieldCheck, ListOrdered 
} from "lucide-react";
import type { AnalysisResult, ChatMessage } from "../types/analysis";
import { api } from "../services/api";

interface AnalysisDashboardProps {
  result: AnalysisResult;
  onReset: () => void;
}

export const AnalysisDashboard: React.FC<AnalysisDashboardProps> = ({ result, onReset }) => {
  const [activeTab, setActiveTab] = useState<"overview" | "insights" | "transcript" | "chat">("overview");
  
  // Transcript search state
  const [searchQuery, setSearchQuery] = useState("");
  const [copied, setCopied] = useState(false);

  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      sender: "assistant",
      text: "Hello! I am your AI Meeting Assistant. Ask me anything about this meeting's transcript, decisions, or action items.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [questionInput, setQuestionInput] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (activeTab === "chat") {
      scrollToBottom();
    }
  }, [chatMessages, activeTab]);

  const handleCopyTranscript = () => {
    navigator.clipboard.writeText(result.transcript);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSendQuestion = async (queryText?: string) => {
    const questionText = queryText || questionInput;
    if (!questionText.trim() || isChatLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: "user",
      text: questionText.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setChatMessages((prev) => [...prev, userMsg]);
    if (!queryText) setQuestionInput("");
    setIsChatLoading(true);

    try {
      const response = await api.sendChatMessage(result.analysis_id, userMsg.text);
      const aiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "assistant",
        text: response.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setChatMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "assistant",
        text: err.response?.data?.detail || "Sorry, I ran into an issue retrieving the answer from the meeting knowledge base.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setChatMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsChatLoading(false);
    }
  };

  // Quick prompt suggestions
  const quickPrompts = [
    "What were the key decisions made?",
    "List all assigned action items and deadlines.",
    "What topics were left open or require follow-up?",
    "Summarize the primary discussion points.",
  ];

  return (
    <div className="w-full max-w-6xl mx-auto space-y-8 pb-16">
      {/* Dashboard Top Navigation & Title Header */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 relative overflow-hidden">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-2">
            <button 
              onClick={onReset}
              className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 font-medium mb-1 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to New Analysis</span>
            </button>
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
              {result.title || "Meeting Intelligence Report"}
            </h1>
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
              <span className="px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 font-medium">
                Analysis ID: {result.analysis_id.slice(0, 8)}
              </span>
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <ShieldCheck className="w-4 h-4" />
                Pipeline Completed
              </span>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex p-1.5 bg-slate-900/90 rounded-2xl border border-white/5">
            <button
              onClick={() => setActiveTab("overview")}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-xs sm:text-sm transition-all ${
                activeTab === "overview"
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Overview</span>
            </button>

            <button
              onClick={() => setActiveTab("insights")}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-xs sm:text-sm transition-all ${
                activeTab === "insights"
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Lightbulb className="w-4 h-4" />
              <span>Insights</span>
            </button>

            <button
              onClick={() => setActiveTab("transcript")}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-xs sm:text-sm transition-all ${
                activeTab === "transcript"
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Transcript</span>
            </button>

            <button
              onClick={() => setActiveTab("chat")}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-xs sm:text-sm transition-all ${
                activeTab === "chat"
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>Chat RAG</span>
            </button>
          </div>
        </div>
      </div>

      {/* TAB CONTENT: Overview */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Quick Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="glass-panel p-6 rounded-2xl border border-indigo-500/20 glass-card-hover flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center">
                <CheckSquare className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Action Items</p>
                <h3 className="text-xl font-bold text-white mt-0.5">Assigned & Tracked</h3>
              </div>
            </div>

            <div className="glass-panel p-6 rounded-2xl border border-purple-500/20 glass-card-hover flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center justify-center">
                <ListOrdered className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Key Decisions</p>
                <h3 className="text-xl font-bold text-white mt-0.5">Extracted & Merged</h3>
              </div>
            </div>

            <div className="glass-panel p-6 rounded-2xl border border-amber-500/20 glass-card-hover flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center">
                <HelpCircle className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Open Questions</p>
                <h3 className="text-xl font-bold text-white mt-0.5">Unresolved Topics</h3>
              </div>
            </div>
          </div>

          {/* Meeting Summary Card */}
          <div className="glass-panel p-8 rounded-3xl border border-white/10 space-y-4">
            <div className="flex items-center gap-3 text-indigo-400 border-b border-white/5 pb-4">
              <Sparkles className="w-5 h-5" />
              <h2 className="text-xl font-bold text-white">Executive Summary</h2>
            </div>
            <div className="prose prose-invert max-w-none text-slate-300 leading-relaxed text-sm space-y-3">
              <ReactMarkdown>{result.summary}</ReactMarkdown>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: Insights */}
      {activeTab === "insights" && (
        <div className="space-y-8">
          {/* Action Items Section */}
          <div className="glass-panel p-8 rounded-3xl border border-indigo-500/20 space-y-6">
            <div className="flex items-center gap-3 text-indigo-400 border-b border-white/5 pb-4">
              <CheckSquare className="w-6 h-6" />
              <div>
                <h2 className="text-xl font-bold text-white">Action Items</h2>
                <p className="text-xs text-slate-400">Extracted tasks, owners, and specified deadlines</p>
              </div>
            </div>
            <div className="prose prose-invert max-w-none text-slate-300 text-sm">
              <ReactMarkdown>{result.action_items}</ReactMarkdown>
            </div>
          </div>

          {/* Key Decisions Section */}
          <div className="glass-panel p-8 rounded-3xl border border-purple-500/20 space-y-6">
            <div className="flex items-center gap-3 text-purple-400 border-b border-white/5 pb-4">
              <ListOrdered className="w-6 h-6" />
              <div>
                <h2 className="text-xl font-bold text-white">Key Decisions Made</h2>
                <p className="text-xs text-slate-400">Agreed-upon outcomes and consensus decisions</p>
              </div>
            </div>
            <div className="prose prose-invert max-w-none text-slate-300 text-sm">
              <ReactMarkdown>{result.key_decisions}</ReactMarkdown>
            </div>
          </div>

          {/* Open Questions Section */}
          <div className="glass-panel p-8 rounded-3xl border border-amber-500/20 space-y-6">
            <div className="flex items-center gap-3 text-amber-400 border-b border-white/5 pb-4">
              <HelpCircle className="w-6 h-6" />
              <div>
                <h2 className="text-xl font-bold text-white">Open & Unresolved Questions</h2>
                <p className="text-xs text-slate-400">Follow-up questions and unresolved items</p>
              </div>
            </div>
            <div className="prose prose-invert max-w-none text-slate-300 text-sm">
              <ReactMarkdown>{result.open_questions}</ReactMarkdown>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: Transcript */}
      {activeTab === "transcript" && (
        <div className="glass-panel p-8 rounded-3xl border border-white/10 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/5 pb-4">
            <div>
              <h2 className="text-xl font-bold text-white">Full Meeting Transcript</h2>
              <p className="text-xs text-slate-400">Searchable verbatim speech-to-text transcript</p>
            </div>
            <button
              onClick={handleCopyTranscript}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-white/10 transition-colors shrink-0"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? "Copied to Clipboard" : "Copy Transcript"}</span>
            </button>
          </div>

          {/* Search Box */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
              <Search className="w-4 h-4" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search transcript..."
              className="w-full pl-11 pr-4 py-3 rounded-2xl bg-slate-900/90 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Transcript Viewer Box */}
          <div className="p-6 rounded-2xl bg-slate-950/80 border border-slate-800/80 max-h-[500px] overflow-y-auto text-sm text-slate-300 leading-relaxed whitespace-pre-wrap font-mono">
            {result.transcript}
          </div>
        </div>
      )}

      {/* TAB CONTENT: Chat RAG */}
      {activeTab === "chat" && (
        <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-indigo-500/20 space-y-6 flex flex-col min-h-[600px]">
          {/* Chat Header */}
          <div className="flex items-center gap-3 border-b border-white/5 pb-4 shrink-0">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Chat with Your Meeting</h2>
              <p className="text-xs text-slate-400">RAG pipeline powered by Mistral AI & ChromaDB vector search</p>
            </div>
          </div>

          {/* Quick Prompts Suggestions */}
          <div className="flex flex-wrap gap-2 shrink-0">
            {quickPrompts.map((promptText, idx) => (
              <button
                key={idx}
                onClick={() => handleSendQuestion(promptText)}
                disabled={isChatLoading}
                className="px-3 py-1.5 rounded-full bg-slate-900 hover:bg-indigo-600/20 border border-slate-700/80 hover:border-indigo-500/50 text-xs text-slate-300 hover:text-indigo-300 transition-all text-left"
              >
                💡 {promptText}
              </button>
            ))}
          </div>

          {/* Message History List */}
          <div className="flex-1 overflow-y-auto space-y-4 p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 max-h-[420px]">
            {chatMessages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-[85%] ${
                  msg.sender === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                    msg.sender === "user"
                      ? "bg-indigo-600 text-white"
                      : "bg-purple-600/20 text-purple-400 border border-purple-500/30"
                  }`}
                >
                  {msg.sender === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>
                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-indigo-600 text-white rounded-tr-none"
                      : "bg-slate-900/90 text-slate-200 border border-slate-800 rounded-tl-none"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.text}</p>
                  <span className="block text-[10px] opacity-60 mt-1 text-right">
                    {msg.timestamp}
                  </span>
                </div>
              </div>
            ))}

            {isChatLoading && (
              <div className="flex gap-3 max-w-[85%] mr-auto">
                <div className="w-8 h-8 rounded-xl bg-purple-600/20 text-purple-400 border border-purple-500/30 flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 text-slate-400 text-xs flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-purple-400 animate-bounce" />
                  <div className="w-2 h-2 rounded-full bg-purple-400 animate-bounce [animation-delay:0.2s]" />
                  <div className="w-2 h-2 rounded-full bg-purple-400 animate-bounce [animation-delay:0.4s]" />
                  <span className="ml-2 text-slate-400">Searching meeting transcript context...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Question Input Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendQuestion();
            }}
            className="flex items-center gap-3 shrink-0"
          >
            <input
              type="text"
              value={questionInput}
              onChange={(e) => setQuestionInput(e.target.value)}
              placeholder="Ask anything about the meeting (e.g. What pricing was agreed upon?)..."
              disabled={isChatLoading}
              className="flex-1 px-5 py-4 rounded-2xl bg-slate-900/90 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-indigo-500"
            />
            <button
              type="submit"
              disabled={isChatLoading || !questionInput.trim()}
              className="p-4 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30 disabled:opacity-40 disabled:cursor-not-allowed transition-all shrink-0"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
};
