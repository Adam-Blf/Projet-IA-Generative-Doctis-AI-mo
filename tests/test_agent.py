
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent import DoctisAgent

def test_agent_initialization():
    """Test que l'agent charge la config par défaut."""
    agent = DoctisAgent()
    assert agent.config is not None
    assert 'tasks' in agent.config
    assert 'agent_metadata' in agent.config

def test_triage_prompt_exists():
    """Vérifie que le prompt de triage est bien chargé."""
    agent = DoctisAgent()
    prompt = agent.get_system_prompt('triage_urgency')
    MIN_PROMPT_LENGTH = 50
    assert prompt is not None
    assert len(prompt) > MIN_PROMPT_LENGTH # Le prompt doit avoir du contenu substantiel

def test_metadata_integrity():
    """Vérifie les métadonnées de l'agent."""
    agent = DoctisAgent()
    meta = agent.get_agent_metadata()
    assert 'name' in meta
    assert 'version' in meta
