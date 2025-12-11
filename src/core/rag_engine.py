import numpy as np
import pandas as pd
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from src.core.knowledge_base import KnowledgeBase
from src.utils.logger import logger

class RAGEngine:
    """
    Semantic Search Engine for Medical Data.
    """
    
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        # Ensure KB is loaded
        if self.kb.df is None:
            self.kb.load()

    MIN_RELEVANCE_SCORE = 0.25

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
# ... (omitting middle lines for brevity in prompt, but in replacement I must be precise)
# Wait, I can just replace the method or the class variable.
# Better to add the constant at class level and change the line.
    
    MIN_RELEVANCE_SCORE = 0.25

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Performs semantic search to find relevant medical context.
        """
        if self.kb.df is None or self.kb.embeddings is None:
            logger.warning("⚠️ Knowledge Base not ready. Returning empty results.")
            return []
        
        try:
            # 1. Encode Query
            # We need to load the model if not already loaded in KB (it should be if load() was called)
            if self.kb.model is None:
                self.kb._load_model()
                
            query_embedding = self.kb.model.encode([query])
            
            # 2. Compute Similarity
            similarities = cosine_similarity(query_embedding, self.kb.embeddings)[0]
            
            # 3. Get Top K
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                score = similarities[idx]
                if score < self.MIN_RELEVANCE_SCORE: # Threshold for relevance
                    continue
                    
                row = self.kb.df.iloc[idx]
                results.append({
                    "disease": row['disease'],
                    "symptoms": row['all_symptoms'],
                    "description": row.get('description', 'N/A'),
                    "precautions": row.get('precautions', 'N/A'),
                    "score": float(score)
                })
                
            return results
            
        except Exception as e:
            logger.error(f"❌ RAG Search Error: {e}")
            return []
