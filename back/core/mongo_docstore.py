from llama_index.core import Document
from pymongo import MongoClient
from bson import ObjectId

class MongoDBDocStore:
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri)
        self.collection = self.client[db_name][collection_name]

    def add_document(self, document: Document):
        """Ajoute un document dans MongoDB."""
        self.collection.insert_one(document.to_dict())

    def get_document_by_id(self, doc_id: str):
        """Récupère un document par son identifiant."""
        return self.collection.find_one({"_id": ObjectId(doc_id)})

    def delete_document_by_id(self, doc_id: str):
        """Supprime un document par son identifiant."""
        self.collection.delete_one({"_id": ObjectId(doc_id)})

    def update_document(self, doc_id: str, updates: dict):
        """Met à jour un document existant."""
        self.collection.update_one({"_id": ObjectId(doc_id)}, {"$set": updates})

    def get_all_documents(self):
        """Récupère tous les documents."""
        return list(self.collection.find())

    def filter_documents(self, filter_query: dict):
        """Filtre les documents selon une condition."""
        return list(self.collection.find(filter_query))
