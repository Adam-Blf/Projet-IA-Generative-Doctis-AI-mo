# ==============================================================================
# DOCTIS-AI-MO: MONITORING & KEEP-ALIVE
# Version: v15.4-Optimized
# Auteurs: Adam Beloucif & Amina Medjdoub
# ==============================================================================

import os
import time
import threading
import requests # type: ignore
import streamlit as st
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional, Tuple

class HealthMonitor:
    """
    Système de surveillance et de maintien en vie (Keep-Alive) pour l'application.
    S'assure que le serveur Render ne s'endort pas et log les états dans MongoDB.
    """

    def __init__(self, app_url: str, mongo_uri: Optional[str] = None) -> None:
        """
        Initialise le moniteur.
        
        Args:
            app_url (str): L'URL publique de l'application (pour le ping).
            mongo_uri (Optional[str]): Chaîne de connexion MongoDB.
        """
        self.app_url = app_url
        self.interval_seconds = 14 * 60  # 14 minutes
        self.mongo_uri = mongo_uri
        self.db_client: Optional[MongoClient] = None
        self.collection = None
        self._setup_db()

    def _setup_db(self) -> None:
        """Configure la connexion MongoDB si une URI est fournie."""
        if self.mongo_uri:
            try:
                self.db_client = MongoClient(self.mongo_uri)
                db = self.db_client['doctis_logs']
                self.collection = db['health_checks']
                print("✅ [MONITOR] Connexion MongoDB établie.")
            except Exception as e:
                print(f"⚠️ [MONITOR] Erreur connexion MongoDB: {e}")

    def log_status(self, success: bool, details: str = "") -> None:
        """
        Met à jour l'état du ping dans MongoDB (Overwrite).
        """
        if self.collection is not None:
            try:
                filter_query = {"_id": "health_monitor_status"}
                update_data = {
                    "$set": {
                        "last_check": datetime.utcnow(),
                        "status": "UP" if success else "DOWN",
                        "details": details,
                        "module": "HealthMonitor",
                        "app_url": self.app_url
                    }
                }
                self.collection.update_one(filter_query, update_data, upsert=True)
            except Exception as e:
                print(f"⚠️ [MONITOR] Impossible de logger dans Mongo: {e}")

    def check_health(self) -> Tuple[bool, str]:
        """Effectue une requête GET sur l'application elle-même."""
        try:
            print(f"Ping {self.app_url} ...")
            response = requests.get(self.app_url, timeout=10)
            if response.status_code == 200:
                return True, f"Status Code: {response.status_code}"
            else:
                return False, f"Error Code: {response.status_code}"
        except Exception as e:
            return False, str(e)

    def start_background_loop(self) -> None:
        """Lance la boucle infinie dans un thread séparé (Non-bloquant)."""
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        print("🚀 [MONITOR] Boucle de maintenance démarrée (14 min).")

    def _loop(self) -> None:
        """La boucle interne qui tourne indéfiniment."""
        while True:
            success, msg = self.check_health()
            if success:
                print(f"✅ [Keep-Alive] Ping succès : {msg}")
            else:
                print(f"❌ [Keep-Alive] Echec : {msg}")
            
            self.log_status(success, msg)
            time.sleep(self.interval_seconds)

def init_monitor() -> None:
    """
    Initialise le monitoring uniquement si ce n'est pas déjà fait.
    """
    if 'monitor_started' not in st.session_state:
        # Secure Secret Retrieval (Env > TOML > Fallback)
        MONGO_URI = os.environ.get("MONGO_URI")
        if not MONGO_URI:
            try:
                MONGO_URI = st.secrets.get("MONGO_URI")
            except:
                pass
        
        if not MONGO_URI:
            MONGO_URI = "mongodb+srv://Users:123@cluster0d.3freyyr.mongodb.net/" # Fallback temporaire
            
        APP_URL = "https://doctis-aimo.onrender.com"
        
        monitor = HealthMonitor(APP_URL, MONGO_URI)
        monitor.start_background_loop()
        
        st.session_state['monitor_started'] = True
