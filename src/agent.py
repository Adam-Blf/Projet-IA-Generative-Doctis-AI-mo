# ==============================================================================
# DOCTIS-AI-MO: AGENT INTELLIGENT (BACKEND LOGIC)
# Version: 8.0-RAG
# Auteurs: Adam Beloucif & Amina Medjdoub
# ==============================================================================

"""
Ce module définit la classe `DoctisAgent`, le cerveau de l'application.

Responsabilités :
1. Charger la configuration dynamique depuis `config/prompts.json`.
2. Fournir une interface simple pour récupérer les "System Prompts" (la personnalité de l'IA).
3. Abstraire la complexité de la gestion des fichiers de configuration pour l'application principale.

Pourquoi séparer l'agent ?
- Pour maintenir le code propre (Separation of Concerns).
- Pour pouvoir réutiliser cet agent dans d'autres interfaces (ex: API REST, CLI, Chatbot Discord) sans modifier la logique métier.
"""

import json
import os

class DoctisAgent:
    """
    Classe principale représentant l'agent IA médical.
    Elle charge les instructions de tâches (Prompts) au démarrage.
    """
    
    def __init__(self, config_path=None):
        """
        Initialise l'agent.
        
        Args:
            config_path (str, optional): Chemin vers le fichier JSON de config.
                                         Si None, cherche automatiquement '../config/prompts.json'.
        """
        # Si aucun chemin n'est fourni, on calcule le chemin relatif par défaut
        if config_path is None:
            # __file__ est le chemin de ce script (src/agent.py)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # On remonte d'un dossier (..) pour aller chercher config/prompts.json
            config_path = os.path.join(base_dir, '..', 'config', 'prompts.json')
        
        # Chargement de la configuration en mémoire
        self.config = self._load_config(config_path)

    def _load_config(self, path):
        """
        Méthode interne (privée) pour lire le fichier JSON.
        Gère les erreurs de fichier manquant ou de JSON invalide.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ Configuration introuvable à : {path}")
        except json.JSONDecodeError:
            raise ValueError(f"❌ JSON invalide dans le fichier : {path}")

    def get_system_prompt(self, task_name):
        """
        Récupère l'instruction système (System Prompt) pour une tâche donnée.
        
        Args:
            task_name (str): Le nom de la tâche (ex: 'triage_urgency').
            
        Returns:
            str ou None: Le prompt textuel ou None si la tâche n'existe pas.
        """
        tasks = self.config.get('tasks', {})
        task = tasks.get(task_name)
        if not task:
            return None
        return task.get('system_prompt')

    def get_agent_metadata(self):
        """
        Renvoie les métadonnées de l'agent (Nom, Version, Modèle par défaut).
        Utile pour l'affichage dans l'interface utilisateur.
        """
        return self.config.get('agent_metadata', {})

# ------------------------------------------------------------------------------
# BLOC DE TEST (MAIN)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Ce bloc ne s'exécute que si le script est lancé directement (pour débogage).
    # Il ne s'exécute pas si le fichier est importé par app.py.
    try:
        print("🔍 Test de chargement de l'agent...")
        agent = DoctisAgent()
        metadata = agent.get_agent_metadata()
        print(f"✅ Agent Chargé : {metadata.get('name')} v{metadata.get('version')}")
        
        # Vérification des tâches critiques
        triage_prompt = agent.get_system_prompt('triage_urgency')
        if triage_prompt:
            print(f"✅ Tâche 'Triage' trouvée ({len(triage_prompt)} caractères).")
        else:
            print("❌ Tâche 'Triage' MANQUANTE !")

    except Exception as e:
        print(f"❌ Erreur critique lors du test : {e}")
