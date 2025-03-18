from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from back.core import DatabaseManager
from llama_index.core import StorageContext
import os
from dotenv import load_dotenv

load_dotenv()

# Initialisation
db_manager = DatabaseManager()

uri = os.getenv("MONGODB_URI")
db_name = os.getenv("MONGO_DB_NAME")
collection_name = os.getenv("MONGO_COLLECTION")

docstore = MongoDocumentStore.from_uri(uri=uri)
vector_store = MongoDBAtlasVectorSearch(
    uri=uri, db_name=db_name, collection_name=collection_name, vector_index_name="vector_index"
)

embed_model = OpenAIEmbedding(model="text-embedding-ada-002")

# Pipeline centralisé
def run_pipeline():
    print("📡 Chargement des articles...")
    articles = db_manager.get_articles()

    documents = [
        Document(
            text=article["text"],
            metadata={
                "link": article["metadata"]["link"],
                "category": article["metadata"]["category"],
                "description": article["metadata"]["description"],
                "source": article["metadata"]["source"],
                "title": article["metadata"]["title"]
            },
        )
        for article in articles
    ]

    print("🚀 Indexation des articles avec embeddings via le pipeline...")
    storage_context = StorageContext.from_defaults(docstore=docstore)

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )

    print("✅ Pipeline exécuté avec succès et index créé !")

if __name__ == "__main__":
    run_pipeline()