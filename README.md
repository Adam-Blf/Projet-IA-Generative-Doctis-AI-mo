# Doctis-AI-mo (v1.0 Ready)

![Visitor Badge](https://visitor-badge.laobi.icu/badge?page_id=Adam-Blf.Projet-IA-Generative-Doctis-AI-mo)
![Last Commit](https://img.shields.io/github/last-commit/Adam-Blf/Projet-IA-Generative-Doctis-AI-mo)
![Top Language](https://img.shields.io/github/languages/top/Adam-Blf/Projet-IA-Generative-Doctis-AI-mo)
![Language Count](https://img.shields.io/github/languages/count/Adam-Blf/Projet-IA-Generative-Doctis-AI-mo)
![Activity](https://img.shields.io/github/commit-activity/y/Adam-Blf/Projet-IA-Generative-Doctis-AI-mo)

**Med-RAG MVP : Assistant de Triage Médical Multilingue (IA Générative + Analyse Sémantique).**

## 🧠 Architecture du Flux (Déployable)

```mermaid
graph TD
    User((Utilisateur)) -->|1. URL Vercel| Client["Frontend (Client/)"]
    Client -->|2. POST /api/triage| Server{"Backend Flask (Server/)"}
    
    subgraph Render Cloud
        Server -->|3. Load Data| Data[("Remote JSON")]
        Server -->|4. SBERT| Engine[Semantic Engine]
    end
    
    Engine -->|5. Match| Top3[Top 3 Pathologies]
    Top3 -->|6. RAG Prompt| GenAI[Google Gemini]
    GenAI -.->|Quota Exceeded?| Rotate[Rotation Modèles]
    Rotate -.-> GenAI
    
    GenAI -->|7. Résumé| Server
    Server -->|8. JSON| Client
```

## 🌍 Langues Supportées

🇫🇷 Français | 🇬🇧 Anglais | 🇪🇸 Espagnol | 🇮🇹 Italien | 🇵🇹 Portugais | 🇷🇺 Russe | 🇩🇪 Allemand | 🇹🇷 Turc

## 🚀 Installation & Développement Local

Le projet est divisé en deux parties :

### 1. Backend (API)

```bash
cd server
pip install -r requirements.txt
python app.py
# API running at http://127.0.0.1:5000
```

### 2. Frontend (Client)

Ouvrez simplement `client/index.html` dans votre navigateur.
*Note : Assurez-vous que `client/static/js/config.js` pointe bien vers `http://127.0.0.1:5000`.*

## ☁️ Déploiement

### Backend (Render)

1. Connectez le repo à **Render**.
2. Le fichier `render.yaml` à la racine configurera automatiquement le service Python dans le dossier `server/`.

### Frontend (Vercel)

1. Connectez le repo à **Vercel**.
2. Le fichier `vercel.json` à la racine configurera le déploiement statique du dossier `client/`.
3. **Une fois déployé :** Copiez l'URL de l'API Render et collez-la dans `client/static/js/config.js` avant de push la version finale.
