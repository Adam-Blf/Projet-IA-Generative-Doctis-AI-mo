# 🏥 DoctisAImo (v3.0-KAGGLE-MAPS)

> **Assistant de Triage IA Avancé | Advanced AI Triage Assistant**

<div align="center">

[**🇫🇷 Français**](#-français) | [**🇬🇧 English**](#-english) | [**🇪🇸 Español**](#-español)

</div>

---

<a name="-français"></a>

## 🇫🇷 Français

### Vue d'ensemble

**DoctisAImo** est un assistant IA de pointe conçu pour le triage médical d'urgence. Contrairement aux chatbots standards, la version 3.0 utilise une **logique orientée données** (inspirée des datasets médicaux Kaggle) pour interpréter les symptômes avec une rigueur statistique. Il fournit des évaluations de sécurité, des secondes opinions et des plans d'action d'urgence.

### Fonctionnalités

#### 1. 🏥 Triage Intelligent (Urgences)

- **Analyse Data-Driven** : Croise les symptômes signalés avec des clusters de maladies probabilistes.
- **Niveaux d'Urgence** :
  - 🟢 **Code Vert** : Sûr / Faible risque.
  - 🟠 **Code Orange** : Risque modéré / Consultation nécessaire.
  - 🔴 **Code Rouge** : Critique / Interaction d'urgence immédiate.
- **Détection de Langue** : Répond automatiquement dans la langue du patient.

#### 2. 🧠 Seconde Opinion

- **Analyse Approfondie** : Fournit une évaluation des risques détaillée (échelle 1-10).
- **Signaux d'Alarme ("Red Flags")** : Met en évidence les signes critiques.

#### 3. 🛡️ Plan d'Action

- **Checklist d'Urgence** : Étapes immédiates et actionnables générées en temps réel.
- **Instructions Claires** : Pas de jargon médical complexe, juste des actions vitales.

#### 4. 🔗 Enrichissement d'Entrée (Nouveau en v3.0)

- **Prêt pour la Recherche Vectorielle** : Transforme les descriptions brutes en mots-clés médicaux structurés.

### Installation

**Prérequis** : Python 3.8+, Clé API Gemini.

```bash
# 1. Cloner le dépôt
git clone https://github.com/Adam-Blf/Projet-IA-Generative-Doctis-AI-mo.git
cd Projet-IA-Generative-Doctis-AI-mo

# 2. Installer les dépendances
pip install -r requirements.txt
```

### Configuration

Le cerveau de DoctisAImo réside dans `config/prompts.json`. Vous pouvez personnaliser les invites système (System Prompts) et les métadonnées de l'agent.

### Vérification

Pour tester si l'agent est correctement configuré :

```bash
python src/agent.py
```

### ⚠️ Avertissement

**DoctisAImo est un projet de recherche en IA.** Ce n'est pas un professionnel de santé agréé.  
*Appelez toujours les urgences (112/15) en cas de danger vital.*

---

<a name="-english"></a>

## 🇬🇧 English

### Overview

**DoctisAImo** is a state-of-the-art AI assistant designed for emergency medical triage. Version 3.0 leverages **Data-Driven Logic** (inspired by Kaggle medical datasets) to interpret symptoms with statistical rigor. It provides safety assessments, second opinions, and emergency action plans.

### Features

#### 1. 🏥 Intelligent Triage

- **Data-Driven Analysis**: Cross-references reported symptoms with probabilistic disease clusters.
- **Urgency Levels**:
  - 🟢 **Code Green**: Safe / Low risk.
  - 🟠 **Code Orange**: Moderate risk.
  - 🔴 **Code Red**: Critical / Immediate emergency.

#### 2. 🧠 Second Opinion

- **Deep Analysis**: Provides a detailed risk assessment (1-10 scale).
- **Red Flags**: Highlights critical warning signs.

#### 3. 🛡️ Action Plan

- **Emergency Checklist**: Immediate, actionable steps generated in real-time.

#### 4. 🔗 Input Enrichment (New in v3.0)

- **Vector Search Ready**: Transforms raw symptom descriptions into structured medical keywords.

### Installation

**Prerequisites**: Python 3.8+, Gemini API Key.

```bash
# 1. Clone the repository
git clone https://github.com/Adam-Blf/Projet-IA-Generative-Doctis-AI-mo.git
cd Projet-IA-Generative-Doctis-AI-mo

# 2. Install dependencies
pip install -r requirements.txt
```

### Configuration

DoctisAImo's configuration is in `config/prompts.json`. You can customize system prompts and agent metadata here.

### Verification

To test if the agent is correctly configured:

```bash
python src/agent.py
```

### ⚠️ Disclaimer

**DoctisAImo is an AI research project.** It is not a licensed medical professional.  
*Always call emergency services (112/911) in life-threatening situations.*

---

<a name="-español"></a>

## 🇪🇸 Español

### Resumen

**DoctisAImo** es un asistente avanzado de IA para el triaje médico de emergencia. La versión 3.0 utiliza **Lógica Basada en Datos** (estilo Kaggle) para evaluar síntomas con rigor estadístico.

### Funcionalidades Principales

1. **🏥 Triaje Inteligente**: Análisis de seguridad rápido (Verde/Naranja/Rojo).
2. **🧠 Segunda Opinión**: Evaluación detallada de riesgos y "Red Flags".
3. **🛡️ Plan de Acción**: Lista de verificación inmediata para emergencias.
4. **🔗 Enriquecimiento de Entrada**: Generación de palabras clave para bases de datos vectoriales.

### ⚠️ Aviso

**DoctisAImo es un proyecto de investigación.** No sustituye a un médico profesional.  
*Llame siempre a emergencias (112) en situaciones de peligro vital.*
