# ==============================================================================
# DOCTIS-AI-MO: DATA LOADER (ETL KAGGLE)
# Version: v16.8-Optimized
# Auteurs: Adam Beloucif & Amina Medjdoub
# ==============================================================================

import os
import pandas as pd
import numpy as np
import streamlit as st
from typing import Tuple, Optional, Any

# Constants
DATA_DIR = "data/"
OPTIMIZED_DB_PATH = os.path.join(DATA_DIR, "medical_knowledge_base.csv")

FILENAMES = {
    "symptoms": "dataset.csv",
    "description": "symptom_Description.csv",
    "precaution": "symptom_precaution.csv",
    "severity": "Symptom-severity.csv",
    "s2d_extra": "Symptom2Disease.csv",
    "das_extra": "DiseaseAndSymptoms.csv"
}

def _safe_read(fname: str) -> pd.DataFrame:
    """Helper pour lire un CSV sans crasher."""
    p = os.path.join(DATA_DIR, fname)
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise les noms de colonnes."""
    if not df.empty:
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

def _build_master_symptoms(df_symp: pd.DataFrame) -> pd.DataFrame:
    """Construit le DataFrame maître des symptômes."""
    if df_symp.empty:
        return pd.DataFrame(columns=['disease', 'all_symptoms'])
        
    df_symp['all_symptoms'] = df_symp.apply(
        lambda x: ', '.join([str(s).strip() for s in x.values[1:] if str(s) != 'nan']), axis=1
    )
    return df_symp[['disease', 'all_symptoms']].copy()

def _merge_extra_symptoms(df_master: pd.DataFrame, df_s2d: pd.DataFrame) -> pd.DataFrame:
    """Fusionne les symptômes du dataset additionnel."""
    if df_s2d.empty:
        return df_master

    # Prepare extra dataset
    df_s2d = df_s2d.rename(columns={'label': 'disease', 'text': 'symptoms_extra'})
    df_grouped = df_s2d.groupby('disease')['symptoms_extra'].apply(lambda x: ', '.join(x)).reset_index()
    
    # Merge
    df_merged = pd.merge(df_master, df_grouped, on='disease', how='outer')
    
    # Combine columns
    df_merged['all_symptoms'] = df_merged['all_symptoms'].fillna('') + ", " + df_merged['symptoms_extra'].fillna('')
    df_merged.drop(columns=['symptoms_extra'], inplace=True)
    
    return df_merged

def _enrich_metadata(df_master: pd.DataFrame, df_desc: pd.DataFrame, df_prec: pd.DataFrame) -> pd.DataFrame:
    """Ajoute description et précautions."""
    if df_master.empty:
        return df_master
        
    df_master['disease'] = df_master['disease'].astype(str).str.strip()
    
    # Merge Description
    if not df_desc.empty:
        df_desc['disease'] = df_desc['disease'].astype(str).str.strip()
        df_master = pd.merge(df_master, df_desc, on='disease', how='left')
        
    # Merge Precautions
    if not df_prec.empty:
        df_prec['disease'] = df_prec['disease'].astype(str).str.strip()
        df_prec['precautions'] = df_prec.apply(
            lambda x: ', '.join([str(p).strip().title() for p in x if str(p) != 'nan' and p != x['disease']]), 
            axis=1
        )
        if 'precautions' in df_prec.columns:
            df_master = pd.merge(df_master, df_prec[['disease', 'precautions']], on='disease', how='left')
            
    return df_master

def process_and_optimize_data() -> Tuple[bool, str]:
    """
    Pipeline ETL (Extract, Transform, Load) Principal :
    1. EXTRACT : Lecture des fichiers CSV bruts sources (Locaux).
    2. TRANSFORM : Nettoyage, normalisation et fusion des données (Join).
    3. LOAD : Sauvegarde d'un fichier CSV unique optimisé pour le RAG.
    """
    try:
        print("⚙️ Démarrage de l'optimisation ETL (V13.0 - Local)...")
        
        # 1. LOAD
        df_symp = _safe_read(FILENAMES["symptoms"])
        df_desc = _safe_read(FILENAMES["description"])
        df_prec = _safe_read(FILENAMES["precaution"])
        df_extra_s2d = _safe_read(FILENAMES["s2d_extra"])
        
        if df_symp.empty and df_extra_s2d.empty:
             return False, "Aucun fichier de données trouvé dans data/."

        # 2. CLEAN
        df_symp = _clean_columns(df_symp)
        df_desc = _clean_columns(df_desc)
        df_prec = _clean_columns(df_prec)
        df_extra_s2d = _clean_columns(df_extra_s2d)

        # 3. CONSTRUCT
        df_master = _build_master_symptoms(df_symp)
        df_master = _merge_extra_symptoms(df_master, df_extra_s2d)
        df_master = _enrich_metadata(df_master, df_desc, df_prec)
        
        # 4. FINALIZE
        df_master.fillna("Non spécifié", inplace=True)
        df_master['all_symptoms'] = df_master['all_symptoms'].str.strip(', ')
        
        # 5. SAVE
        df_master.to_csv(OPTIMIZED_DB_PATH, index=False)
        print(f"✅ BDD Optimisée générée (V13.0) : {len(df_master)} entrées.")
        return True, "Base V13 complétée."
        
    except Exception as e:
        print(f"❌ Erreur ETL : {e}")
        return False, str(e)

def load_knowledge_base() -> Optional[pd.DataFrame]:
    """
    Interface principale pour le chargement des données.
    Charge la base optimisée ou tente de la reconstruire depuis les CSV locaux.
    """
    # 1. Try Load Existing DB
    if os.path.exists(OPTIMIZED_DB_PATH):
        try:
            return pd.read_csv(OPTIMIZED_DB_PATH)
        except Exception:
            pass 
            
    # 2. Run ETL (Local Files Only)
    ok, etl_msg = process_and_optimize_data()
    if ok:
        return pd.read_csv(OPTIMIZED_DB_PATH)
    else:
        st.warning(f"⚠️ Base de connaissances indisponible : {etl_msg}. L'appli fonctionnera en mode IA seule.")
        return None
