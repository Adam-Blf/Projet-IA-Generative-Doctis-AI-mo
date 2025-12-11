from fastapi import FastAPI, Request, Header, Header

# ... (Previous imports remain)

# ... inside @app.post("/api/analyze")

@app.post("/api/analyze")
async def analyze_symptoms(
    data: TriageRequest,
    x_gemini_api_key: Optional[str] = Header(None)
):
    """
    Main Logic Pipeline:
    ...
    """
    # ... (BMI Logic remains same)

    # ... (RAG Logic remains same)
    
    # ... Prompt construction ...
    
    # 3. Generate (Smart Switch)
    # Configure custom context if key is provided
    custom_config = {"api_key": x_gemini_api_key} if x_gemini_api_key else None
    
    ai_response = llm.generate_content(system_prompt, user_prompt, custom_config=custom_config)
    
    return {
        "analysis": ai_response,
        "sources": rag_results
    }
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
app = FastAPI(title="DoctisAImo v16.8-Optimized", description="Advanced Medical Triage AI")

# CORS (Allow all for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Public API: Allow all origins
    allow_credentials=False, # No cookies/auth headers needed -> simplifies CORS significantly
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static & Templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend")

# --- CORE LOADING ---
# Lazy load core components to ensure startup speed
kb = KnowledgeBase()
# We don't block startup on load, but we ensure it's loaded before first request
if not kb.df is not None:
    kb.load()

rag = RAGEngine(kb)
llm = ModelManager()

# --- DATA MODELS ---
from typing import Optional

class TriageRequest(BaseModel):
    # Identity (Required)
    first_name: str
    last_name: str
    age: int
    gender: str
    
    # Biometrics (Required for BMI)
    height: int # cm
    weight: int # kg
    
    # Clinical (Required)
    symptoms: str
    
    # Optional Context
    history: Optional[str] = None
    vitals: Optional[str] = None
    medications: Optional[str] = None

# --- ROUTES ---

@app.get("/")
async def read_root(request: Request):
    """Serves the main frontend interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/analyze")
async def analyze_symptoms(
    data: TriageRequest,
    x_gemini_api_key: Optional[str] = Header(None)
):
    """
    Main Logic Pipeline:
    1. Calculate BMI
    2. Semantic Search (RAG)
    3. Context Construction (Full Report)
    4. LLM Generation
    """
    # 0. Calc BMI
    bmi = 0.0
    bmi_category = "N/A"
    if data.height > 0:
        height_m = data.height / 100
        bmi = data.weight / (height_m * height_m)
        
        if bmi < 18.5: bmi_category = "Maigreur"
        elif 18.5 <= bmi < 25: bmi_category = "Normal"
        elif 25 <= bmi < 30: bmi_category = "Surpoids"
        else: bmi_category = "Obésité"

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
    ANALYSE CE DOSSIER PATIENT COMPLET :
    
    ==== 1. IDENTITÉ & BIOMÉTRIE ====
    Nom: {data.last_name.upper()}, {data.first_name}
    Age: {data.age} ans | Sexe: {data.gender}
    Taille: {data.height} cm | Poids: {data.weight} kg
    IMC: {bmi:.1f} ({bmi_category})
    
    ==== 2. CLINIQUE (MOTIF) ====
    "{data.symptoms}"
    
    ==== 3. CONTEXTE ADDITIONNEL (SI DISPO) ====
    Antécédents / Histoire: {data.history or "Non renseigné"}
    Constantes (Vitals): {data.vitals or "Non renseigné"}
    Traitements: {data.medications or "Non renseigné"}
    
    ==== 4. BASE DE CONNAISSANCE (RAG) ====
    {rag_context}
    
    INSTRUCTIONS DE RAPPORT:
    1. Résumé Clinique (incluant l'interprétation de l'IMC si pertinent).
    2. Analyse Différentielle (Basée sur RAG + Symptômes).
    3. Niveau d'Urgence Estimé (Code Couleur).
    4. Recommandations & Prochaines étapes.
    
    Réponds en Français. Sois professionnel, empathique, et précis.
    """
    
    # 3. Generate (Smart Switch)
    custom_config = {"api_key": x_gemini_api_key} if x_gemini_api_key else None
    ai_response = llm.generate_content(system_prompt, user_prompt, custom_config=custom_config)
    
    return {
        "analysis": ai_response,
        "sources": rag_results
    }

if __name__ == "__main__":
    DEFAULT_HOST = "0.0.0.0" # Bind to all interfaces (Docker/Render)
    DEFAULT_PORT = 8000
    uvicorn.run("main:app", host=DEFAULT_HOST, port=DEFAULT_PORT, reload=True)
