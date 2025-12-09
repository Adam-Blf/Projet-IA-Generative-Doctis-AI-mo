import json
import os

class DoctisAgent:
    def __init__(self, config_path=None):
        if config_path is None:
            # Default to ../config/prompts.json relative to this script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, '..', 'config', 'prompts.json')
        
        self.config = self._load_config(config_path)

    def _load_config(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at {path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file at {path}")

    def get_system_prompt(self, task_name):
        tasks = self.config.get('tasks', {})
        task = tasks.get(task_name)
        if not task:
            return None
        return task.get('system_prompt')

    def get_agent_metadata(self):
        return self.config.get('agent_metadata', {})

if __name__ == "__main__":
    # verification
    try:
        agent = DoctisAgent()
        metadata = agent.get_agent_metadata()
        print(f"Agent Loaded: {metadata.get('name')} v{metadata.get('version')}")
        
        # Verify Triage Prompt Update
        triage_prompt = agent.get_system_prompt('triage_urgency')
        if triage_prompt and "Kaggle Medical Datasets" in triage_prompt:
            print("\n[SUCCESS] Triage System Prompt loaded and verified (Kaggle Logic detected).")
        else:
            print("\n[ERROR] Triage task not found or Kaggle logic missing.")

        # Verify Input Enrichment
        enrich_prompt = agent.get_system_prompt('input_enrichment')
        if enrich_prompt:
             print("\n[SUCCESS] Input Enrichment task loaded successfully.")
        else:
             print("\n[ERROR] Input Enrichment task not found.")
            
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Failed to load agent: {e}")
