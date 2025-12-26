# =============================================================================
# Projet: Doctis AI
# Auteurs: Adam Beloucif & Amina Medjdoub
# Description: API FastAPI pour le pré-diagnostic médical avec RAG + LLM
# =============================================================================

"""
Doctis AI - Backend API
-----------------------
Architecture:
1. SBERT (all-MiniLM-L6-v2) pour le matching sémantique des symptômes
2. LLM quantizé (GGUF) pour la génération de réponses empathiques
3. Base de données JSON de pathologies

Endpoints:
- POST /diagnose : Analyse des symptômes et pré-diagnostic
- GET /health : Vérification de l'état du service
- GET /pathologies : Liste des pathologies disponibles
"""

import json
import os
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Tentative d'import de llama-cpp-python (optionnel si non installé)
try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("⚠️  llama-cpp-python non installé. Mode dégradé activé (réponses templates).")


# =============================================================================
# Configuration
# =============================================================================

class Settings:
    """Configuration de l'application."""
    APP_NAME: str = "Doctis AI"
    APP_VERSION: str = "1.0.0"
    AUTHORS: list = ["Adam Beloucif", "Amina Medjdoub"]

    # Chemins
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = BASE_DIR / "models"

    # Modèles
    SBERT_MODEL: str = "all-MiniLM-L6-v2"
    LLM_MODEL_PATH: str = str(MODELS_DIR / "llama-3-8b-instruct.Q4_K_M.gguf")

    # Seuils
    SIMILARITY_THRESHOLD: float = 0.4
    LLM_MAX_TOKENS: int = 256
    LLM_TEMPERATURE: float = 0.7


settings = Settings()


# =============================================================================
# Modèles Pydantic (Schémas)
# =============================================================================

class SymptomInput(BaseModel):
    """Schéma d'entrée pour l'analyse des symptômes."""
    symptoms: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Description des symptômes en langage naturel",
        example="J'ai mal au ventre en bas à droite et je vomis depuis ce matin"
    )


class PathologyMatch(BaseModel):
    """Résultat du matching d'une pathologie."""
    id: str
    name: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    severity_level: int = Field(..., ge=1, le=5)
    urgency: str
    advice: str
    specialist: str


class DiagnosisResponse(BaseModel):
    """Réponse complète du diagnostic."""
    success: bool
    matched: bool
    pathology: Optional[PathologyMatch] = None
    ai_response: str
    disclaimer: str
    authors: list[str] = settings.AUTHORS


class HealthResponse(BaseModel):
    """Réponse du health check."""
    status: str
    app_name: str
    version: str
    models_loaded: dict
    authors: list[str]


# =============================================================================
# Services
# =============================================================================

class DoctisAIService:
    """
    Service principal de Doctis AI.
    Gère le chargement des modèles et l'analyse des symptômes.
    """

    def __init__(self):
        self.sbert_model: Optional[SentenceTransformer] = None
        self.llm_model: Optional[Llama] = None
        self.pathologies: list = []
        self.pathology_embeddings: Optional[np.ndarray] = None
        self.disclaimer: str = ""

    def load_pathologies(self) -> None:
        """Charge la base de données des pathologies."""
        pathologies_path = settings.DATA_DIR / "pathologies.json"

        if not pathologies_path.exists():
            raise FileNotFoundError(f"Fichier pathologies.json non trouvé: {pathologies_path}")

        with open(pathologies_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.pathologies = data.get("pathologies", [])
        self.disclaimer = data.get("disclaimer", "Consultez un médecin pour tout diagnostic médical.")

        print(f"✅ {len(self.pathologies)} pathologies chargées")

    def load_sbert_model(self) -> None:
        """Charge le modèle SBERT pour les embeddings."""
        print(f"⏳ Chargement du modèle SBERT: {settings.SBERT_MODEL}...")
        self.sbert_model = SentenceTransformer(settings.SBERT_MODEL)
        print("✅ Modèle SBERT chargé")

        # Pré-calcul des embeddings des pathologies
        if self.pathologies:
            symptoms_texts = [p["symptoms_description"] for p in self.pathologies]
            self.pathology_embeddings = self.sbert_model.encode(symptoms_texts)
            print(f"✅ Embeddings pré-calculés pour {len(symptoms_texts)} pathologies")

    def load_llm_model(self) -> None:
        """Charge le modèle LLM quantizé (GGUF)."""
        if not LLAMA_AVAILABLE:
            print("⚠️  LLM non disponible (llama-cpp-python non installé)")
            return

        if not os.path.exists(settings.LLM_MODEL_PATH):
            print(f"⚠️  Fichier LLM non trouvé: {settings.LLM_MODEL_PATH}")
            print("   → Mode dégradé activé (réponses templates)")
            return

        print(f"⏳ Chargement du modèle LLM: {settings.LLM_MODEL_PATH}...")
        self.llm_model = Llama(
            model_path=settings.LLM_MODEL_PATH,
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )
        print("✅ Modèle LLM chargé")

    def compute_similarity(self, user_input: str) -> list[tuple[dict, float]]:
        """
        Calcule la similarité cosinus entre l'input utilisateur
        et les descriptions de symptômes des pathologies.

        Returns:
            Liste de tuples (pathologie, score) triée par score décroissant
        """
        if self.sbert_model is None or self.pathology_embeddings is None:
            raise RuntimeError("Modèle SBERT non initialisé")

        # Encode l'input utilisateur
        user_embedding = self.sbert_model.encode([user_input])

        # Calcule la similarité cosinus
        similarities = cosine_similarity(user_embedding, self.pathology_embeddings)[0]

        # Associe chaque pathologie à son score
        results = list(zip(self.pathologies, similarities))

        # Trie par score décroissant
        results.sort(key=lambda x: x[1], reverse=True)

        return results

    def generate_llm_response(self, pathology: dict, confidence: float) -> str:
        """
        Génère une réponse empathique via le LLM.
        Si le LLM n'est pas disponible, utilise un template.
        """
        if self.llm_model is None:
            # Mode dégradé : template de réponse
            return self._generate_template_response(pathology, confidence)

        # Prompt système médical
        system_prompt = """Tu es Doctis AI, un assistant médical bienveillant et professionnel.
Tu dois générer une réponse empathique pour un patient qui présente des symptômes.
Reste rassurant mais prudent. Rappelle toujours l'importance de consulter un médecin.
Réponds en français, de manière concise (2-3 phrases maximum)."""

        user_prompt = f"""Le patient présente des symptômes correspondant à : {pathology['name']}
Niveau de confiance de l'analyse : {confidence*100:.0f}%
Gravité : {pathology['severity_level']}/5
Conseil médical de base : {pathology['advice']}

Génère une réponse empathique et rassurante pour le patient."""

        # Génération via LLM
        full_prompt = f"<|system|>\n{system_prompt}<|end|>\n<|user|>\n{user_prompt}<|end|>\n<|assistant|>\n"

        response = self.llm_model(
            full_prompt,
            max_tokens=settings.LLM_MAX_TOKENS,
            temperature=settings.LLM_TEMPERATURE,
            stop=["<|end|>", "<|user|>"]
        )

        return response["choices"][0]["text"].strip()

    def _generate_template_response(self, pathology: dict, confidence: float) -> str:
        """Génère une réponse template si le LLM n'est pas disponible."""
        severity_messages = {
            1: "Il s'agit généralement d'une condition bénigne.",
            2: "Cette condition est généralement modérée et gérable.",
            3: "Cette condition mérite une attention médicale.",
            4: "Cette condition nécessite une consultation médicale rapide.",
            5: "Cette condition peut être sérieuse et nécessite une attention médicale urgente."
        }

        severity_msg = severity_messages.get(pathology['severity_level'], "")

        response = f"""D'après l'analyse de vos symptômes, je détecte une possible **{pathology['name']}** avec un niveau de confiance de {confidence*100:.0f}%.

{severity_msg}

**Recommandation :** {pathology['advice']}

N'oubliez pas : seul un professionnel de santé peut établir un diagnostic définitif. Si vos symptômes persistent ou s'aggravent, consultez rapidement un médecin."""

        return response

    def diagnose(self, symptoms: str) -> DiagnosisResponse:
        """
        Effectue le pré-diagnostic complet.

        Args:
            symptoms: Description des symptômes par l'utilisateur

        Returns:
            DiagnosisResponse avec le résultat du diagnostic
        """
        # Calcul de similarité
        matches = self.compute_similarity(symptoms)

        if not matches:
            return DiagnosisResponse(
                success=True,
                matched=False,
                ai_response="Je n'ai pas pu analyser vos symptômes. Veuillez reformuler votre description ou consulter un médecin.",
                disclaimer=self.disclaimer
            )

        # Prend le meilleur match
        best_match, best_score = matches[0]

        # Vérifie le seuil de similarité
        if best_score < settings.SIMILARITY_THRESHOLD:
            return DiagnosisResponse(
                success=True,
                matched=False,
                ai_response=f"Vos symptômes ne correspondent pas de manière suffisamment précise à une pathologie connue dans ma base de données (score: {best_score*100:.0f}%). Je vous recommande de consulter un médecin pour une évaluation personnalisée.",
                disclaimer=self.disclaimer
            )

        # Génère la réponse IA
        ai_response = self.generate_llm_response(best_match, best_score)

        # Construit la réponse
        pathology_match = PathologyMatch(
            id=best_match["id"],
            name=best_match["name"],
            confidence_score=round(float(best_score), 3),
            severity_level=best_match["severity_level"],
            urgency=best_match["urgency"],
            advice=best_match["advice"],
            specialist=best_match["specialist"]
        )

        return DiagnosisResponse(
            success=True,
            matched=True,
            pathology=pathology_match,
            ai_response=ai_response,
            disclaimer=self.disclaimer
        )


# =============================================================================
# Application FastAPI
# =============================================================================

# Instance globale du service
doctis_service = DoctisAIService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    # Startup
    print("\n" + "="*60)
    print("🏥 Démarrage de Doctis AI")
    print(f"   Auteurs: {', '.join(settings.AUTHORS)}")
    print("="*60 + "\n")

    doctis_service.load_pathologies()
    doctis_service.load_sbert_model()
    doctis_service.load_llm_model()

    print("\n✅ Doctis AI prêt à recevoir des requêtes!\n")

    yield

    # Shutdown
    print("\n👋 Arrêt de Doctis AI\n")


# Création de l'application
app = FastAPI(
    title="Doctis AI",
    description="API de pré-diagnostic médical utilisant l'IA (RAG + LLM)",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Endpoints
# =============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Page d'accueil de l'API."""
    return {
        "message": "Bienvenue sur Doctis AI - API de pré-diagnostic médical",
        "version": settings.APP_VERSION,
        "authors": settings.AUTHORS,
        "documentation": "/docs",
        "endpoints": {
            "diagnose": "POST /diagnose",
            "health": "GET /health",
            "pathologies": "GET /pathologies"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Système"])
async def health_check():
    """Vérifie l'état de santé du service."""
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        models_loaded={
            "sbert": doctis_service.sbert_model is not None,
            "llm": doctis_service.llm_model is not None,
            "pathologies_count": len(doctis_service.pathologies)
        },
        authors=settings.AUTHORS
    )


@app.get("/pathologies", tags=["Données"])
async def get_pathologies():
    """Retourne la liste des pathologies disponibles."""
    return {
        "count": len(doctis_service.pathologies),
        "pathologies": [
            {
                "id": p["id"],
                "name": p["name"],
                "severity_level": p["severity_level"]
            }
            for p in doctis_service.pathologies
        ],
        "authors": settings.AUTHORS
    }


@app.post("/diagnose", response_model=DiagnosisResponse, tags=["Diagnostic"])
async def diagnose(input_data: SymptomInput):
    """
    Analyse les symptômes et retourne un pré-diagnostic.

    Le système utilise:
    1. SBERT pour le matching sémantique avec les pathologies connues
    2. LLM pour générer une réponse empathique et personnalisée

    **⚠️ Disclaimer:** Ce service est fourni à titre informatif uniquement
    et ne remplace pas une consultation médicale professionnelle.
    """
    try:
        result = doctis_service.diagnose(input_data.symptoms)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse: {str(e)}"
        )


# =============================================================================
# Point d'entrée
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
