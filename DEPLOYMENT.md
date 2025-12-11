# 🚀 Guide de Déploiement : DoctisAImo v2.0

Ce projet est optimisé pour un déploiement hybride :

- **Backend (API)** : Render
- **Frontend (UI)** : Vercel

---

## 1. Backend (Render)

Héberge l'API Python (FastAPI) et le moteur d'IA.

1. Créez un compte sur [Render.com](https://render.com).
2. Cliquez sur **"New + "** -> **"Web Service"**.
3. Connectez votre dépôt GitHub.
4. **Configuration** :
    - **Name** : `doctis-backend`
    - **Environment** : `Python 3`
    - **Build Command** : `pip install -r requirements.txt`
    - **Start Command** : `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Variables d'Environnement** (Section "Environment") :
    - `GOOGLE_API_KEY`: Votre clé Gemini.
    - `OPENAI_API_KEY`: (Optionnel) Votre clé OpenAI.

> **Notez l'URL** fournie par Render (ex: `https://doctis-backend.onrender.com`).

---

## 2. Frontend (Vercel)

Héberge l'interface statique pour une performance maximale.

1. Créez un compte sur [Vercel.com](https://vercel.com).
2. Importez votre dépôt GitHub.
3. **Configuration du Projet** :
    - **Framework Preset** : `Other`
    - **Root Directory** : Cliquez sur "Edit" et sélectionnez `frontend`.
4. **Déploiement** : Cliquez sur **Deploy**.

---

## 3. Liaison (Configuration Finale)

Pour que le Frontend (Vercel) parle au Backend (Render) :

1. Allez sur votre tableau de bord **Vercel** -> **Settings** -> **Environment Variables**.
2. Ajoutez une nouvelle variable :
    - **Key** : `NEXT_PUBLIC_API_URL` (ou simplement modifiez `config.js` si pas de build system)
    - **Value** : L'URL de votre backend Render (ex: `https://doctis-backend.onrender.com`) without trailing slash.
3. **Redéployez** sur Vercel.

*Note : Le code local est configuré pour détecter automatiquement si vous êtes en production ou en local.*
