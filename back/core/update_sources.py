from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

OPTIMIZED_SOURCES = [
    # 📰 Actu internationale & géopolitique
    {"url": "https://www.reuters.com/rssFeed/worldNews", "category": "International"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "category": "International"},
    {"url": "https://www.bbc.co.uk/news/world/rss.xml", "category": "International"},
    
    # 🏀 Sport (on garde une seule source généraliste)
    {"url": "https://www.eurosport.fr/rss.xml", "category": "Sports"},
    
    # 🖥️ Technologie & innovation
    {"url": "https://www.numerama.com/feed/", "category": "Technologie"},
    {"url": "https://www.01net.com/rss/info/flux-rss/flux-toutes-les-actualites/", "category": "Technologie"},
    
    # 🔬 Science & découvertes (ajout de sources spécialisées)
    {"url": "https://www.futura-sciences.com/rss/actualites.xml", "category": "Sciences"},
    {"url": "https://www.science.org/rss/news_current.xml", "category": "Sciences"},
    {"url": "https://arxiv.org/rss/cs.AI", "category": "IA & Machine Learning"},
    
    # 🇫🇷 Actu France
    {"url": "https://www.lefigaro.fr/rss/figaro_actualite-france.xml", "category": "France"},
    {"url": "https://www.francetvinfo.fr/titres.rss", "category": "France"},
]


class SourceUpdater:
    def __init__(self):
        """Initialisation de la connexion MongoDB."""
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client[os.getenv("MONGO_DB_NAME")]

    def insert_new_sources(self, sources):
        """Insère les nouvelles sources en base."""
        print("📝 Ajout des nouvelles sources...")
        self.db["sources"].insert_many(sources)
        print(f"✅ {len(sources)} sources insérées avec succès.")

    def close(self):
        """Ferme la connexion MongoDB."""
        self.client.close()


if __name__ == "__main__":
    updater = SourceUpdater()
    updater.insert_new_sources(OPTIMIZED_SOURCES)
    updater.close()
