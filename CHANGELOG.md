# Changelog

## [16.8-Optimized] - 2025-12-11

### Added

- **Formulaire Médical Complet** : Ajout des champs Taille, Poids, Calcul IMC automatique, Antécédents, et Constantes.
- **Frontend Découplé** : Interface déplacée dans `frontend/` pour un déploiement optimisé sur Vercel.
- **Architecture FastAPI** : Migration du backend vers FastAPI pour de meilleures performances et une API RESTful.
- **Déploiement Hybride** : Support natif pour le déploiement Backend (Render) et Frontend (Vercel).
- **Animations UI** : Ajout d'animations `fadeInUp` et de micro-interactions pour une expérience utilisateur premium.

### Changed

- Refonte complète de l'interface utilisateur (HTML/CSS/JS natifs) en remplacement de Streamlit.
- Mise à jour de la documentation (`README.md` et `DEPLOYMENT.md`) pour refléter la nouvelle architecture.
- Optimisation du moteur RAG pour inclure les nouvelles données biométriques dans le contexte.

### Fixed

- Correction des problèmes de CORS et d'URL API dynamique via `script.js`.
- Amélioration de la sécurité (XSS) et validation des entrées utilisateur.

## [v1.0.0] - 2025-12-08

### Initial Release

- Lancement initial avec Streamlit.
- Intégration Gemini 2.0 et RAG basique.
