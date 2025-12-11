import google.generativeai as genai
import openai
import requests
import time
from typing import Optional, Dict, Any, List
from src.utils.config import Config
from src.utils.logger import logger

class ModelManager:
    """
    Manages LLM interactions with Smart Fallback (Gemini -> OpenAI -> Local).
    """
    
    def __init__(self):
        self.providers = [
            self._call_gemini_primary,
            self._call_gemini_fallback,
            self._call_openai_primary,
            self._call_openai_fallback,
            self._call_local_llm
        ]
        
        # Configure APIs
        if Config.GOOGLE_API_KEY:
            genai.configure(api_key=Config.GOOGLE_API_KEY)
        
        if Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY

    def generate_content(self, system_prompt: str, user_prompt: str, custom_config: dict = None) -> str:
        """
        Main entry point. Iterates through providers until one succeeds.
        """
        # Configure Dynamic Key if provided
        if custom_config and custom_config.get("api_key"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=custom_config["api_key"])
                # We prioritize Gemini Primary with this new key
                # Note: This changes global state for the process worker. 
                # In production/async, we would instantiate a client per request.
                pass 
            except Exception as e:
                logger.error(f"Failed to configure custom API key: {e}")

        last_error = None
        
        for provider in self.providers:
            provider_name = provider.__name__.replace("_call_", "").upper()
            try:
                logger.info(f"🚀 Attempting generation with: {provider_name}")
                response = provider(system_prompt, user_prompt)
                
                if response:
                    logger.info(f"✅ Success with {provider_name}")
                    return response
                    
            except Exception as e:
                error_msg = str(e).lower()
                logger.warning(f"⚠️ {provider_name} Failed: {e}")
                last_error = e
                
                # Check for specific quota errors to confirm we should switch
                if "quota" in error_msg or "429" in error_msg or "exhausted" in error_msg:
                    logger.warning(f"📉 Quota Limit Reached for {provider_name}. Switching...")
                    continue # Try next provider
                
                # For other errors (e.g. network), maybe we should retry?
                # For now, we treat all errors as trigger to switch for robustness.
                continue

        logger.error("❌ ALL BUILDERS FAILED. Unable to generate content.")
        return f"System Error: Unable to generate response. {str(last_error)}"

    # --- PROVIDERS IMPLEMENTATION ---

    def _call_gemini_primary(self, sys_prompt: str, user_prompt: str) -> str:
        return self._gemini_request(Config.DEFAULT_GEMINI_MODEL, sys_prompt, user_prompt)

    def _call_gemini_fallback(self, sys_prompt: str, user_prompt: str) -> str:
        return self._gemini_request(Config.FALLBACK_GEMINI_MODEL, sys_prompt, user_prompt)

    def _gemini_request(self, model_name: str, sys_prompt: str, user_prompt: str) -> str:
        model = genai.GenerativeModel(
            model_name,
            system_instruction=sys_prompt
        )
        response = model.generate_content(user_prompt)
        return response.text

    def _call_openai_primary(self, sys_prompt: str, user_prompt: str) -> str:
        return self._openai_request(Config.DEFAULT_OPENAI_MODEL, sys_prompt, user_prompt)

    def _call_openai_fallback(self, sys_prompt: str, user_prompt: str) -> str:
        return self._openai_request(Config.FALLBACK_OPENAI_MODEL, sys_prompt, user_prompt)

    def _openai_request(self, model_name: str, sys_prompt: str, user_prompt: str) -> str:
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return completion.choices[0].message.content

    def _call_local_llm(self, sys_prompt: str, user_prompt: str) -> str:
        """
        Calls a local OpenAI-compatible endpoint (e.g. Ollama).
        """
        try:
            payload = {
                "model": "mistral", # Default local model, can be configured
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False
            }
            LOCAL_TIMEOUT = 30
            response = requests.post(f"{Config.LOCAL_LLM_URL}/chat/completions", json=payload, timeout=LOCAL_TIMEOUT)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                raise Exception(f"Local Server Error: {response.text}")
        except requests.exceptions.ConnectionError:
            raise Exception("Local LLM Server (Ollama) is offline.")
