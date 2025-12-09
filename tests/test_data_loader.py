
import os
import sys
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_loader import _clean_columns, _build_master_symptoms, _merge_extra_symptoms

def test_clean_columns():
    """Vérifie le nettoyage des colonnes."""
    df = pd.DataFrame({'Disease Name ': [1], ' Symptom Extra': [2]})
    df_clean = _clean_columns(df)
    assert 'disease_name' in df_clean.columns
    assert 'symptom_extra' in df_clean.columns

def test_build_master_symptoms():
    """Vérifie l'agrégation des symptômes (format horizontal vers string)."""
    data = {
        'disease': ['Flu'],
        'symptom_1': ['fever'],
        'symptom_2': ['cough'],
        'symptom_3': [float('nan')]
    }
    df = pd.DataFrame(data)
    result = _build_master_symptoms(df)
    
    assert 'all_symptoms' in result.columns
    # La concaténation doit être correcte
    assert result.iloc[0]['all_symptoms'] == "fever, cough"

def test_merge_extra_symptoms():
    """Vérifie la fusion de Symptom2Disease."""
    # Master Mock
    df_master = pd.DataFrame({
        'disease': ['Covid'],
        'all_symptoms': ['fever']
    })
    
    # Extra Mock
    df_extra = pd.DataFrame({
        'label': ['Covid', 'Covid'],
        'text': ['loss of smell', 'fatigue']
    })
    
    result = _merge_extra_symptoms(df_master, df_extra)
    
    # Doit avoir fusionné les symptômes
    symptoms = result.iloc[0]['all_symptoms']
    assert 'fever' in symptoms
    assert 'loss of smell' in symptoms
    assert 'fatigue' in symptoms
