import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration for DoctisAImo."""
    
    # API Keys
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    
    # Model Configuration
    DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
    FALLBACK_GEMINI_MODEL = "gemini-1.5-pro-latest"
    
    DEFAULT_OPENAI_MODEL = "gpt-4o"
    FALLBACK_OPENAI_MODEL = "gpt-3.5-turbo"
    
    LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/v1") # Default to Ollama
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.join(BASE_DIR, '..', '..')
    DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
    PROMPTS_PATH = os.path.join(PROJECT_ROOT, 'config', 'prompts.json')
    
    @classmethod
    def validate(cls):
        """Check for critical missing configuration."""
        missing = []
        if not cls.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        # OpenAI is optional (Fallback)
        return missing
