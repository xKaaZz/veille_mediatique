import openai
import numpy as np

class EmbeddingGenerator:
    """Classe pour générer et stocker des embeddings avec OpenAI."""
    
    def __init__(self, db_manager, api_key):
        """
        Initialise le générateur d'embeddings avec une connexion à MongoDB et une clé API OpenAI.
        :param db_manager: Instance de DatabaseManager.
        :param api_key: Clé API OpenAI.
        """
        self.db_manager = db_manager
        openai.api_key = api_key

    def generate_embedding(self, text):
        """Génère un embedding à partir du texte en utilisant OpenAI."""
        try:
            print(f"🚀 Envoi d'un embedding pour : {text[:50]}...")
            response = openai.embeddings.create(model="text-embedding-ada-002", input=text)
            embedding = response.data[0].embedding
            print(f"✅ Embedding généré ({len(embedding)} valeurs) pour : {text[:50]}...")
            return embedding
        except Exception as e:
            print(f"❌ Erreur OpenAI : {e}")
            return None