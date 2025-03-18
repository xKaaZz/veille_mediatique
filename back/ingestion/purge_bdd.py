from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseCleaner:
    def __init__(self):
        """Initialisation de la connexion MongoDB."""
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client[os.getenv("MONGO_DB_NAME")]
        self.collection = self.db[os.getenv("MONGO_COLLECTION")]

    def purge_database(self):
        """Supprime toutes les sources et articles existants."""
        print("🚨 Suppression de toutes les sources et articles...")
        self.db["sources"].delete_many({})
        self.collection.delete_many({})
        print("✅ Base de données purgée !")

    def close(self):
        """Ferme la connexion MongoDB."""
        self.client.close()


if __name__ == "__main__":
    cleaner = DatabaseCleaner()
    cleaner.purge_database()
    cleaner.close()
