import os
from dotenv import load_dotenv
from pymongo import MongoClient, TEXT
from datetime import datetime, timedelta, date

load_dotenv()

class DatabaseManager:
    def __init__(self):
        """Initialisation de la connexion MongoDB"""
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client[os.getenv("MONGO_DB_NAME")]
        self.collection = self.db[os.getenv("MONGO_COLLECTION")]

        # 🔍 Vérification des index existants
        existing_indexes = self.collection.index_information()
        index_name = "content_text_title_text"

        if index_name in existing_indexes:
            print(f"🔄 Index {index_name} existe déjà, suppression et recréation...")
            self.collection.drop_index(index_name)

        # ✅ Création d'un nouvel index texte si besoin
        self.collection.create_index([("title", TEXT), ("content", TEXT)], name=index_name)
        print(f"✅ Index {index_name} créé avec succès.")

    def get_rss_feeds(self):
        """Récupère les flux RSS stockés dans MongoDB."""
        feeds = self.db["sources"].find({}, {"_id": 0, "url": 1})
        return [feed["url"] for feed in feeds]

    def insert_article(self, article):
        """Ajoute un article à MongoDB s'il n'existe pas déjà"""
        if not self.collection.find_one({"link": article["link"]}):
            self.collection.insert_one(article)
            print(f"✅ Article inséré : {article['title']}")
        else:
            print(f"🔵 Article déjà en base : {article['title']}")

    def get_articles(self):
        """Récupère tous les articles de la collection MongoDB."""
        return list(self.collection.find({}, {"_id": 0}))  # Exclure l'ID MongoDB
    
    

    def get_articles_of_day(db_manager, target_date):
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())
        
        articles = list(db_manager.collection.find({
            "pub_date": {"$gte": start, "$lt": end}  # 🔥 Ne filtre plus sur `content_vector`
        }, {"_id": 0}))
        
        print(f"📌 Articles récupérés pour {target_date} : {len(articles)}")
        
        return articles
    
    from datetime import datetime

    def get_articles_since(self, duration):
        """Récupère les articles publiés depuis une période définie (en jours)."""
        
        # Vérifie que `duration` est bien un entier (sécurisation)
        if not isinstance(duration, int):
            raise ValueError("❌ Erreur: `duration` doit être un entier représentant le nombre de jours.")

        # Calcul correct de la plage de dates
        start_date = datetime.combine(date.today() - timedelta(days=duration), datetime.min.time())
        end_date = datetime.combine(date.today(), datetime.min.time())
        
        articles = list(self.collection.find({
            "pub_date": {"$gte": start_date, "$lt": end_date}
        }, {"_id": 0}))

        print(f"📌 Articles récupérés depuis {start_date.strftime('%Y-%m-%d')} : {len(articles)}")
        return articles


    
    def update_embedding(self, link, embedding):
        """Met à jour l'embedding seulement s'il n'existe pas déjà"""
        existing_article = self.collection.find_one({"link": link}, {"content_vector": 1})

        if existing_article and "content_vector" in existing_article and existing_article["content_vector"]:
            print(f"⚠️ Embedding déjà existant pour {link}, SKIP")
            return  # On ne remplace pas

        print(f"📡 Enregistrement de l'embedding pour {link} en base")
        self.collection.update_one(
            {"link": link}, {"$set": {"content_vector": embedding}}
        )
        print(f"✅ Embedding stocké pour {link}")


    
    def close(self):
        """Ferme la connexion MongoDB"""
        self.client.close()
