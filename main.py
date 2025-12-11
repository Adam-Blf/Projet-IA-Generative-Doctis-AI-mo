from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os

from src.core.knowledge_base import KnowledgeBase
from src.core.rag_engine import RAGEngine
from src.services.llm_service import ModelManager

# --- APP INIT ---
app = FastAPI(title="DoctisAImo v2.0", description="Advanced Medical Triage AI")

# CORS (Allow all for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static & Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- CORE LOADING ---
# Lazy load core components to ensure startup speed
kb = KnowledgeBase()
# We don't block startup on load, but we ensure it's loaded before first request
if not kb.df is not None:
    kb.load()

rag = RAGEngine(kb)
llm = ModelManager()

# --- DATA MODELS ---
class TriageRequest(BaseModel):
    age: int
    gender: str
    symptoms: str

# --- ROUTES ---

@app.get("/")
async def read_root(request: Request):
    """Serves the main frontend interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/analyze")
async def analyze_symptoms(data: TriageRequest):
    """
    Main Logic Pipeline:
    1. Semantic Search (RAG)
    2. Context Construction
    3. LLM Generation (with Auto-Switch)
    """
    # 1. RAG Retrieve
    rag_results = rag.search(data.symptoms, top_k=3)
    
    # Format context for LLM
    rag_context = "\n".join([
        f"- {r['disease']} (Pertinence: {r['score']:.2f}): {r['description']}" 
        for r in rag_results
    ])
    
    # 2. Build Prompt
    system_prompt = "Tu es DoctisAImo, une IA experte en triage médical d'urgence. Réponds en Markdown structuré."
    
    user_prompt = f"""
    ANALYSE CE CAS MÉDICAL :
    
    PATIENT: {data.age} ans, {data.gender}.
    SYMPTÔMES: "{data.symptoms}"
    
    CONTEXTE MÉDICAL DE RÉFÉRENCE (RAG):
    {rag_context}
    
    INSTRUCTIONS:
    1. Détermine le niveau d'urgence (Code Vert/Orange/Rouge).
    2. Fournis une analyse clinique.
    3. Liste des recommandations immédiates.
    
    Réponds en Français. Sois concis et professionnel.
    """
    
    # 3. Generate (Smart Switch)
    ai_response = llm.generate_content(system_prompt, user_prompt)
    
    return {
        "analysis": ai_response,
        "sources": rag_results
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
