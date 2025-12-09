# Changelog

All notable changes to the **DoctisAImo** project will be documented in this file.

## [V12.0-RAG] - 2025-12-09 (Current)

- **UI/UX**: Complete "Premium" Overhaul. Added Tabs, Custom CSS, and conversational UI.
- **Data**: Integrated 3 new datasets (Symptom2Disease, DiseaseAndSymptoms, Disease precaution).
- **RAG**: Enhanced "Evidence" tab showing exact matches from Kaggle DB.

## [V14.0] - 2025-12-09

### Workflow & DevOps

- **Test Coverage**: Ajout d'une suite de tests unitaires complète (`tests/`) couvrant l'Agent, l'ETL et le Monitoring.
- **CI/CD**: Mise en place d'un pipeline GitHub Actions pour automatiser les tests à chaque push.
- **Dependencies**: Ajout de `pytest` les prérequis.
- **Quality**: Le projet est désormais testé et intégré automatiquement.

## [V13.0] - 2025-12-09

### Optimized

- **Strict Typing**: Ajout de Type Hints (Python) sur l'ensemble du Codebase (`src/data_loader.py`, `src/agent.py`, `app.py`).
- **ETL Modulaire**: Refactoring complet de `data_loader.py` en 5 sous-fonctions indépendantes.
- **Clean Code**: Extraction du CSS dans `inject_custom_css()` pour alléger `app.py`.
- **Robustesse**: Gestion d'erreur renforcée pour l'authentification Kaggle (Fallback Env/Secrets/Token).

## [V11.0] - 2025-12-09

- **Versioning**: Applied strict protocol (1 Mod = 1 Version Bump).

## [V10.0] - 2025-12-09

- **RAG**: Completed RAG System with ETL optimization of 4 datasets.

## [V9.0] - 2025-12-09

- **Fix**: Enhanced .env logic to handle JSON `KAGGLE_API_TOKEN`.

## [V8.1] - 2025-12-09

- **Optimization**: MongoDB logging now overwrites status instead of appending (Storage optimization).

## [V8.0] - 2025-12-09

- **Monitoring**: Added `src/monitoring.py` for Keep-Alive and MongoDB logging.

## [V7.0] - 2025-12-09

- **Security**: Hardened configuration.
  - Added `.gitignore`.
  - Created `.env.example`.
  - Removed local `.env`.

## [V6.0] - 2025-12-09

- **Data**: Added Kaggle API integration.
- **Documentation**: Extensive comments added for code presentation.

## [V5.0] - 2025-12-09

- **Documentation**: Added Amina Medjdoub to authors.
- **Localization**: Optimized French comments and README.

## [V4.0] - 2025-12-09

- **Feature**: Upgrade to Professional Dashboard (Streamlit).
- **Docs**: Added Architecture Diagrams (Mermaid).

## [V3.0] - 2025-12-09

- **Core**: Switch to Gemini API (from OpenAI).
- **Docs**: Added 7 European languages to README.

## [V2.0] - 2025-12-09

- **Logic**: Implemented "Input Enrichment" and "Triage" tasks.

## [V1.0] - 2025-12-09

- **Init**: Project scaffolding and Agent configuration.
