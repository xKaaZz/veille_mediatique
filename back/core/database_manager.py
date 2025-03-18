import os
from dotenv import load_dotenv
from pymongo import MongoClient, TEXT
from datetime import datetime, timedelta, date

load_dotenv()

class DatabaseManager:
    def __init__(self):
        """Initialisation de la connexion MongoDB"""
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client[os.getenv("MONGO_DB_NAME")]
        self.collection = self.db[os.getenv("MONGO_COLLECTION")]

        # 🔍 Vérification et création de l'index principal
        index_name = "content_text_title_text"
        existing_indexes = self.collection.index_information()

        if index_name not in existing_indexes:
            self.collection.create_index([("title", TEXT), ("text", TEXT)], name=index_name)
            print(f"✅ Index {index_name} créé avec succès.")

    def get_articles(self):
        """Récupère tous les articles (format compatible avec le pipeline)"""
        return list(self.collection.find({}, {"_id": 0}))

    def insert_article(self, article):
        """Ajoute ou met à jour un article avec embeddings dans MongoDB."""
        existing_article = self.collection.find_one({"link": article["link"]})
        if existing_article:
            print(f"🔵 Article déjà en base : {article['title']}")
            return

        self.collection.insert_one(article)
        print(f"✅ Article inséré : {article['title']}")

    def get_articles_since(self, duration):
        """Récupère les articles publiés récemment (durée définie)."""
        # Conversion des dates en format ISO 8601 (compatible avec le format en base)
        start_date_str = datetime.combine(date.today() - timedelta(days=duration), datetime.min.time()).isoformat()
        end_date_str = datetime.combine(date.today(), datetime.min.time()).isoformat()

        articles = list(self.collection.find({
            "metadata.pub_date": {"$gte": start_date_str, "$lt": end_date_str}
        }, {"_id": 0}))

        print(f"📌 Articles récupérés depuis {start_date_str[:10]} : {len(articles)}")
        return articles

    def close(self):
        """Ferme la connexion MongoDB"""
        self.client.close()
