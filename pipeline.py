from llama_index.core import Document
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from database_manager import DatabaseManager
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

# Pipeline d'ingestion avec SentenceSplitter, TitleExtractor et Embedding
def run_pipeline():
    print("📡 Chargement des articles...")
    articles = db_manager.get_articles()

    documents = [
        Document(
            text=article["content"],
            metadata={
                "link": article["link"],
                "category": article["category"],
                "description": article["description"],
                "source": article["source"],
                "title": article["title"]
            },
        )
        for article in articles
    ]

    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=500, chunk_overlap=0),
            embed_model,
        ],
        vector_store=vector_store,
        docstore=docstore
    )

    print("🚀 Lancement du pipeline avec SentenceSplitter, TitleExtractor et Embedding...")
    pipeline.run(documents=documents)
    print("✅ Pipeline exécuté avec succès !")

    # Création de l'index
    index = VectorStoreIndex.from_vector_store(vector_store)
    print("✅ Index créé avec succès !")

if __name__ == "__main__":
    run_pipeline()
