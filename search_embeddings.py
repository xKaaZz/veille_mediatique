import numpy as np

class SearchEmbeddings:
    """Classe pour rechercher des articles par similarité d'embeddings."""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def cosine_similarity(self, vec1, vec2):
        """Calcule la similarité cosinus entre deux vecteurs."""
        vec1, vec2 = np.array(vec1), np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def search_similar_articles(self, query_embedding, top_k=5):
        """Recherche les articles les plus proches d'un embedding donné."""
        articles = self.db_manager.collection.find(
            {"content_vector": {"$exists": True}},
            {"_id": 0, "title": 1, "content_vector": 1}
        )

        scored_articles = []
        for article in articles:
            similarity = self.cosine_similarity(query_embedding, article["content_vector"])
            scored_articles.append((article["title"], similarity))

        # 🔥 Trier par similarité décroissante et renvoyer les `top_k`
        scored_articles.sort(key=lambda x: x[1], reverse=True)
        return scored_articles[:top_k]
