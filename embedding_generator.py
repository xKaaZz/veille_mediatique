import openai
import numpy as np

class EmbeddingGenerator:
    def __init__(self, db_manager, docstore, api_key):
        self.db_manager = db_manager
        self.docstore = docstore
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

    def update_embeddings(self):
        """Met à jour les articles en ajoutant des embeddings si absents."""
        articles = self.docstore.get_all_documents()

        for article in articles:
            if "content_vector" in article and article["content_vector"]:
                print(f"⚠️ Embedding déjà existant pour {article['title']}, SKIP")
                continue  

            text = f"{article['title']} {article.get('content', '')}"
            embedding = self.generate_embedding(text)

            if embedding:
                self.docstore.update_document(
                    doc_id=article["_id"], 
                    updates={"content_vector": embedding}
                )
                print(f"✅ Embedding ajouté pour {article['title']}")
            else:
                print(f"❌ Échec de l'embedding pour {article['title']}")
