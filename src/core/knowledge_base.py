import os
import pandas as pd
import numpy as np
import pickle
from typing import Tuple, Optional, List
from sentence_transformers import SentenceTransformer
from src.utils.logger import logger
from src.utils.config import Config

class KnowledgeBase:
    """
    Manages the medical knowledge base (ETL + Embeddings).
    """
    
    FILENAMES = {
        "symptoms": "dataset.csv",
        "description": "symptom_Description.csv",
        "precaution": "symptom_precaution.csv",
        "severity": "Symptom-severity.csv",
        "s2d_extra": "Symptom2Disease.csv",
    }
    
    DB_FILENAME = "medical_knowledge_base.csv"
    EMBEDDINGS_FILENAME = "embeddings_cache.pkl"

    def __init__(self):
        self.data_dir = Config.DATA_DIR
        self.db_path = os.path.join(self.data_dir, self.DB_FILENAME)
        self.embeddings_path = os.path.join(self.data_dir, self.EMBEDDINGS_FILENAME)
        self.df: Optional[pd.DataFrame] = None
        self.embeddings: Optional[np.ndarray] = None
        self.model = None

    def _load_model(self):
        """Lazy load the embedding model."""
        if self.model is None:
            logger.info("⏳ Loading Embedding Model (all-MiniLM-L6-v2)...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Model loaded.")

    def load(self, force_reload: bool = False) -> bool:
        """Loads the DB and Embeddings. Runs ETL if missing."""
        if not force_reload and os.path.exists(self.db_path) and os.path.exists(self.embeddings_path):
            try:
                self.df = pd.read_csv(self.db_path)
                with open(self.embeddings_path, 'rb') as f:
                    self.embeddings = pickle.load(f)
                logger.info(f"✅ Knowledge Base loaded ({len(self.df)} entries).")
                return True
            except Exception as e:
                logger.warning(f"⚠️ Cache corrupted, rebuilding... Error: {e}")
        
        return self.build_pipeline()

    def build_pipeline(self) -> bool:
        """Runs the ETL pipeline and generates embeddings."""
        logger.info("⚙️ Starting ETL Pipeline...")
        
        # 1. EXTRACT & TRANSFORM (Logic adapted from old data_loader.py)
        try:
            df_master = self._run_etl()
            if df_master.empty:
                logger.error("❌ ETL Failed: No data generated.")
                return False
            
            # 2. GENERATE EMBEDDINGS
            self._load_model()
            logger.info("🧠 Generating Embeddings (this may take a moment)...")
            
            # Create a rich text representation for embedding
            df_master['embedding_text'] = df_master.apply(
                lambda x: f"{x['disease']} {x['all_symptoms']} {x.get('description', '')}", axis=1
            )
            
            embeddings = self.model.encode(df_master['embedding_text'].tolist(), show_progress_bar=True)
            
            # 3. SAVE
            df_master.to_csv(self.db_path, index=False)
            with open(self.embeddings_path, 'wb') as f:
                pickle.dump(embeddings, f)
            
            self.df = df_master
            self.embeddings = embeddings
            
            logger.info("✅ ETL & Embeddings Complete.")
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline Error: {e}")
            return False

    def _run_etl(self) -> pd.DataFrame:
        """Internal ETL logic."""
        # Helper to read
        def read(fname):
            p = os.path.join(self.data_dir, fname)
            return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()
        
        df_symp = read(self.FILENAMES["symptoms"])
        df_desc = read(self.FILENAMES["description"])
        df_prec = read(self.FILENAMES["precaution"])
        df_extra = read(self.FILENAMES["s2d_extra"])
        
        if df_symp.empty and df_extra.empty:
            return pd.DataFrame()

        # Cleaning
        for df in [df_symp, df_desc, df_prec, df_extra]:
            if not df.empty:
                df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # Merge Logic
        # 1. Main Symptoms
        if not df_symp.empty:
            df_symp['all_symptoms'] = df_symp.apply(lambda x: ', '.join([str(s).strip() for s in x.values[1:] if str(s) != 'nan']), axis=1)
            df_master = df_symp[['disease', 'all_symptoms']].copy()
        else:
            df_master = pd.DataFrame(columns=['disease', 'all_symptoms'])

        # 2. Extra Symptoms
        if not df_extra.empty:
            df_extra = df_extra.rename(columns={'label': 'disease', 'text': 'symptoms_extra'})
            grouped = df_extra.groupby('disease')['symptoms_extra'].apply(lambda x: ', '.join(x)).reset_index()
            df_master = pd.merge(df_master, grouped, on='disease', how='outer')
            df_master['all_symptoms'] = df_master['all_symptoms'].fillna('') + ", " + df_master['symptoms_extra'].fillna('')
            df_master.drop(columns=['symptoms_extra'], inplace=True)

        # 3. Metadata
        df_master['disease'] = df_master['disease'].astype(str).str.strip()
        if not df_desc.empty:
            df_desc['disease'] = df_desc['disease'].astype(str).str.strip()
            df_master = pd.merge(df_master, df_desc, on='disease', how='left')
        
        if not df_prec.empty:
            df_prec['disease'] = df_prec['disease'].astype(str).str.strip()
            df_prec['precautions'] = df_prec.apply(lambda x: ', '.join([str(p).strip().title() for p in x if str(p) != 'nan' and p != x['disease']]), axis=1)
            df_master = pd.merge(df_master, df_prec[['disease', 'precautions']], on='disease', how='left')

        df_master.fillna("Non spécifié", inplace=True)
        return df_master
