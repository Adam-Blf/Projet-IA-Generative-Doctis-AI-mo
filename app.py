# ==============================================================================
# DOCTIS-AI-MO: APPLICATION PRINCIPALE (STREAMLIT DASHBOARD)
# Version: v8.0-RAG (Premium UI)
# Auteurs: Adam Beloucif & Amina Medjdoub
# ==============================================================================

import streamlit as st
import google.generativeai as genai
import json
import os
import pandas as pd
from src.agent import DoctisAgent
from src.data_loader import load_knowledge_base
from src.monitoring import init_monitor

# ==============================================================================
# 0. INIT & CONFIG
# ==============================================================================
st.set_page_config(
    page_title="DoctisAImo V8 - Intelligent Triage",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Premium Medical" Content
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom Header */
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 700;
    }
    
    /* Card-like containers for Input and Results */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Primary Button Style */
    div.stButton > button {
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

init_monitor()

# ------------------------------------------------------------------------------
# 1. LOGIC HELPERS
# ------------------------------------------------------------------------------
def configure_gemini():
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    except:
        api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        st.error("❌ CLÉ API MANQUANTE (GOOGLE_API_KEY).")
        st.stop()
    
    genai.configure(api_key=api_key)

@st.cache_resource
def load_agent():
    return DoctisAgent()

@st.cache_data
def get_kaggle_data():
    with st.spinner("🔄 Chargement de la Base de Connaissances V7..."):
        return load_knowledge_base()

# Init Resources
configure_gemini()
agent = load_agent()
df_medical = get_kaggle_data()
metadata = agent.get_agent_metadata()

# ------------------------------------------------------------------------------
# 2. SIDEBAR NAVIGATION
# ------------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/doctor-male.png", width=80)
    st.title("DoctisAImo")
    st.caption(f"v{metadata.get('version')} • RAG-Enhanced")
    
    st.markdown("---")
    
    mode = st.radio(
        "Module Clinique",
        ["🚑 Triage Urgence", "🧠 Seconde Opinion", "ℹ️ À propos"],
        captions=["Code Vert/Orange/Rouge", "Analyse différentielle", "Crédits & Tech"]
    )
    
    st.markdown("---")
    
    # Kpi rapides
    c1, c2 = st.columns(2)
    c1.metric("Dataset", f"{len(df_medical) if df_medical is not None else 0}", "Maladies")
    c2.metric("Status", "Online", delta_color="normal")
    
    st.warning(
        "**AVERTISSEMENT**\n\nCeci est une IA. En cas d'urgence vitale, appelez le 15 ou le 112.",
        icon="⚠️"
    )

# ------------------------------------------------------------------------------
# 3. MAIN INTERFACE
# ------------------------------------------------------------------------------

# HEADER
st.title(f"{mode}")
st.markdown("---")

if mode == "ℹ️ À propos":
    st.markdown("""
    ### 🌟 Le Futur du Triage Médical
    
    **DoctisAImo V7** repousse les limites de l'assistance médicale par IA en combinant :
    1.  **Google Gemini 2.0 (Flash)** : Pour le raisonnement clinique rapide et empathique.
    2.  **RAG Dynamique** : Une base de connaissances fusionnée de 4 datasets Kaggle (Symptômes, Précautions, Descriptions, Sévérité).
    3.  **UX Premium** : Une interface pensée pour les praticiens.
    
    ---
    **Auteurs** : Adam Beloucif & Amina Medjdoub  
    *Projet Open Source à but éducatif et de recherche.*
    """)

else:
    # --- MEDICAL MODULES ---
    
    # 1. INPUT PANEL
    col_left, col_right = st.columns([1, 1.2], gap="large")
    
    with col_left:
        st.subheader("📝 Dossier Patient")
        st.caption("Remplissez les informations cliniques pour lancer l'analyse IA.")
        
        with st.form("triage_form"):
            c1, c2 = st.columns(2)
            age = c1.number_input("Âge", 0, 120, 35)
            gender = c2.selectbox("Genre", ["Homme", "Femme", "Autre"])
            
            symptoms = st.text_area(
                "Tableau Clinique (Symptômes & Histoire)",
                height=200,
                placeholder="Ex: Patient de 35 ans se plaignant de céphalées intenses, photophobie et raideur de la nuque depuis 4h..."
            )
            
            submitted = st.form_submit_button("Lancer l'Analyse ⚡", use_container_width=True)

    # 2. ANALYSIS RESULTS
    with col_right:
        if submitted and symptoms:
            # --- RAG SEARCH LOGIC ---
            kaggle_context = ""
            matches_found = []
            
            if df_medical is not None:
                # Recherche V7 (Optimisée sur 'all_symptoms')
                keywords = [w.lower() for w in symptoms.split() if len(w) > 3]
                if not keywords: keywords = [symptoms.lower()]
                
                try:
                    mask = df_medical['all_symptoms'].str.lower().apply(lambda x: any(k in str(x) for k in keywords))
                    match_df = df_medical[mask]
                    
                    if not match_df.empty:
                        # Top 3 Matches
                        for _, row in match_df.head(3).iterrows():
                            # Gestion safe des colonnes
                            desc = row.get('description', 'N/A')
                            prec = row.get('precautions', 'N/A')
                            matches_found.append(f"• **{row['disease']}** : {desc}")
                            
                            kaggle_context += (
                                f"- Maladie: {row['disease']}\n"
                                f"  Symptômes: {row.get('all_symptoms', '')}\n"
                                f"  Précautions: {prec}\n"
                                f"  Description: {desc}\n"
                            )
                        kaggle_context = f"SOURCES MÉDICALES (RAG V7):\n{kaggle_context}"
                    else:
                        kaggle_context = "Aucune correspondance exacte dans la base de connaissances (Analyse LLM pure)."
                except Exception as e:
                    kaggle_context = f"Erreur RAG: {str(e)}"

            # --- AI GENERATION ---
            current_task = "triage_urgency" if "Urgence" in mode else "second_opinion"
            task_config = agent.config['tasks'].get(current_task, agent.config['tasks']['triage_urgency']) 
            
            prompt = task_config['user_template'].format(
                first_name="Patient", last_name="", age=age, gender=gender,
                symptoms=symptoms, nlp_matches_str=kaggle_context, nlp_matches_json="{}"
            )
            
            with st.spinner("🤖 Le Dr. IA analyse le cas..."):
                try:
                    model = genai.GenerativeModel(
                        metadata.get('default_model', 'gemini-2.0-flash'),
                        system_instruction=task_config['system_prompt']
                    )
                    response = model.generate_content(prompt)
                    ai_text = response.text.replace("```json", "").replace("```", "").strip()
                except Exception as e:
                    st.error(f"Erreur IA: {e}")
                    st.stop()

            # --- DISPLAY V7 (TABS & CARDS) ---
            st.subheader("💡 Résultats de l'Analyse")
            
            # Parsing JSON si c'est le mode Triage
            data = {}
            is_json = False
            if current_task == "triage_urgency":
                try:
                    data = json.loads(ai_text)
                    is_json = True
                except:
                    pass

            if is_json:
                # 1. STATUS BADGE
                urgency = data.get('urgency_level', 'Unknown')
                color_map = {"Green": "success", "Orange": "warning", "Red": "error"}
                alert_type = "info"
                for k, v in color_map.items():
                    if k in urgency: alert_type = v
                
                if alert_type == "success": st.success(f"### {urgency}")
                elif alert_type == "warning": st.warning(f"### {urgency}")
                else: st.error(f"### {urgency}")

                # 2. TABS RESULTS
                tab1, tab2, tab3 = st.tabs(["🩺 Diagnostic & Analyse", "💊 Actions & Soins", "📚 Preuves (RAG)"])
                
                with tab1:
                    st.markdown("#### Analyse Clinique")
                    st.info(data.get('analysis', 'Aucune analyse.'))
                    st.markdown(f"**Raisonnement :**\n{data.get('reasoning', '')}")
                
                with tab2:
                    st.markdown("#### Recommandations")
                    st.write(data.get('recommendation', 'Aucune reco.'))
                
                with tab3:
                    if matches_found:
                        st.success("✅ **Données vérifiées trouvées dans la Base Kaggle**")
                        for m in matches_found:
                            st.markdown(m)
                    else:
                        st.warning("⚠️ Aucune donnée similaire trouvée dans la base RAG (Analyse générative pure).")
                        
            else:
                # Mode Texte (Second Opinion)
                st.chat_message("assistant", avatar="🧑‍⚕️").markdown(ai_text)
                if matches_found:
                    with st.expander("📚 Sources & Contexte (RAG)"):
                        st.write(kaggle_context)
            
        elif not submitted:
            # Empty State (Premium Placeholder)
            st.info("👈 Remplissez le formulaire à gauche pour commencer.")
            st.markdown(
                """
                <div style="text-align: center; color: #64748b; padding: 2rem;">
                    <h3 style="color: #cbd5e1;">En attente de données patient...</h3>
                    <p>Le système analysera les symptômes en croisant 4 bases de données médicales.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
