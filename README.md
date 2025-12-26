# 🏥 Doctis AI - Assistant de Pré-diagnostic Médical

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Projet de validation - Module IA Générative & Data Engineering**
>
> EFREI Paris - Promotion 2025

---

## 👥 Auteurs

| Nom | Rôle |
|-----|------|
| **Adam Beloucif** | Développeur Full-Stack & ML Engineer |
| **Amina Medjdoub** | Développeur Full-Stack & Data Engineer |

---

## 📋 Description

**Doctis AI** est un assistant intelligent de pré-diagnostic médical. L'utilisateur décrit ses symptômes en langage naturel, et l'IA :

1. **Analyse sémantiquement** la description des symptômes
2. **Identifie** la pathologie la plus probable dans sa base de connaissances
3. **Génère** une réponse empathique et informative avec des recommandations

### Exemple d'utilisation

```
👤 Patient: "J'ai mal au ventre en bas à droite depuis ce matin, avec des nausées et un peu de fièvre"

🤖 Doctis AI: "D'après l'analyse de vos symptômes, je détecte une possible Appendicite
avec un niveau de confiance de 78%. Cette condition peut être sérieuse et nécessite
une attention médicale urgente. Consultez immédiatement les urgences..."
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│                    (Vercel - Next.js)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Interface utilisateur React + Tailwind CSS         │   │
│  │  - Formulaire de saisie des symptômes              │   │
│  │  - Affichage du diagnostic avec jauge de confiance │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                              │
│                    (Render - FastAPI)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. SBERT (all-MiniLM-L6-v2)                        │   │
│  │     → Matching sémantique des symptômes             │   │
│  │                                                      │   │
│  │  2. LLM Quantizé (GGUF - CPU)                       │   │
│  │     → Génération de réponses empathiques            │   │
│  │                                                      │   │
│  │  3. Base de pathologies (JSON)                      │   │
│  │     → Référentiel de maladies et symptômes          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Stack Technique

| Composant | Technologie | Hébergement |
|-----------|-------------|-------------|
| Frontend | Next.js 14, React, Tailwind CSS | Vercel |
| Backend | FastAPI, Python 3.11 | Render |
| Embeddings | Sentence-Transformers (SBERT) | - |
| LLM | llama-cpp-python (GGUF, CPU) | - |
| RAG | Similarité cosinus sur embeddings | - |

---

## 🚀 Installation

### Prérequis

- Python 3.11+
- Node.js 18+
- Git

### 1. Cloner le repository

```bash
git clone https://github.com/Adam-Blf/Projet-IA-Generative-Doctis-AI-mo.git
cd Projet-IA-Generative-Doctis-AI-mo
```

### 2. Backend (FastAPI)

```bash
# Aller dans le dossier backend
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Télécharger le modèle GGUF (voir section ci-dessous)

# Lancer le serveur
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend (Next.js)

```bash
# Aller dans le dossier frontend
cd frontend

# Installer les dépendances
npm install

# Configurer l'URL de l'API
cp .env.example .env.local
# Éditer .env.local pour définir NEXT_PUBLIC_API_URL

# Lancer le serveur de développement
npm run dev
```

---

## 📥 Téléchargement du modèle LLM

Le modèle GGUF doit être placé dans `backend/models/`.

### Option 1 : Utiliser un modèle pré-entraîné (Recommandé pour tester)

```bash
# Créer le dossier models
mkdir -p backend/models

# Télécharger TinyLlama (léger, ~700 Mo)
wget -O backend/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf \
  https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

### Option 2 : Fine-tuner votre propre modèle

Suivez le guide dans [`training/TRAINING.md`](training/TRAINING.md) pour :
1. Fine-tuner Phi-3 ou TinyLlama sur des données médicales
2. Convertir le modèle en format GGUF
3. Quantifier pour optimiser la taille

---

## 📁 Structure du Projet

```
DoctisAimo/
├── backend/
│   ├── data/
│   │   └── pathologies.json    # Base de données des maladies
│   ├── models/
│   │   └── *.gguf              # Modèle LLM quantifié
│   ├── main.py                 # API FastAPI
│   └── requirements.txt        # Dépendances Python
│
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx        # Page principale
│   │       ├── layout.tsx      # Layout Next.js
│   │       └── globals.css     # Styles Tailwind
│   ├── package.json
│   └── tailwind.config.ts
│
├── training/
│   ├── TRAINING.md             # Guide de fine-tuning
│   └── train_colab.ipynb       # Notebook Google Colab
│
└── README.md                   # Ce fichier
```

---

## 🔌 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/` | Page d'accueil de l'API |
| `GET` | `/health` | Vérification de l'état du service |
| `GET` | `/pathologies` | Liste des pathologies disponibles |
| `POST` | `/diagnose` | Analyse des symptômes |

### Exemple de requête `/diagnose`

```bash
curl -X POST "http://localhost:8000/diagnose" \
  -H "Content-Type: application/json" \
  -d '{"symptoms": "J ai mal au ventre en bas à droite avec des nausées"}'
```

### Exemple de réponse

```json
{
  "success": true,
  "matched": true,
  "pathology": {
    "id": "appendicitis",
    "name": "Appendicite",
    "confidence_score": 0.782,
    "severity_level": 5,
    "urgency": "URGENCE MÉDICALE",
    "advice": "Consultez immédiatement les urgences...",
    "specialist": "Chirurgien digestif / Urgentiste"
  },
  "ai_response": "D'après l'analyse de vos symptômes...",
  "disclaimer": "Ces informations sont fournies à titre indicatif...",
  "authors": ["Adam Beloucif", "Amina Medjdoub"]
}
```

---

## 🧪 Tests

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm run test
```

---

## 🚀 Déploiement

### Backend sur Render

1. Créer un nouveau Web Service sur [Render](https://render.com)
2. Connecter le repository GitHub
3. Configurer :
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Ajouter le modèle GGUF (via stockage externe ou Git LFS)

### Frontend sur Vercel

1. Importer le projet sur [Vercel](https://vercel.com)
2. Configurer le dossier racine : `frontend`
3. Ajouter la variable d'environnement :
   - `NEXT_PUBLIC_API_URL`: URL de votre API Render

---

## ⚠️ Avertissement

> **Ce service est fourni à titre informatif uniquement et ne remplace en aucun cas une consultation médicale professionnelle.**
>
> En cas de symptômes graves ou persistants, consultez immédiatement un médecin ou appelez les services d'urgence.

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- EFREI Paris pour le module IA Générative & Data Engineering
- Hugging Face pour les modèles et datasets
- La communauté llama.cpp pour l'optimisation CPU

---

<div align="center">

**Projet réalisé par Adam Beloucif & Amina Medjdoub**

EFREI Paris - 2025

</div>
