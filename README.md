# Doctis-AI-mo

![Visitor Badge](https://visitor-badge.laobi.icu/badge?page_id=Adam-Blf.Projet-IA-Generative-Doctis-AI-mo)
![Last Commit](https://img.shields.io/github/last-commit/Adam-Blf/Projet-IA-Generative-Doctis-AI-mo)
![Top Language](https://img.shields.io/github/languages/top/Adam-Blf/Projet-IA-Generative-Doctis-AI-mo)
![Language Count](https://img.shields.io/github/languages/count/Adam-Blf/Projet-IA-Generative-Doctis-AI-mo)
![Activity](https://img.shields.io/github/commit-activity/y/Adam-Blf/Projet-IA-Generative-Doctis-AI-mo)

**Med-RAG MVP : Assistant de Triage Médical Multilingue (IA Générative + Analyse Sémantique).**

## 🧠 Architecture du Flux (AISCA)
```mermaid
graph TD
    User((Utilisateur)) -->|1. Symptômes + Langue| Client[Frontend JS]
    Client -->|2. POST /api/triage| Server{Flask API}
    
    subgraph Backend Core
        Server -->|3. Load Data| Data[(Remote JSON)]
        Server -->|4. Vectorisation| SBERT[SBERT Model]
        Data --> SBERT
        SBERT -->|5. Cosine Similarity| Top3[Top 3 Pathologies]
    end
    
    Top3 -->|6. RAG Prompt| GenAI[Google Gemini / LLM]
    GenAI -->|7. Résumé & Conseils| Server
    Server -->|8. Réponse JSON| Client
    Client -->|9. Affichage| User
```

## 🌍 Langues Supportées
🇫🇷 Français | 🇬🇧 Anglais | 🇪🇸 Espagnol | 🇮🇹 Italien | 🇵🇹 Portugais | 🇷🇺 Russe | 🇩🇪 Allemand | 🇹🇷 Turc

## 🚀 Fonctionnalités
*   **Triage Intelligent :** Analyse sémantique des symptômes via `sentence-transformers` (SBERT).
*   **Zero-Database :** Chargement des pathologies depuis une source distante (Remote Data Fetching).
*   **RAG (Retrieval Augmented Generation) :** Résumé et conseils générés par IA (Gemini/OpenAI).
*   **Interface Multilingue :** Client Web moderne "Medical Blue".

## 🛠️ Stack Technique
*   **Backend :** Python, Flask, Sentence-Transformers.
*   **Frontend :** HTML5, CSS3, Vanilla JS.

## 📦 Installation & Démarrage

1.  **Cloner le projet :**
    ```bash
    git clone https://github.com/Adam-Blf/Projet-IA-Generative-Doctis-AI-mo.git
    cd Projet-IA-Generative-Doctis-AI-mo
    ```

2.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Lancer le serveur :**
    ```bash
    python app.py
    ```
    *(Le premier lancement téléchargera le modèle d'IA ~400Mo)*

4.  **Accéder à l'application :**
    Ouvrez `http://127.0.0.1:5000`
