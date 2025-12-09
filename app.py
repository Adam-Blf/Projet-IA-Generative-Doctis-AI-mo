import streamlit as st
import google.generativeai as genai
import json
import os
from src.agent import DoctisAgent

# Page Configuration
st.set_page_config(
    page_title="DoctisAImo - Triage Urgences",
    page_icon="🏥",
    layout="centered"
)

# 1. Setup API interaction
def configure_gemini():
    # Try getting key from Streamlit secrets, then environment variable
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except (FileNotFoundError, KeyError):
        api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        st.error("❌ API Key missing. Please set GOOGLE_API_KEY in .streamlit/secrets.toml or as an environment variable.")
        st.stop()

    genai.configure(api_key=api_key)

configure_gemini()

# 2. Load Agent
@st.cache_resource
def load_agent():
    return DoctisAgent()

agent = load_agent()
metadata = agent.get_agent_metadata()

# 3. UI Layout
st.title(f"🏥 {metadata.get('name')} (v{metadata.get('version')})")
st.markdown("""
> **Assistant de Triage IA Avancé | Advanced AI Triage Assistant**
> 
> *Entraîné sur des logiques de datasets médicaux pour évaluer l'urgence.*
""")

with st.form("triage_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Âge / Age", min_value=0, max_value=120, value=30)
    with col2:
        gender = st.selectbox("Genre / Gender", ["Male", "Female", "Other"])
    
    symptoms = st.text_area("Symptômes / Symptoms", placeholder="Describe symptoms here... / Décrivez les symptômes ici...")
    
    submitted = st.form_submit_button("🚑 Analyser / Analyze")

# 4. Analysis Logic
if submitted and symptoms:
    with st.spinner("Analyse en cours... / Analyzing..."):
        try:
            # Get Triage Prompt
            task_config = agent.config['tasks']['triage_urgency']
            system_instruction = task_config['system_prompt']
            user_template = task_config['user_template']

            # Use default model from config
            model_name = metadata.get('default_model', 'gemini-2.0-flash')
            model = genai.GenerativeModel(
                model_name,
                system_instruction=system_instruction
            )

            # Format User Prompt
            user_prompt = user_template.format(
                first_name="Patient",
                last_name="",
                age=age,
                gender=gender,
                symptoms=symptoms,
                nlp_matches_str="N/A (Web Input)" 
            )

            # Generate response
            response = model.generate_content(user_prompt)
            
            # Parse JSON
            # Clean possible markdown code blocks
            response_text = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(response_text)

            # Display Results
            urgency = result.get("urgency_level", "Unknown")
            
            if "Green" in urgency:
                st.success(f"### 🟢 {urgency}")
            elif "Orange" in urgency:
                st.warning(f"### 🟠 {urgency}")
            elif "Red" in urgency:
                st.error(f"### 🔴 {urgency} - IMMEDIATE ACTION REQUIRED")
            else:
                st.info(f"### ⚪ {urgency}")

            st.subheader("📝 Analyse / Analysis")
            st.write(result.get("analysis"))

            st.subheader("🛡️ Recommandation / Recommendation")
            st.write(result.get("recommendation"))

            with st.expander("🔍 Raisonnement Statistique / Reasoning"):
                st.write(result.get("reasoning"))

        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")
elif submitted:
    st.warning("Veuillez entrer des symptômes. / Please enter symptoms.")
