# ==============================================================================
# DOCTIS-AI-MO: DATA LOADER (ETL KAGGLE)
# Version: 12.0-RAG
# Auteurs: Adam Beloucif & Amina Medjdoub
# ==============================================================================

import os
import json
import pandas as pd
import numpy as np
import streamlit as st
from kaggle.api.kaggle_api_extended import KaggleApi
from dotenv import load_dotenv

# Charge les variables d'environnement locales (.env)
load_dotenv()

DATASET_SLUG = "itachi9604/disease-symptom-description-dataset"
DATA_DIR = "data/"
OPTIMIZED_DB_PATH = os.path.join(DATA_DIR, "medical_knowledge_base.csv")

def authenticate_kaggle():
    """Authentification robuste (Secrets > .env > JSON Token)."""
    try:
        # 1. Secrets / Env Vars
        os.environ['KAGGLE_USERNAME'] = st.secrets.get("KAGGLE_USERNAME", os.environ.get("KAGGLE_USERNAME", ""))
        os.environ['KAGGLE_KEY'] = st.secrets.get("KAGGLE_KEY", os.environ.get("KAGGLE_KEY", ""))
        
        # 2. Token Fallback
        token_str = os.environ.get("KAGGLE_API_TOKEN")
        if token_str and not os.environ['KAGGLE_USERNAME']:
            try:
                creds = json.loads(token_str)
                os.environ['KAGGLE_USERNAME'] = creds.get('username', '')
                os.environ['KAGGLE_KEY'] = creds.get('key', '')
            except:
                pass
                
        if not os.environ['KAGGLE_USERNAME'] or not os.environ['KAGGLE_KEY']:
            return False, "Identifiants manquants."
            
        api = KaggleApi()
        api.authenticate()
        return True, api
    except Exception as e:
        return False, str(e)

def download_medical_dataset():
    """Télécharge les fichiers bruts si nécessaire."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    # On vérifie si les fichiers bruts sont là (dataset.csv est le principal)
    raw_files = ["dataset.csv", "symptom_Description.csv", "symptom_precaution.csv", "Symptom-severity.csv"]
    missing = [f for f in raw_files if not os.path.exists(os.path.join(DATA_DIR, f))]
    
    if not missing:
        return True, "Fichiers bruts déjà présents."
        
    success, result = authenticate_kaggle()
    if not success:
        return False, f"Erreur Auth: {result}"
        
    try:
        api = result
        print("⬇️ Téléchargement des données Kaggle...")
        api.dataset_download_files(DATASET_SLUG, path=DATA_DIR, unzip=True)
        return True, "Données téléchargées."
    except Exception as e:
        return False, f"Erreur Download: {e}"

def process_and_optimize_data():
    """
    ETL: Fusionne les CSVs bruts (Kaggle + Extra) en une BDD optimisée.
    Crée 'medical_knowledge_base.csv'.
    """
    try:
        print("⚙️ Démarrage de l'optimisation ETL (V7)...")
        
        # 1. LOAD raw files (Main Kaggle Set)
        # On utilise safe read pour éviter les crashs si un fichier manque
        def safe_read(fname):
            p = os.path.join(DATA_DIR, fname)
            return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()
            
        df_symp = safe_read("dataset.csv")
        df_desc = safe_read("symptom_Description.csv")
        df_prec = safe_read("symptom_precaution.csv")
        
        # New Datasets (User provided)
        df_extra_s2d = safe_read("Symptom2Disease.csv") #Cols: label, text
        df_extra_das = safe_read("DiseaseAndSymptoms.csv")
        
        # 2. CLEAN & NORMALIZE
        dfs = [df_symp, df_desc, df_prec, df_extra_s2d, df_extra_das]
        for df in dfs:
            if not df.empty:
                df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # 3. MASTER DATAFRAME CONSTRUCTION
        # Base: dataset.csv (Disease -> Symptoms_list)
        if not df_symp.empty:
            df_symp['all_symptoms'] = df_symp.apply(
                lambda x: ', '.join([str(s).strip() for s in x.values[1:] if str(s) != 'nan']), axis=1
            )
            df_master = df_symp[['disease', 'all_symptoms']].copy()
        else:
            df_master = pd.DataFrame(columns=['disease', 'all_symptoms'])

        # Merge Extra: Symptom2Disease (label=disease, text=symptom_description)
        if not df_extra_s2d.empty:
            # On considère 'text' comme des symptômes additionnels
            # Renaming columns to match master
            df_extra_s2d = df_extra_s2d.rename(columns={'label': 'disease', 'text': 'symptoms_extra'})
            # On agrège par maladie car il y a plusieurs lignes par maladie
            df_grouped = df_extra_s2d.groupby('disease')['symptoms_extra'].apply(lambda x: ', '.join(x)).reset_index()
            
            # Merge with master
            df_master = pd.merge(df_master, df_grouped, on='disease', how='outer')
            # Combine symptoms
            df_master['all_symptoms'] = df_master['all_symptoms'].fillna('') + ", " + df_master['symptoms_extra'].fillna('')
            df_master.drop(columns=['symptoms_extra'], inplace=True)

        # 4. MERGE METADATA (Description & Precautions)
        if not df_master.empty:
            df_master['disease'] = df_master['disease'].astype(str).str.strip()
            
            if not df_desc.empty:
                df_desc['disease'] = df_desc['disease'].astype(str).str.strip()
                df_master = pd.merge(df_master, df_desc, on='disease', how='left')
                
            if not df_prec.empty:
                df_prec['disease'] = df_prec['disease'].astype(str).str.strip()
                df_prec['precautions'] = df_prec.apply(
                    lambda x: ', '.join([str(p).strip().title() for p in x if str(p) != 'nan' and p != x['disease']]), 
                    axis=1
                )
                if 'precautions' in df_prec.columns:
                    df_master = pd.merge(df_master, df_prec[['disease', 'precautions']], on='disease', how='left')

        # 7. SAVE
        df_master.fillna("Non spécifié", inplace=True)
        # Clean up commas
        df_master['all_symptoms'] = df_master['all_symptoms'].str.strip(', ')
        
        df_master.to_csv(OPTIMIZED_DB_PATH, index=False)
        print(f"✅ BDD Optimisée générée (V7) : {len(df_master)} entrées.")
        return True, "Base V7 complétée."
        
    except Exception as e:
        print(f"❌ Erreur ETL : {e}")
        return False, str(e)

def load_knowledge_base():
    """
    Charge la BDD optimisée. Si elle n'existe pas, lance le processus complet.
    """
    # 1. Check optimized file
    if os.path.exists(OPTIMIZED_DB_PATH):
        try:
            return pd.read_csv(OPTIMIZED_DB_PATH)
        except:
            pass # Fichier corrompu, on recrée
            
    # 2. Check & Download Raw
    success, msg = download_medical_dataset()
    if not success:
        st.error(f"Erreur d'initialisation des données : {msg}")
        return None
        
    # 3. Run ETL
    ok, etl_msg = process_and_optimize_data()
    if ok:
        return pd.read_csv(OPTIMIZED_DB_PATH)
    else:
        st.error(f"Echec de l'optimisation BDD : {etl_msg}")
        return None
