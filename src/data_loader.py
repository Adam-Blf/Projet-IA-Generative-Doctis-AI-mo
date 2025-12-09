# ==============================================================================
# DOCTIS-AI-MO: DATA LOADER (ETL KAGGLE)
# Version: 5.0-RAG
# Auteurs: Adam Beloucif & Amina Medjdoub
# ==============================================================================

import os
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
import streamlit as st

def download_medical_dataset():
    """
    Télécharge un dataset médical depuis Kaggle s'il n'existe pas déjà.
    
    Dataset cible : 'itachi9604/disease-symptom-description-dataset'
    Ce dataset contient des liens entre maladies, symptômes et précautions.
    
    Returns:
        tuple: (bool success, str message)
    """
    # -----------------------------------------------------------
    # 1. AUTHENTIFICATION SÉCURISÉE
    # -----------------------------------------------------------
    # On essaie de récupérer les identifiants depuis les secrets Streamlit (Cloud)
    # ou les variables d'environnement (Local via .env).
    try:
        os.environ['KAGGLE_USERNAME'] = st.secrets.get("KAGGLE_USERNAME", os.environ.get("KAGGLE_USERNAME"))
        os.environ['KAGGLE_KEY'] = st.secrets.get("KAGGLE_KEY", os.environ.get("KAGGLE_KEY"))
    except Exception:
        # En local sans st.secrets, os.environ est déjà géré par python-dotenv si chargé
        pass

    # Vérification que les clés sont bien présentes pour éviter un crash
    if not os.environ.get('KAGGLE_USERNAME') or not os.environ.get('KAGGLE_KEY'):
        return False, "Identifiants Kaggle manquants (KAGGLE_USERNAME/KEY)."

    # Instanciation de l'API Kaggle
    api = KaggleApi()
    
    try:
        api.authenticate()
    except Exception as e:
        return False, f"Erreur d'authentification Kaggle : {str(e)}"

    # -----------------------------------------------------------
    # 2. TÉLÉCHARGEMENT DU DATASET
    # -----------------------------------------------------------
    dataset_path = "data/"
    # Création du dossier data/ s'il n'existe pas
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    # Identifiant unique du dataset sur Kaggle (Owner/Name)
    dataset_slug = "itachi9604/disease-symptom-description-dataset"
    
    # On vérifie si le fichier principal existe déjà pour gagner du temps
    target_file = os.path.join(dataset_path, "dataset.csv")
    
    # N.B.: Le dataset téléchargé peut contenir plusieurs fichiers. 
    # Ici, nous supposons que le téléchargement est nécessaire si le dossier est vide ou le fichier absent.
    if not os.path.exists(target_file):
        try:
            # Téléchargement et décompression automatique
            api.dataset_download_files(dataset_slug, path=dataset_path, unzip=True)
            return True, "✅ Dataset médical Kaggle téléchargé avec succès."
        except Exception as e:
            return False, f"❌ Erreur lors du téléchargement Kaggle : {str(e)}"
    
    return True, "⚡ Dataset déjà présent en cache local."

def load_symptom_data():
    """
    Charge les données brutes dans un DataFrame Pandas pour analyse.
    
    Returns:
        pd.DataFrame or None: Le tableau de données ou None si erreur.
    """
    try:
        # On tente de charger le fichier CSV principal
        # Note: Le nom du fichier dépend du contenu du zip Kaggle. 
        # Pour ce dataset spécifique, le fichier principal est souvent 'dataset.csv' ou 'Symptom-severity.csv'
        # Nous allons essayer de trouver un csv pertinent.
        
        # Pour l'exemple, nous chargeons 'dataset.csv' s'il existe
        file_path = "data/dataset.csv"
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            return df
        else:
            return None
            
    except Exception as e:
        print(f"Erreur de lecture CSV: {e}")
        return None
