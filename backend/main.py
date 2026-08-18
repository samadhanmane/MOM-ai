import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root directory is in sys.path for direct python execution
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Load environment variables first
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.health import router as health_router
from backend.routes.analysis import router as analysis_router
from backend.routes.chat import router as chat_router

app = FastAPI(
    title="AI Video Assistant API",
    description="Backend API for AI Video Assistant providing speech-to-text, summarization, key insight extraction, and RAG meeting search.",
    version="1.0.0"
)

# CORS Configuration
frontend_url = os.getenv("FRONTEND_URL", "*")
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "https://mom-ai-gamma.vercel.app",
]

if frontend_url and frontend_url not in origins and frontend_url != "*":
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if frontend_url != "*" else ["*"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router)
app.include_router(analysis_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {
        "message": "AI Video Assistant API is running.",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
