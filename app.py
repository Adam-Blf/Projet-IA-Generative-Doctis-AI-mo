import streamlit as st
import google.generativeai as genai
import json
import os
from src.agent import DoctisAgent

# Page Configuration
st.set_page_config(
    page_title="DoctisAImo V4 - Medical Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UTILS ---
def configure_gemini():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except (FileNotFoundError, KeyError):
        api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        st.error("❌ API Key missing. Set GOOGLE_API_KEY in secrets or env.")
        st.stop()
    genai.configure(api_key=api_key)

@st.cache_resource
def load_agent():
    return DoctisAgent()

# --- SETUP ---
configure_gemini()
agent = load_agent()
metadata = agent.get_agent_metadata()

# --- SIDEBAR ---
st.sidebar.title(f"🏥 {metadata.get('name')}")
st.sidebar.caption(f"Version: {metadata.get('version')}")

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

# --- MAIN LOGIC ---

# 1. ABOUT PAGE
if mode == "ℹ️ À propos":
    st.title("ℹ️ À propos de DoctisAImo")
    st.markdown("""
    ### Assistant de Triage Médical Avancé (V4)
    
    **DoctisAImo** est un systéme expert piloté par l'IA générative (Gemini 2.0 Flash).
    
    #### Capacités :
    - **🚑 Triage Urgence** : Analyse statistique des symptômes basée sur des datasets médicaux (Kaggle).
    - **🧠 Seconde Opinion** : Détection des "Red Flags" et signaux faibles.
    - **📋 Plan d'Action** : Génération de checklists d'intervention immédiate.
    
    ---
    *Développé par Adam Beloucif - Projet Open Source*
    """)

# 2. MEDICAL MODES
else:
    # Map selection to config tasks
    task_map = {
        "🚑 Urgence & Triage": "triage_urgency",
        "🧠 Seconde Opinion": "second_opinion",
        "📋 Plan d'Action": "action_plan"
    }
    current_task = task_map[mode]
    
    st.title(mode)
    
    # --- LAYOUT ---
    col_input, col_result = st.columns([1, 1], gap="large")
    
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

    with col_result:
        st.subheader("📊 Résultats & IA / Results & AI")
        
        if analyze_btn and symptoms:
            with st.spinner("🧠 Analyse Data-Driven en cours..."):
                try:
                    # Config & Model
                    task_config = agent.config['tasks'][current_task]
                    system_instruction = task_config['system_prompt']
                    user_template = task_config['user_template']
                    
                    model = genai.GenerativeModel(
                        metadata.get('default_model', 'gemini-2.0-flash'),
                        system_instruction=system_instruction
                    )
                    
                    # Prompt Construction
                    prompt = user_template.format(
                        first_name="Patient", last_name="", 
                        age=age, gender=gender, 
                        symptoms=symptoms, 
                        nlp_matches_str="[Web Input Direct]",
                        nlp_matches_json="{}" # Handle diff templates
                    )
                    
                    # Generation
                    response = model.generate_content(prompt)
                    clean_resp = response.text.replace("```json", "").replace("```", "").strip()
                    
                    # --- DISPLAY LOGIC ---
                    
                    # CASE A: JSON Output (Triage)
                    if current_task == "triage_urgency" or (clean_resp.startswith("{") and clean_resp.endswith("}")):
                        try:
                            data = json.loads(clean_resp)
                            
                            # Urgency Badge
                            urgency = data.get("urgency_level", "Unknown")
                            if "Green" in urgency:
                                st.success(f"### 🟢 {urgency}")
                            elif "Orange" in urgency:
                                st.warning(f"### 🟠 {urgency}")
                            elif "Red" in urgency:
                                st.error(f"### 🔴 {urgency} - ALERTE")
                            else:
                                st.info(f"### {urgency}")
                            
                            # Cards
                            with st.container(border=True):
                                st.markdown("#### 🩺 Analyse Clinique")
                                st.write(data.get("analysis", "No analysis provided."))
                            
                            with st.container(border=True):
                                st.markdown("#### 🛡️ Recommandation")
                                st.write(data.get("recommendation", "No recommendation provided."))
                                
                            with st.expander("📈 Raisonnement Statistique"):
                                st.info(data.get("reasoning", "No reasoning provided."))
                                
                        except json.JSONDecodeError:
                            st.warning("⚠️ L'IA a répondu en texte brut (JSON malformé).")
                            st.write(response.text)
                            
                    # CASE B: Text Output (Second Opinion / Action Plan)
                    else:
                        with st.container(border=True):
                            st.markdown(response.text)
                            
                except Exception as e:
                    st.error(f"Erreur Système : {str(e)}")
                    
        elif analyze_btn:
            st.warning("⚠️ Veuillez décrire les symptômes.")
        else:
            st.info("👈 Remplissez le formulaire pour démarrer l'analyse.")
