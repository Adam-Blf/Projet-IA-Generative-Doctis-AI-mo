# ==============================================================================
# DOCTIS-AI-MO: APPLICATION PRINCIPALE (STREAMLIT DASHBOARD)
# Version: v16.7-Optimized (Premium UI)
# Auteurs: Adam Beloucif & Amina Medjdoub
# ==============================================================================

import streamlit as st  # Framework pour créer l'interface web
import google.generativeai as genai  # Client pour l'IA Gemini
import json  # Pour gérer les réponses formatées en JSON
import os  # Pour accéder aux variables système (clés API)
import pandas as pd  # Pour manipuler les tableaux de données (Excel-like)
from typing import Optional, Dict, Any, List
from src.agent import DoctisAgent
from src.data_loader import load_knowledge_base
from src.monitoring import init_monitor

# ==============================================================================
# 0. CONFIGURATION & STYLES
# ==============================================================================
# Cette section gère l'apparence visuelle de l'application (Couleurs, Polices, etc.)

def _inject_custom_css() -> None:
    """Injecte le CSS personnalisé pour l'interface Premium."""
    st.markdown("""
    <style>
        /* --- DARK MODE THEME --- */
        
        /* Main Background & Fonts */
        .stApp {
            background-color: #0e1117; /* Streamlit Dark BG */
            font-family: 'Inter', sans-serif;
            color: #fafafa;
        }
        
        /* Custom Header */
        h1 {
            color: #f8fafc; /* Slate-50 */
            font-weight: 800;
            font-size: 2.2rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        h2, h3 {
            color: #e2e8f0; /* Slate-200 */
            font-weight: 700;
        }
        
        /* Card-like containers for Input and Results */
        div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
            background-color: #1e293b; /* Slate-800 */
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            border: 1px solid #334155; /* Slate-700 */
        }

        /* Inputs (Text Area, Number Input) */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #0f172a !important; /* Slate-900 */
            color: white !important;
            border: 1px solid #475569 !important;
        }
        
        /* Metrics values */
        div[data-testid="stMetricValue"] {
            color: #38bdf8 !important; /* Sky-400 */
        }
        
        /* Primary Button Style */
        div.stButton > button {
            background-color: #3b82f6; /* Blue-500 */
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.2s;
            width: auto;
        }
        div.stButton > button:hover {
            background-color: #2563eb; /* Blue-600 */
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            transform: translateY(-1px);
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #171923; /* Darker Sidebar */
            border-right: 1px solid #2d3748;
        }
        
        /* Sidebar Text */
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p {
            color: #e2e8f0 !important;
        }

        /* --- RESPONSIVE DESIGN --- */
        @media (max-width: 768px) {
            .stApp {
                background-color: #0e1117;
            }
            h1 { font-size: 1.8rem !important; }
            h2 { font-size: 1.5rem !important; }
            
            div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
                padding: 1rem !important;
                background-color: #1a202c; /* Slightly Lighter Mobile Card */
                border: none;
            }
            
            div.stButton > button {
                width: 100% !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(
    page_title="DoctisAImo V13 - Intelligent Triage",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

_inject_custom_css()
init_monitor()

# ------------------------------------------------------------------------------
# 1. LOGIC HELPERS
# ------------------------------------------------------------------------------
def configure_gemini() -> None:
    """
    Connecte l'application à l'intelligence artificielle de Google (Gemini).
    C'est comme donner la clé de la maison pour entrer.
    """
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
             try:
                 api_key = st.secrets.get("GOOGLE_API_KEY")
             except:
                 pass
    except:
        api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        st.error("❌ CLÉ API MANQUANTE (GOOGLE_API_KEY).")
        st.stop()
    
    genai.configure(api_key=api_key)

@st.cache_resource
def load_agent() -> DoctisAgent:
    return DoctisAgent()

@st.cache_data
def get_kaggle_data() -> Optional[pd.DataFrame]:
    with st.spinner("🔄 Chargement de la Base de Connaissances V13..."):
        return load_knowledge_base()

# Init Resources
# On charge les outils nécessaires au démarrage de l'application
configure_gemini()  # Connexion à l'IA
agent = load_agent()  # Chargement du cerveau de l'agent
df_medical = get_kaggle_data()  # Chargement de la base de données médicale
metadata = agent.get_agent_metadata()  # Infos sur l'agent (Nom, Version)

# ------------------------------------------------------------------------------
# 2. SIDEBAR NAVIGATION
# ------------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/doctor-male.png", width=80)
    st.title("DoctisAImo")
    st.caption(f"v13.0 • RAG-Enhanced")
    
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
    
    **DoctisAImo V13 (Optimized)** repousse les limites de l'assistance médicale par IA en combinant :
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
            # --- ÉTAPE 1 : RECHERCHE DE PREUVES (RAG) ---
            # On cherche d'abord dans nos livres (CSV) avant de demander à l'IA.
            kaggle_context = ""
            matches_found: List[str] = []
            
            if df_medical is not None:
                # Recherche Optimisée (sur 'all_symptoms')
                keywords = [w.lower() for w in symptoms.split() if len(w) > 3]
                if not keywords: keywords = [symptoms.lower()]
                
                try:
                    # Type checking safe
                    mask = df_medical['all_symptoms'].astype(str).str.lower().apply(lambda x: any(k in x for k in keywords))
                    match_df = df_medical[mask]
                    
                    if not match_df.empty:
                        # Top 3 Matches
                        for _, row in match_df.head(3).iterrows():
                            desc = row.get('description', 'N/A')
                            prec = row.get('precautions', 'N/A')
                            matches_found.append(f"• **{row['disease']}** : {desc}")
                            
                            kaggle_context += (
                                f"- Maladie: {row['disease']}\n"
                                f"  Symptômes: {row.get('all_symptoms', '')}\n"
                                f"  Précautions: {prec}\n"
                                f"  Description: {desc}\n"
                            )
                        kaggle_context = f"SOURCES MÉDICALES (RAG V13):\n{kaggle_context}"
                    else:
                        kaggle_context = "Aucune correspondance exacte dans la base de connaissances (Analyse LLM pure)."
                except Exception as e:
                    kaggle_context = f"Erreur RAG: {str(e)}"

            # --- AI GENERATION WITH FALLBACK ---
            current_task = "triage_urgency" if "Urgence" in mode else "second_opinion"
            task_config = agent.config['tasks'].get(current_task, agent.config['tasks']['triage_urgency']) 
            
            prompt = task_config['user_template'].format(
                first_name="Patient", last_name="", age=age, gender=gender,
                symptoms=symptoms, nlp_matches_str=kaggle_context, nlp_matches_json="{}"
            )
            
            ai_text = ""
            provider_used = "Gemini"
            
            with st.spinner("🤖 Le Dr. IA analyse le cas (Tentative Gemini)..."):
                try:
                    # 1. On essaie d'abord avec Gemini (Google)
                    model = genai.GenerativeModel(
                        metadata.get('default_model', 'gemini-2.0-flash'),
                        system_instruction=task_config['system_prompt']
                    )
                    response = model.generate_content(prompt)
                    ai_text = response.text
                except Exception as e_gemini:
                    # 2. Si Gemini échoue (panne, quota...), on bascule sur OpenAI (Plan B)
                    print(f"⚠️ Gemini Error: {e_gemini}. Switching to OpenAI...")
                    openai_key = os.environ.get("OPENAI_API_KEY") 
                    if not openai_key:
                        try: openai_key = st.secrets["OPENAI_API_KEY"]
                        except: pass
                        
                    if openai_key:
                        try:
                            import openai
                            client = openai.OpenAI(api_key=openai_key)
                            with st.spinner("⚠️ Gemini indisponible. Relais OpenAI (GPT-4o) activé..."):
                                completion = client.chat.completions.create(
                                    model="gpt-4o",
                                    messages=[
                                        {"role": "system", "content": task_config['system_prompt']},
                                        {"role": "user", "content": prompt}
                                    ]
                                )
                                ai_text = completion.choices[0].message.content
                                provider_used = "OpenAI (GPT-4o)"
                        except Exception as e_openai:
                            st.error(f"❌ Erreur critique (Gemini & OpenAI) : {e_openai}")
                            st.stop()
                    else:
                        st.error(f"❌ Erreur Gemini : {e_gemini}. (Ajoutez OPENAI_API_KEY pour le fallback).")
                        st.stop()

            ai_text = ai_text.replace("```json", "").replace("```", "").strip()
            
            if provider_used != "Gemini":
                st.toast(f"⚠️ Fallback activé : Réponse générée par {provider_used}", icon="🛟")

            # --- DISPLAY (TABS & CARDS) ---
            st.subheader("💡 Résultats de l'Analyse")
            
            # Parsing JSON si c'est le mode Triage
            data: Dict[str, Any] = {}
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
            # Empty State
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
