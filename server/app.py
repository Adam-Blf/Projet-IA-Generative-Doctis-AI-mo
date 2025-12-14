import os
import json
import requests
import numpy as np
import functools
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from google.api_core import exceptions
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes (Allow Vercel frontend to access)
CORS(app) 

# --- Security Headers ---
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# --- Health Check ---
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "doctis-ai-mo"}), 200

# --- Configuration Gemini ---
GENAI_API_KEY = os.getenv("GOOGLE_API_KEY")
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)

# Liste de priorité des modèles (User Request)
# Rotation automatique si Quota Exceeded
MODEL_ROTATION_LIST = [
    'gemini-2.5-flash-lite',
    'gemini-2.5-flash',
    'gemma-3-12b',
    'gemini-1.5-flash', # Fallback Safe
    'gemini-pro'        # Fallback Standard
]

# --- Engine Setup ---
DATA_SOURCE_URL = "https://gist.githubusercontent.com/Adam-Blf/raw/fake-gist-id/diseases.json" 
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
model = None
pathology_data = []
pathology_embeddings = None

# --- Logic ---

def fetch_disease_data():
    try:
        # Mock Data (Same as before)
        data = [
            {"id": "D01", "name": "Migraine", "symptoms": ["unilateral head pain", "pulsating sensation", "nausea", "vomiting", "sensitivity to light", "photophobia"]},
            {"id": "D02", "name": "Influenza (Flu)", "symptoms": ["fever", "chills", "muscle aches", "cough", "congestion", "runny nose", "headache", "fatigue"]},
            {"id": "D03", "name": "Gastroenteritis", "symptoms": ["watery diarrhea", "abdominal cramps", "pain", "nausea", "vomiting", "low-grade fever"]},
            {"id": "D04", "name": "Acute Bronchitis", "symptoms": ["cough", "production of mucus", "fatigue", "shortness of breath", "slight fever", "chest discomfort"]},
            {"id": "D05", "name": "Panic Attack", "symptoms": ["sense of impending doom", "rapid heart rate", "sweating", "trembling", "shortness of breath", "chills", "hot flashes"]}
        ]
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

def initialize_engine():
    global model, pathology_data, pathology_embeddings
    print(f"Loading SBERT model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    pathology_data = fetch_disease_data()
    corpus = [", ".join(p["symptoms"]) for p in pathology_data]
    print("Encoding vectors...")
    pathology_embeddings = model.encode(corpus, convert_to_tensor=True)
    print("Engine Initialized.")

def generate_summary_with_rotation(prompt):
    """
    Tente de générer le résumé en essayant les modèles un par un si Quota Exceeded.
    """
    if not GENAI_API_KEY:
        return "API Key Missing."

    last_error = None

    for model_name in MODEL_ROTATION_LIST:
        try:
            print(f"Attempting RAG with model: {model_name}")
            gen_model = genai.GenerativeModel(model_name)
            response = gen_model.generate_content(prompt)
            return response.text
        except exceptions.ResourceExhausted:
            print(f"Quota Exceeded for {model_name}. Switching to next...")
            continue # Try next model
        except Exception as e:
            print(f"Error with {model_name}: {e}")
            last_error = e
            # If it's not a quota error (e.g. Model Not Found), we strictly should try next too? 
            # Yes, let's robust filtering.
            continue
            
    return f"Service currently unavailable. All models busy or failed. ({str(last_error)})"

@functools.lru_cache(maxsize=100)
def cached_rag(user_input, top_matches_str, lang):
    prompt = (
        f"Act as a medical assistant. Language: {lang}. "
        f"Analysis: User reports '{user_input}'. "
        f"Semantic match indicates: {top_matches_str}. "
        "Provide a brief, empathetic summary and advice. "
        "Strictly Start with: 'DISCLAIMER: I am an AI, consult a doctor.'"
    )
    return generate_summary_with_rotation(prompt)

# --- Routes ---

@app.route('/api/triage', methods=['POST'])
def triage():
    try:
        data = request.json
        user_desc = data.get('description', '').strip()
        lang = data.get('lang', 'en')

        if not user_desc:
            return jsonify({"error": "No input"}), 400

        user_embedding = model.encode(user_desc, convert_to_tensor=True)
        cosine_scores = util.cos_sim(user_embedding, pathology_embeddings)[0]
        
        top_results = []
        # Score processing
        scores_list = cosine_scores.tolist()
        indexed_scores = sorted(list(enumerate(scores_list)), key=lambda x: x[1], reverse=True)[:3]

        for idx, score in indexed_scores:
            path = pathology_data[idx]
            top_results.append({
                "name": path["name"],
                "score": float(score),
                "probability": "High" if score >= 0.7 else "Moderate" if score >= 0.5 else "Low"
            })

        matches_str = ", ".join([f"{r['name']} ({r['score']:.2f})" for r in top_results])
        summary = cached_rag(user_desc, matches_str, lang)

        return jsonify({
            "matches": top_results,
            "advice": summary
        })

    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    initialize_engine()
    app.run(debug=True, port=5000)
