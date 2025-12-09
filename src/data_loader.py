# ==============================================================================
# DOCTIS-AI-MO: DATA LOADER (ETL KAGGLE)
# Version: 5.0-RAG
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
    ETL: Fusionne les CSVs bruts en une BDD optimisée.
    Crée 'medical_knowledge_base.csv'.
    """
    try:
        print("⚙️ Démarrage de l'optimisation ETL...")
        
        # 1. LOAD raw files
        df_symp = pd.read_csv(os.path.join(DATA_DIR, "dataset.csv"))
        df_desc = pd.read_csv(os.path.join(DATA_DIR, "symptom_Description.csv"))
        df_prec = pd.read_csv(os.path.join(DATA_DIR, "symptom_precaution.csv"))
        df_sev = pd.read_csv(os.path.join(DATA_DIR, "Symptom-severity.csv"))
        
        # 2. CLEAN & NORMALIZE
        # Nettoyage des noms de colonnes et espaces
        for df in [df_symp, df_desc, df_prec, df_sev]:
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            
        # 3. TRANSFORM (Melt des symptômes)
        # dataset.csv est "Wide" (Symptom_1, Symptom_2...), on le passe en "Long" pour avoir une liste
        df_symp['all_symptoms'] = df_symp.apply(
            lambda x: ', '.join([str(s).strip() for s in x.values[1:] if str(s) != 'nan']), axis=1
        )
        # On ne garde que Disease et la liste agrégée
        df_master = df_symp[['disease', 'all_symptoms']].copy()
        
        # 4. MERGE (Description)
        # Attention aux noms de maladie qui peuvent différer par des espaces
        df_master['disease'] = df_master['disease'].str.strip()
        df_desc['disease'] = df_desc['disease'].str.strip()
        
        df_master = pd.merge(df_master, df_desc, on='disease', how='left')
        
        # 5. MERGE (Precautions)
        df_prec['disease'] = df_prec['disease'].str.strip()
        # Concaténer les 4 précautions en une phrase
        df_prec['precautions'] = df_prec.apply(
            lambda x: ', '.join([str(p).strip().title() for p in x[['precaution_1', 'precaution_2', 'precaution_3', 'precaution_4']] if str(p) != 'nan']), 
            axis=1
        )
        df_master = pd.merge(df_master, df_prec[['disease', 'precautions']], on='disease', how='left')
        
        # 6. ENRICH (Severity Score - Experimental)
        # On pourrait calculer un score moyen basé sur les symptômes présents
        # Pour l'instant on garde ça simple.
        
        # 7. SAVE
        df_master.fillna("Information non disponible", inplace=True)
        df_master.to_csv(OPTIMIZED_DB_PATH, index=False)
        print(f"✅ BDD Optimisée générée : {OPTIMIZED_DB_PATH} ({len(df_master)} maladies)")
        return True, "Base de connaissances optimisée."
        
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
