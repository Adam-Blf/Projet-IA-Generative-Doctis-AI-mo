# ==============================================================================
# DOCTIS-AI-MO: APPLICATION PRINCIPALE (STREAMLIT DASHBOARD)
# Version: 5.0-RAG
# Auteurs: Adam Beloucif & Amina Medjdoub
# ==============================================================================

"""
Ce fichier est le point d'entrée de l'application Web.
Il utilise la bibliothèque Streamlit pour générer une interface utilisateur interactive.

Responsabilités du fichier :
1. Configuration de la page et de l'authentification API (Gemini).
2. Initialisation de l'agent IA (DoctisAgent) et connexion à Kaggle (DataLoader).
3. Gestion de l'interface utilisateur (Sidebar, Formulaires, Colonnes).
4. Logique de "RAG-lite" (Retrieval Augmented Generation) :
   - Recherche de symptômes dans le dataset réel Kaggle.
   - Injection des données trouvées dans le prompt de l'IA.
5. Affichage des résultats avec des alertes visuelles et des options d'export.
"""

import streamlit as st
import google.generativeai as genai
import json
import os
import pandas as pd
from src.agent import DoctisAgent
from src.data_loader import download_medical_dataset, load_symptom_data
from src.monitoring import init_monitor

# ==============================================================================
# 0. INITIALISATION DU MONITORING (Keep-Alive)
# ==============================================================================
init_monitor()

# ------------------------------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE
# ------------------------------------------------------------------------------
# Configuration globale de la fenêtre du navigateur (Titre, Icône, Layout Large)
st.set_page_config(
    page_title="DoctisAImo V5 - Medical Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# 2. FONCTIONS UTILITAIRES (BACKEND)
# ------------------------------------------------------------------------------

def configure_gemini():
    """
    Configure le client API Google Gemini.
    Récupère la clé API 'GOOGLE_API_KEY' depuis les secrets Streamlit ou les variables d'environnement.
    Arrête l'exécution si la clé est manquante.
    """
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY")
    except (FileNotFoundError, KeyError):
        api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        st.error("❌ CLÉ API MANQUANTE. Veuillez définir GOOGLE_API_KEY dans .streamlit/secrets.toml ou .env")
        st.stop() # Arrêt critique
    
    genai.configure(api_key=api_key)

@st.cache_resource
def load_agent():
    """
    Instancie et met en cache l'agent Doctis.
    Le décorateur @st.cache_resource évite de recharger l'agent à chaque interaction utilisateur,
    ce qui optimise les performances.
    """
    return DoctisAgent()

@st.cache_data
def get_kaggle_data():
    """
    Gère le cycle de vie des données Kaggle :
    1. Télécharge le dataset si nécessaire (mise en cache).
    2. Charge le CSV en mémoire (Pandas DataFrame).
    """
    with st.spinner("🔄 Initialisation de la Base de Connaissances Kaggle..."):
        success, msg = download_medical_dataset()
        if not success:
            st.warning(f"⚠️ Mode Hors-Ligne (Kaggle indisponible) : {msg}")
            return None
        
        df = load_symptom_data()
        return df

# ------------------------------------------------------------------------------
# 3. INITIALISATION (SETUP)
# ------------------------------------------------------------------------------
# Exécution au démarrage du script
configure_gemini()
agent = load_agent()
metadata = agent.get_agent_metadata()

# Chargement des données médicales réelles
df_medical = get_kaggle_data()

# ------------------------------------------------------------------------------
# 4. INTERFACE UTILISATEUR : BARRE LATÉRALE (SIDEBAR)
# ------------------------------------------------------------------------------
st.sidebar.title(f"🏥 {metadata.get('name')}")
st.sidebar.caption(f"Version: {metadata.get('version')}")

# Menu de navigation
mode = st.sidebar.radio(
    "Mode de Triage / Triage Mode",
    [
        "🚑 Urgence & Triage",
        "🧠 Seconde Opinion",
        "📋 Plan d'Action",
        "ℹ️ À propos"
    ]
)

st.sidebar.markdown("---")

# Disclaimer légal (Indispensable pour une app médicale)
with st.sidebar.expander("⚠️ Disclaimer / Avertissement", expanded=True):
    st.error(
        """
        **DO NOT USE FOR LIFE-THREATENING EMERGENCIES.**
        
        This AI tool is for informational purposes only.
        Always call 112/911 in case of emergency.
        
        *Ce système est une IA d'aide à la décision.
        En cas d'urgence vitale, appelez le 15 ou le 112.*
        """
    )

# ------------------------------------------------------------------------------
# 5. LOGIQUE PRINCIPALE (MAIN AREA)
# ------------------------------------------------------------------------------

# CASE 1 : PAGE "À PROPOS"
if mode == "ℹ️ À propos":
    st.title("ℹ️ À propos de DoctisAImo")
    st.markdown("""
    ### Assistant de Triage Médical Avancé (V5 - RAG Integrated)
    
    **DoctisAImo** est un systéme expert piloté par l'IA générative (Gemini 2.0 Flash) et enrichi par des données réelles.
    
    #### Architecture Technique :
    - **Frontend** : Streamlit (Python)
    - **Cerveau** : Google Gemini 2.0 via API
    - **Mémoire** : Dataset Kaggle 'Disease Symptom Description'
    - **Pattern** : RAG-lite (Retrieval, Augmentation, Generation)
    
    ---
    *Développé par Adam Beloucif & Amina Medjdoub - Projet Open Source*
    """)

# CASE 2 : MODES MÉDICAUX (TRIAGE, SECONDE OPINION, PLAN)
else:
    # Mapping entre le nom du bouton et la clé de configuration dans prompts.json
    task_map = {
        "🚑 Urgence & Triage": "triage_urgency",
        "🧠 Seconde Opinion": "second_opinion",
        "📋 Plan d'Action": "action_plan"
    }
    current_task = task_map[mode]
    
    st.title(mode)
    
    # --- LAYOUT EN DEUX COLONNES ---
    col_input, col_result = st.columns([1, 1], gap="large")
    
    # COLONNE GAUCHE : SAISIE
    with col_input:
        st.subheader("📝 Données Patient / Patient Data")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Âge", 0, 120, 30)
            with c2:
                gender = st.selectbox("Genre", ["H/M", "F/F", "Autre/Other"])
            
            symptoms = st.text_area("Symptômes & Histoire / Symptoms & History", height=150, placeholder="Ex: Douleur thoracique irradiant dans le bras gauche...")
            
            analyze_btn = st.button("🚀 Analyser / Analyze", use_container_width=True, type="primary")

    # COLONNE DROITE : RÉSULTATS
    with col_result:
        st.subheader("📊 Résultats & IA / Results & AI")
        
        if analyze_btn and symptoms:
            with st.spinner("🧠 Analyse Data-Driven en cours..."):
                try:
                    # A. RÉCUPÉRATION DU TEMPLATE DE PROMPT
                    task_config = agent.config['tasks'][current_task]
                    system_instruction = task_config['system_prompt']
                    user_template = task_config['user_template']
                    
                    # B. LOGIQUE RAG (Retrieval Augmented Generation) SIMPLIFIÉE
                    # On cherche des correspondances dans le dataset Kaggle chargé
                    kaggle_context = "Aucune donnée spécifique trouvée dans la base."
                    
                    if df_medical is not None:
                        # Recherche naïve de mots-clés dans la première colonne du CSV
                        # (Supposons que la col 1 contient les maladies ou symptômes)
                        # On cherche si les symptômes saisis correspondent à des entrées
                        try:
                            # On convertit tout en string pour la recherche
                            matches = df_medical[df_medical.apply(lambda row: row.astype(str).str.contains(symptoms, case=False).any(), axis=1)]
                            
                            if not matches.empty:
                                # On prend les 3 meilleures correspondances pour ne pas saturer le prompt
                                top_matches = matches.head(3).to_string(index=False)
                                kaggle_context = f"DATASET KAGGLE (Preuves Statistiques) :\n{top_matches}"
                            else:
                                kaggle_context = "Recherche dataset effectuée : Aucune correspondance directe."
                        except Exception as e:
                            kaggle_context = f"Erreur lecture dataset: {e}"

                    # C. CONSTRUCTION DU PROMPT FINAL
                    # On injecte les données Kaggle dans le champ 'nlp_matches_str' du template
                    prompt = user_template.format(
                        first_name="Patient", last_name="", 
                        age=age, gender=gender, 
                        symptoms=symptoms, 
                        nlp_matches_str=kaggle_context, # <--- L'injection magie opérée ici
                        nlp_matches_json="{}" 
                    )
                    
                    # D. APPEL API (GÉNÉRATION)
                    # On utilise le modèle défini dans la config
                    model = genai.GenerativeModel(
                        metadata.get('default_model', 'gemini-2.0-flash'),
                        system_instruction=system_instruction
                    )
                    
                    response = model.generate_content(prompt)
                    clean_resp = response.text.replace("```json", "").replace("```", "").strip()
                    
                    # E. AFFICHAGE INTELLIGENT
                    
                    # Si c'est du JSON (Triage)
                    if current_task == "triage_urgency" or (clean_resp.startswith("{") and clean_resp.endswith("}")):
                        try:
                            data = json.loads(clean_resp)
                            
                            # 1. Badge d'Urgence (Code Couleur)
                            urgency = data.get("urgency_level", "Unknown")
                            if "Green" in urgency:
                                st.success(f"### 🟢 {urgency}")
                            elif "Orange" in urgency:
                                st.warning(f"### 🟠 {urgency}")
                            elif "Red" in urgency:
                                st.error(f"### 🔴 {urgency} - ALERTE")
                            else:
                                st.info(f"### {urgency}")
                            
                            # 2. Cartes d'Analyse
                            with st.container(border=True):
                                st.markdown("#### 🩺 Analyse Clinique")
                                st.write(data.get("analysis", "No analysis provided."))
                            
                            with st.container(border=True):
                                st.markdown("#### 🛡️ Recommandation")
                                st.write(data.get("recommendation", "No recommendation provided."))
                                
                            with st.expander("📈 Raisonnement Statistique & Sources"):
                                st.info(data.get("reasoning", "No reasoning provided."))
                                st.caption("Source des données : Kaggle Disease Symptom Description Dataset")
                                st.text(kaggle_context) # Affiche les données brutes injectées pour transparence

                            # 3. Export
                            st.divider()
                            st.subheader("💾 Exporter le Rapport / Export Report")
                            
                            c_down1, c_down2 = st.columns(2)
                            
                            # JSON Download
                            json_str = json.dumps(data, indent=2, ensure_ascii=False)
                            c_down1.download_button(
                                label="📥 Télécharger JSON",
                                data=json_str,
                                file_name="doctis_report.json",
                                mime="application/json"
                            )
                            
                            # Text Download
                            text_report = f"""DOCTIS-AI-MO REPORT (V4)
---------------------------
Date: {pd.Timestamp.now()}
Patient: {age} ans, {gender}
Symptômes: {symptoms}

URGENCY: {urgency}
SOURCE DATA: {kaggle_context if len(kaggle_context) < 100 else 'Kaggle Dataset Integrated'}
---------------------------
ANALYSIS:
{data.get('analysis')}

RECOMMENDATION:
{data.get('recommendation')}
---------------------------
"""
                            c_down2.download_button(
                                label="📥 Télécharger Texte",
                                data=text_report,
                                file_name="doctis_report.txt",
                                mime="text/plain"
                            )
                                
                        except json.JSONDecodeError:
                            st.warning("⚠️ L'IA a répondu en texte brut (JSON malformé).")
                            st.write(response.text)
                            
                    # Si c'est du Texte libre (Seconde Opinion / Action Plan)
                    else:
                        with st.container(border=True):
                            st.markdown(response.text)
                            
                except Exception as e:
                    st.error(f"Erreur Système : {str(e)}")
                    
        elif analyze_btn:
            st.warning("⚠️ Veuillez décrire les symptômes.")
        else:
            st.info("👈 Remplissez le formulaire pour démarrer l'analyse.")
