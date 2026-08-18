import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarise, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MOM — AI Video Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;500&display=swap');

/* ── Root Variables ── */
:root {
    --bg: #f0f4f8;
    --surface: #ffffff;
    --surface-soft: #f7f9fc;
    --border: #dce3ed;
    --border-focus: #7eb8e0;
    --accent: #4a90d9;
    --accent-light: #6aafe6;
    --accent-soft: #e8f0fe;
    --text: #0f172a;
    --text-soft: #334155;
    --text-muted: #64748b;
    --success: #2e9b6e;
    --success-soft: #e6f5ef;
    --warning: #e8a838;
    --danger: #d95c5c;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

header[data-testid="stHeader"] {
    background: var(--bg) !important;
    border-bottom: 1px solid var(--border) !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

.stApp {
    background: var(--bg) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    padding: 1.5rem 1rem !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}

.sidebar-brand-icon {
    width: 40px;
    height: 40px;
    background: var(--accent);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
    font-weight: 700;
    box-shadow: 0 4px 12px rgba(74, 144, 217, 0.25);
}

.sidebar-brand-name {
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.3px;
}

.sidebar-brand-sub {
    font-size: 8px;
    color: var(--text-muted);
    letter-spacing: 1.2px;
    text-transform: uppercase;
    font-weight: 600;
}

.sidebar-section {
    font-size: 9px;
    letter-spacing: 1.2px;
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
    margin: 1.5rem 0 0.5rem 0;
}

.sidebar-item {
    padding: 8px 12px;
    border-radius: 8px;
    color: var(--text-soft);
    font-size: 13px;
    margin-bottom: 2px;
    transition: all 0.15s ease;
    display: flex;
    align-items: center;
    gap: 10px;
}

.sidebar-item.active {
    background: var(--accent-soft);
    color: var(--accent);
    font-weight: 600;
}

.sidebar-item:not(.active):hover {
    background: rgba(74, 144, 217, 0.05);
}

.sidebar-footer {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    font-size: 10px;
    color: var(--text-muted);
    line-height: 1.6;
}

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text) !important;
}

/* ── Hero ── */
.hero-title {
    font-family: 'DM Sans', sans-serif;
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 700;
    line-height: 1.1;
    margin: 0;
    color: var(--text);
    letter-spacing: -0.5px;
}

.hero-sub {
    font-size: 0.9rem;
    color: var(--text-soft);
    margin-top: 0.3rem;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--success-soft);
    border: 1px solid #b8dec9;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 11px;
    color: var(--success);
    font-weight: 600;
}

.hero-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--success);
    animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.card:hover {
    border-color: var(--border-focus);
    box-shadow: 0 4px 16px rgba(74, 144, 217, 0.06);
}

.card-accent {
    border-left: 3px solid var(--accent);
}

.card-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-content {
    font-size: 0.9rem;
    line-height: 1.7;
    color: var(--text-soft);
}

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 5px;
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.badge-blue   { background: var(--accent-soft); color: var(--accent); border: 1px solid #c5d9f0; }
.badge-green  { background: var(--success-soft); color: var(--success); border: 1px solid #b8dec9; }
.badge-gray   { background: #f0f2f5; color: var(--text-muted); border: 1px solid #e0e4ea; }

/* ── Input & Buttons ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.12) !important;
}

.stButton > button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(74, 144, 217, 0.2) !important;
}

.stButton > button:hover:not(:disabled) {
    background: #3a7bc8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(74, 144, 217, 0.35) !important;
}

.stButton > button:disabled {
    background: #b0c8e0 !important;
    cursor: not-allowed !important;
    transform: none !important;
    box-shadow: none !important;
}

.stButton > button[kind="secondary"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-soft) !important;
    box-shadow: none !important;
}

.stButton > button[kind="secondary"]:hover {
    background: var(--surface-soft) !important;
    transform: none !important;
}

/* ─────────────────────────────────────────
   FILE UPLOADER
───────────────────────────────────────── */

[data-testid="stFileUploaderDropzone"] {
    border: 1.5px dashed #cbd5e1 !important;
    border-radius: 14px !important;

    background: #f8fafc !important;

    padding: 1.6rem !important;

    transition:
        border-color 0.2s ease,
        background 0.2s ease,
        box-shadow 0.2s ease !important;
}


/* ─────────────────────────────────────────
   DROPZONE HOVER
───────────────────────────────────────── */

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #f97316 !important;
    background: #fffaf5 !important;

    box-shadow:
        0 4px 14px rgba(249, 115, 22, 0.08) !important;
}


/* ─────────────────────────────────────────
   UPLOAD BUTTON — ONLY CHANGE THIS
───────────────────────────────────────── */

[data-testid="stFileUploaderDropzone"] button {
    background: #ffffff !important;

    color: #334155 !important;

    border: 1px solid #cbd5e1 !important;

    border-radius: 9px !important;

    font-weight: 600 !important;

    font-size: 0.8rem !important;

    padding: 0.55rem 1rem !important;

    box-shadow: none !important;

    transition:
        background 0.2s ease,
        border-color 0.2s ease,
        color 0.2s ease !important;
}


/* ─────────────────────────────────────────
   UPLOAD BUTTON HOVER
───────────────────────────────────────── */

[data-testid="stFileUploaderDropzone"] button:hover {
    background: #fff7ed !important;

    color: #ea580c !important;

    border-color: #f97316 !important;

    box-shadow: none !important;
}

/* ─────────────────────────────────────
   HEADER
───────────────────────────────────── */

.analysis-header {
    margin-bottom: 1.55rem;
}

.analysis-title {
    display: flex;
    align-items: center;
    gap: 0.45rem;

    font-size: 1.2rem;
    font-weight: 700;

    color: #1e293b;

    letter-spacing: -0.01em;

    margin-bottom: 0.35rem;
}

.analysis-description {
    font-size: 0.88rem;

    color: #475569;

    line-height: 1.5;
}


/* ─────────────────────────────────────
   FILE UPLOADER
───────────────────────────────────── */
/* ─────────────────────────────────────────
   FILE UPLOADER
───────────────────────────────────────── */

[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed #cbd5e1 !important;
    border-radius: 14px !important;
    background: #f8fafc !important;
    padding: 1.5rem !important;
    min-height: 120px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    overflow: hidden !important;
    transition: border-color 0.2s ease, background 0.2s ease !important;
}

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #f97316 !important;
    background: #fffaf5 !important;
}

/* Fix for button text overflow */
[data-testid="stFileUploaderDropzone"] button {
    background: #ffffff !important;
    color: #334155 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 9px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.2rem !important;
    box-shadow: none !important;
    white-space: nowrap !important;
    min-width: auto !important;
    width: auto !important;
    max-width: 100% !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    transition: border-color 0.2s ease, background 0.2s ease, color 0.2s ease !important;
}

[data-testid="stFileUploaderDropzone"] button:hover {
    background: #fff7ed !important;
    border-color: #f97316 !important;
    color: #ea580c !important;
    box-shadow: none !important;
}

/* Center the upload content */
[data-testid="stFileUploaderDropzone"] > div,
[data-testid="stFileUploaderDropzone"] > div > div {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    text-align: center !important;
}

/* Hide the small text that overflows */
[data-testid="stFileUploader"] > div > small {
    display: none !important;
}

/* Fix text wrapping */
[data-testid="stFileUploaderDropzone"] p {
    color: #64748b !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    margin: 0 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

[data-testid="stFileUploaderDropzone"] small {
    color: #94a3b8 !important;
    font-size: 0.7rem !important;
}

/* ─────────────────────────────────────
   FILE UPLOADER CONTENT — center everything inside
───────────────────────────────────── */

[data-testid="stFileUploaderDropzone"] > div,
[data-testid="stFileUploaderDropzone"] > div > div,
[data-testid="stFileUploaderDropzone"] > section,
[data-testid="stFileUploaderDropzone"] > section > div,
[data-testid="stFileUploaderDropzone"] section[data-testid="stFileUploaderDropzoneInput"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    text-align: center !important;
}

[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] label {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}


/* ─────────────────────────────────────
   FILE UPLOADER CONTENT — center everything inside
───────────────────────────────────── */

[data-testid="stFileUploaderDropzone"] > div,
[data-testid="stFileUploaderDropzone"] > div > div,
[data-testid="stFileUploaderDropzone"] > section,
[data-testid="stFileUploaderDropzone"] > section > div,
[data-testid="stFileUploaderDropzone"] section[data-testid="stFileUploaderDropzoneInput"] {

    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    text-align: center !important;
}

[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] label {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}


/* ─────────────────────────────────────
   UPLOAD BUTTON
───────────────────────────────────── */

[data-testid="stFileUploaderDropzone"] button {

    background: #ffffff !important;

    color: #334155 !important;

    border: 1px solid #cbd5e1 !important;

    border-radius: 9px !important;

    font-size: 0.8rem !important;

    font-weight: 600 !important;

    padding: 0.55rem 1rem !important;

    box-shadow: none !important;

    white-space: nowrap !important;

    transition:
        border-color 0.2s ease,
        background 0.2s ease,
        color 0.2s ease !important;
}


[data-testid="stFileUploaderDropzone"] button:hover {

    background: #fff7ed !important;

    border-color: #f97316 !important;

    color: #ea580c !important;

    box-shadow: none !important;
}


/* ─────────────────────────────────────
   UPLOADER TEXT
───────────────────────────────────── */

[data-testid="stFileUploaderDropzone"] p {

    color: #64748b !important;

    font-size: 0.82rem !important;

    font-weight: 500 !important;

    margin: 0 !important;

    white-space: nowrap !important;
}


[data-testid="stFileUploaderDropzone"] small {

    color: #94a3b8 !important;

}


/* ─────────────────────────────────────
   YOUTUBE LABEL
───────────────────────────────────── */

.youtube-label {

    font-size: 0.72rem;

    font-weight: 600;

    color: #64748b;

    margin-bottom: 0.55rem;
}


/* ─────────────────────────────────────
   YOUTUBE INPUT
───────────────────────────────────── */

.stTextInput > div > div > input {

    height: 46px !important;

    background: #ffffff !important;

    color: #334155 !important;

    border: 1px solid #d7e0ea !important;

    border-radius: 10px !important;

    padding: 0.7rem 0.85rem !important;

    font-size: 0.82rem !important;

    box-shadow: none !important;

    transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease !important;
}


/* Placeholder */

.stTextInput > div > div > input::placeholder {

    color: #94a3b8 !important;

    opacity: 1 !important;
}


/* Focus */

.stTextInput > div > div > input:focus {

    border-color: #f97316 !important;

    box-shadow:
        0 0 0 3px rgba(249, 115, 22, 0.08) !important;
}


/* ─────────────────────────────────────
   BUTTON SPACING
───────────────────────────────────── */

.analyze-spacing {

    height: 20px;

}


/* ─────────────────────────────────────
   ANALYZE BUTTON
───────────────────────────────────── */

.stButton > button {

    height: 54px !important;

    background: #ffffff !important;

    color: #334155 !important;

    border: 1px solid #d7e0ea !important;

    border-radius: 10px !important;

    font-size: 0.85rem !important;

    font-weight: 600 !important;

    box-shadow: none !important;

    transition:
        border-color 0.2s ease,
        background 0.2s ease,
        color 0.2s ease,
        transform 0.15s ease !important;
}


.stButton > button:hover {

    background: #fffaf5 !important;

    border-color: #f97316 !important;

    color: #ea580c !important;

    transform: translateY(-1px) !important;

    box-shadow:
        0 4px 12px rgba(249, 115, 22, 0.08) !important;
}


.stButton > button:disabled {

    background: #f1f5f9 !important;

    color: #94a3b8 !important;

    border-color: #e2e8f0 !important;

    box-shadow: none !important;

    transform: none !important;
}

/* ── Pipeline Steps ── */
.pipeline-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}

.pipeline-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
}

.pipeline-title {
    font-weight: 700;
    font-size: 0.85rem;
}

.pipeline-status-text {
    font-size: 0.7rem;
    color: var(--text-muted);
    font-weight: 600;
}

.pipeline-step {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 4px;
    background: var(--surface-soft);
    border: 1px solid transparent;
    transition: all 0.2s ease;
}

.pipeline-step.active {
    background: var(--accent-soft);
    border-color: #c5d9f0;
}

.pipeline-step.done {
    background: var(--success-soft);
    border-color: #b8dec9;
}

.pipeline-step.pending {
    background: #f5f6f8;
    border-color: #e8ecf2;
}

.pipeline-step .step-icon {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    flex-shrink: 0;
}

.pipeline-step.active .step-icon { background: #d4e4f7; }
.pipeline-step.done .step-icon { background: #c5e6d6; }
.pipeline-step.pending .step-icon { background: #e8ecf2; }

.pipeline-step .step-info { flex: 1; }
.pipeline-step .step-name { font-size: 12px; font-weight: 600; }
.pipeline-step .step-detail { font-size: 10px; color: var(--text-muted); margin-top: 1px; }

.pipeline-step .step-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.pipeline-step.active .step-dot { background: var(--accent); animation: pulse 1.5s infinite; }
.pipeline-step.done .step-dot { background: var(--success); }
.pipeline-step.pending .step-dot { background: #c5cbd5; }

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.85); }
}

/* ── Processing Status ── */
.processing-status {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: var(--accent-soft);
    border: 1px solid #c5d9f0;
    border-radius: 10px;
    margin-bottom: 1rem;
}

.processing-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #c5d9f0;
    border-top: 2px solid var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* ── Transcript ── */
.transcript-box {
    background: var(--surface-soft);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.25rem;
    font-size: 0.82rem;
    line-height: 1.8;
    max-height: 320px;
    overflow-y: auto;
    color: var(--text-soft);
    white-space: pre-wrap;
    word-break: break-word;
    font-family: 'Space Mono', monospace;
}

/* ── Chat ── */
.chat-container {
    background: var(--surface-soft);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    max-height: 380px;
    overflow-y: auto;
    margin-bottom: 1rem;
}

.chat-msg {
    margin-bottom: 0.8rem;
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}

.chat-label {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.chat-bubble {
    display: inline-block;
    padding: 0.6rem 1rem;
    border-radius: 10px;
    font-size: 0.85rem;
    line-height: 1.6;
    max-width: 90%;
}

.user-label { color: var(--accent); }
.bot-label { color: var(--success); }

.user-bubble {
    background: var(--accent-soft);
    border: 1px solid #c5d9f0;
    align-self: flex-end;
}
.bot-bubble {
    background: var(--success-soft);
    border: 1px solid #b8dec9;
    align-self: flex-start;
}

/* scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #c5cbd5; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
    "button_disabled": False,
    "current_step_detail": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
PIPELINE_STEPS = [
    {"key": "download", "icon": "📥", "name": "Downloading Video", "detail": "Fetching from YouTube or local file"},
    {"key": "audio", "icon": "🎧", "name": "Audio Processing", "detail": "Extracting and preparing audio chunks"},
    {"key": "transcript", "icon": "✍️", "name": "Transcription", "detail": "Converting speech to text with Whisper"},
    {"key": "title", "icon": "🏷️", "name": "Title Generation", "detail": "Understanding the session context"},
    {"key": "summary", "icon": "📋", "name": "Summarisation", "detail": "Creating executive summary"},
    {"key": "extract", "icon": "🔍", "name": "Insight Extraction", "detail": "Finding actions, decisions, questions"},
    {"key": "rag", "icon": "🧠", "name": "Knowledge Index", "detail": "Building RAG question-answering"},
]

def get_step_status(key: str) -> str:
    return st.session_state.pipeline_steps.get(key, "pending")

def render_pipeline():
    """Render the pipeline status on the main page"""
    completed = sum(1 for s in PIPELINE_STEPS if get_step_status(s["key"]) == "done")
    total = len(PIPELINE_STEPS)
    running = any(get_step_status(s["key"]) == "active" for s in PIPELINE_STEPS)

    if running:
        status_text = f"{completed}/{total} · Running"
    elif completed == total:
        status_text = "✓ Complete"
    else:
        status_text = "Ready"

    html = f'<div class="pipeline-container"><div class="pipeline-header"><div class="pipeline-title">⚡ Pipeline</div><div class="pipeline-status-text">{status_text}</div></div>'

    for step in PIPELINE_STEPS:
        status = get_step_status(step["key"])
        if status == "active":
            css = "active"
            detail = step["detail"] + " · Working now"
        elif status == "done":
            css = "done"
            detail = step["detail"] + " · Completed"
        else:
            css = "pending"
            detail = step["detail"]

        html += f'<div class="pipeline-step {css}"><div class="step-icon">{step["icon"]}</div><div class="step-info"><div class="step-name">{step["name"]}</div><div class="step-detail">{detail}</div></div><div class="step-dot"></div></div>'

    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">✦</div>
        <div>
            <div class="sidebar-brand-name">MOM</div>
            <div class="sidebar-brand-sub">AI Video Assistant</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Language</div>', unsafe_allow_html=True)
    language = st.selectbox("Select language", ["english", "hinglish"], label_visibility="collapsed")

    if st.session_state.result is not None:
        st.markdown("---")
        if st.button("🔄 Analyze New Video", use_container_width=True):
            st.session_state.result = None
            st.session_state.chat_history = []
            st.session_state.pipeline_done = False
            st.session_state.pipeline_steps = {}
            st.rerun()

    st.markdown('<div class="sidebar-footer">MOM v2.0 · Whisper · RAG · Mistral</div>', unsafe_allow_html=True)


# ─── Main Area ──────────────────────────────────────────────────────────────────
# Hero
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="hero-title">Turn videos into knowledge.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Transcribe, summarize, extract insights, and chat with your meeting content.</div>', unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style="display:flex;justify-content:flex-end;padding-top:0.5rem;">
        <div class="hero-badge"><div class="hero-dot"></div> System Ready</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Upload Section ─────────────────────────────────────────────────────────────
if st.session_state.result is None:

    # ─────────────────────────────────────
    # HEADER
    # ─────────────────────────────────────

    st.markdown('<div class="analysis-header"><div class="analysis-title">📤 Start a new analysis</div><div class="analysis-description">Paste a YouTube URL or drop a media file below.</div></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────
    # INPUT ROW
    # ─────────────────────────────────────

    col_upload, col_url = st.columns(
        [3, 2],
        gap="large"
    )

    # ───────────── FILE UPLOAD ─────────────

    with col_upload:

        uploaded_file = st.file_uploader(
            "Upload media",
            type=["mp4", "mov", "webm", "mp3", "wav", "m4a", "ogg", "flac"],
            label_visibility="collapsed",
            help="Drag and drop or click to browse"
        )

    # ───────────── YOUTUBE URL ─────────────

    with col_url:

        st.markdown('<div class="youtube-label">YouTube URL</div>', unsafe_allow_html=True)

        source_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed"
        )

    # ─────────────────────────────────────
    # ANALYZE BUTTON
    # ─────────────────────────────────────

    st.markdown("<div class='analyze-spacing'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:

        button_disabled = (
            st.session_state.processing
            or st.session_state.pipeline_done
        )

        analyze_btn = st.button(
            "✦ Analyze Video",
            use_container_width=True,
            disabled=button_disabled
        )


    # ─── Show processing status ───────────────────────────────────────────────
    if st.session_state.processing:
        st.markdown("""
        <div class="processing-status">
            <div class="processing-spinner"></div>
            <div>
                <div style="font-weight:600;font-size:0.9rem;color:var(--text);">Processing your video...</div>
                <div style="font-size:0.8rem;color:var(--text-muted);">This may take a few moments</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ─── Pipeline Display Placeholder ─────────────────────────────────────────
    pipeline_placeholder = st.empty()
    if st.session_state.pipeline_done or st.session_state.processing:
        with pipeline_placeholder.container():
            render_pipeline()

    # Helper to refresh the pipeline container dynamically
    def update_pipeline_ui(active_key=None, done_keys=None):
        done_set = set(done_keys or [])
        for s in PIPELINE_STEPS:
            k = s["key"]
            if k in done_set:
                st.session_state.pipeline_steps[k] = "done"
            elif k == active_key:
                st.session_state.pipeline_steps[k] = "active"
            else:
                st.session_state.pipeline_steps[k] = "pending"
        with pipeline_placeholder.container():
            render_pipeline()

    # ─── Run Pipeline ──────────────────────────────────────────────────────────
    if analyze_btn and not st.session_state.processing:
        source = source_url.strip() if source_url else None

        if uploaded_file:
            import tempfile
            import os
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                source = tmp.name

        if not source:
            st.warning("⚠️ Please provide a YouTube URL or upload a media file.")
        else:
            st.session_state.pipeline_done = False
            st.session_state.result = None
            st.session_state.chat_history = []
            st.session_state.pipeline_steps = {}
            st.session_state.processing = True
            st.session_state.button_disabled = True

            try:
                # ── Step 0 & 1: Download & Audio ──
                update_pipeline_ui("download", [])
                chunks = process_input(source)
                update_pipeline_ui("transcript", ["download", "audio"])

                # ── Step 2: Transcription ──
                transcript = transcribe_all(chunks, language)
                update_pipeline_ui("title", ["download", "audio", "transcript"])

                # ── Step 3: Title ──
                title = generate_title(transcript)
                update_pipeline_ui("summary", ["download", "audio", "transcript", "title"])

                # ── Step 4: Summary ──
                summary = summarise(transcript)
                update_pipeline_ui("extract", ["download", "audio", "transcript", "title", "summary"])

                # ── Step 5: Extraction ──
                action_items = extract_action_items(transcript)
                decisions = extract_key_decisions(transcript)
                questions = extract_questions(transcript)
                update_pipeline_ui("rag", ["download", "audio", "transcript", "title", "summary", "extract"])

                # ── Step 6: RAG ──
                rag_chain = build_rag_chain(transcript)
                update_pipeline_ui(None, ["download", "audio", "transcript", "title", "summary", "extract", "rag"])

                st.session_state.result = {
                    "title": title,
                    "transcript": transcript,
                    "summary": summary,
                    "action_items": action_items,
                    "key_decisions": decisions,
                    "open_questions": questions,
                    "rag_chain": rag_chain,
                }
                st.session_state.pipeline_done = True
                st.session_state.processing = False
                st.session_state.button_disabled = False
                st.success("✅ Analysis complete!")
                time.sleep(0.5)
                st.rerun()

            except Exception as e:
                st.session_state.processing = False
                st.session_state.button_disabled = False
                for s in PIPELINE_STEPS:
                    if st.session_state.pipeline_steps.get(s["key"]) == "active":
                        st.session_state.pipeline_steps[s["key"]] = "pending"
                st.error(f"❌ Error: {e}")

# ─── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # Show pipeline
    render_pipeline()

    # Title banner
    st.markdown(f"""
    <div class="card card-accent" style="background:linear-gradient(135deg, #f8fbff, #ffffff);">
        <div class="card-title">📌 Session Title</div>
        <div style="font-size:1.4rem;font-weight:700;color:var(--text);">
            {r['title']}
        </div>
        <div style="margin-top:0.5rem;">
            <span class="badge badge-blue">Transcript</span>
            <span class="badge badge-green">Summary</span>
            <span class="badge badge-gray">RAG Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Summary + Transcript
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown('<div class="card-title" style="margin-bottom:8px;">📋 Executive Summary</div>', unsafe_allow_html=True)
        st.markdown(r['summary'])

    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(r['transcript'])

    # Insights
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown('<div class="card-title" style="margin-bottom:8px;">✅ Action Items</div>', unsafe_allow_html=True)
        st.markdown(r['action_items'])

    with c2:
        st.markdown('<div class="card-title" style="margin-bottom:8px;">🔑 Key Decisions</div>', unsafe_allow_html=True)
        st.markdown(r['key_decisions'])

    with c3:
        st.markdown('<div class="card-title" style="margin-bottom:8px;">❓ Open Questions</div>', unsafe_allow_html=True)
        st.markdown(r['open_questions'])

    st.markdown("---")

    # ── RAG Chat ──────────────────────────────────────────────────────────────
    st.markdown('<div style="font-size:1.2rem;font-weight:700;margin-bottom:0.8rem;">💬 Ask MOM</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.85rem;color:var(--text-soft);margin-bottom:1rem;">Ask questions about the meeting — MOM will search the transcript for answers.</div>', unsafe_allow_html=True)

    # Chat history using Streamlit chat messages
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(msg["content"])
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:1.5rem;">
            <div style="font-size:2rem;margin-bottom:0.5rem;">💬</div>
            <div style="font-size:0.9rem;color:var(--text-soft);">Ask anything about your meeting transcript</div>
        </div>
        """, unsafe_allow_html=True)

    # Chat input
    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input("Your question", placeholder="What were the main decisions made?", label_visibility="collapsed")
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Searching transcript..."):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    # Empty state (only shown when no result and not processing)
    if not st.session_state.processing and not st.session_state.pipeline_done:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:3rem 1rem;text-align:center;margin-top:1rem;">
            <div style="font-size:3.5rem;margin-bottom:1rem;">🎬</div>
            <div style="font-size:1.3rem;font-weight:700;color:var(--text);margin-bottom:0.5rem;">
                Ready to analyse
            </div>
            <div style="color:var(--text-muted);font-size:0.9rem;max-width:400px;line-height:1.7;">
                Upload a video or paste a YouTube URL above to get started.
            </div>
            <div style="margin-top:1.5rem;display:flex;gap:0.8rem;flex-wrap:wrap;justify-content:center;">
                <span class="badge badge-blue">Transcription</span>
                <span class="badge badge-green">Summarisation</span>
                <span class="badge badge-gray">RAG Chat</span>
            </div>
        </div>
        """, unsafe_allow_html=True)