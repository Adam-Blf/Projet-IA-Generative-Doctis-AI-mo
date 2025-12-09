# ==============================================================================
# DOCTIS-AI-MO: AGENT INTELLIGENT (BACKEND LOGIC)
# Version: v15.1-Optimized
# Auteurs: Adam Beloucif & Amina Medjdoub
# ==============================================================================

"""
Ce module définit la classe `DoctisAgent`, le cerveau de l'application.

Responsabilités :
1. Charger la configuration dynamique depuis `config/prompts.json`.
2. Fournir une interface simple pour récupérer les "System Prompts".
3. Abstraire la complexité de la gestion des fichiers de configuration.
"""

import json
import os
from typing import Optional, Dict, Any

class DoctisAgent:
    """
    Classe principale représentant l'agent IA médical.
    Elle charge les instructions de tâches (Prompts) au démarrage.
    """
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialise l'agent.
        
        Args:
            config_path (Optional[str]): Chemin vers le fichier JSON de config.
                                         Si None, cherche automatiquement '../config/prompts.json'.
        """
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, '..', 'config', 'prompts.json')
        
        self.config: Dict[str, Any] = self._load_config(config_path)

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Méthode interne pour lire le fichier JSON de configuration."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ Configuration introuvable à : {path}")
        except json.JSONDecodeError:
            raise ValueError(f"❌ JSON invalide dans le fichier : {path}")

    def get_system_prompt(self, task_name: str) -> Optional[str]:
        """
        Récupère l'instruction système (System Prompt) pour une tâche donnée.
        
        Args:
            task_name (str): Le nom de la tâche (ex: 'triage_urgency').
            
        Returns:
            Optional[str]: Le prompt textuel ou None si la tâche n'existe pas.
        """
        tasks = self.config.get('tasks', {})
        task = tasks.get(task_name)
        if not task:
            return None
        return task.get('system_prompt')

    def get_agent_metadata(self) -> Dict[str, Any]:
        """Renvoie les métadonnées de l'agent (Nom, Version, Modèle)."""
        return self.config.get('agent_metadata', {})

if __name__ == "__main__":
    # Test Block
    try:
        print("🔍 Test de chargement de l'agent...")
        agent = DoctisAgent()
        metadata = agent.get_agent_metadata()
        print(f"✅ Agent Chargé : {metadata.get('name')} v{metadata.get('version')}")
        
        triage_prompt = agent.get_system_prompt('triage_urgency')
        if triage_prompt:
            print(f"✅ Tâche 'Triage' trouvée ({len(triage_prompt)} caractères).")
        else:
            print("❌ Tâche 'Triage' MANQUANTE !")

    except Exception as e:
        print(f"❌ Erreur critique lors du test : {e}")
