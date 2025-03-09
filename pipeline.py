from database_manager import DatabaseManager
from rss_scraper import RSSScraper
from embedding_generator import EmbeddingGenerator
from mongo_docstore import MongoDBDocStore
import openai
import pymongo
import os
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.storage.index_store.mongodb import MongoIndexStore
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import Document
from llama_index.core import SimpleDirectoryReader, StorageContext


def get_mongo_client(mongo_uri):
  """Establish connection to the MongoDB."""
  try:
    client = pymongo.MongoClient(mongo_uri)
    print("Connection to MongoDB successful")
    return client
  except pymongo.errors.ConnectionFailure as e:
    print(f"Connection failed: {e}")
    return None


uri=os.getenv("MONGO_URI")


db_manager = DatabaseManager()
scraper = RSSScraper(db_manager)

mongo_client = get_mongo_client(uri)
DB_NAME="news_database"
COLLECTION_NAME="llama"
db = mongo_client[os.getenv("MONGO_DB_NAME")]

embed_model = OpenAIEmbedding(model="text-embedding-ada-002")

from llama_index.core.ingestion import IngestionPipeline

articles = db_manager.get_articles()
documents=[]

for article in articles:
    document = Document(
    text=article["content"],
    metadata={
        "link": article["link"],
        "category": article["category"],
        "description": article["description"],
        "source": article["source"],
        "title": article["title"] 
        },
    )
    documents.append(document)

from llama_index.core.node_parser import SentenceSplitter

parser = SentenceSplitter()
docstore=MongoDocumentStore.from_uri(uri=uri),
index_store=MongoIndexStore.from_uri(uri=uri),

storage_context = StorageContext.from_defaults(
    docstore=docstore,
    index_store=index_store,
)
vector_store = MongoDBAtlasVectorSearch(mongo_client, db_name=DB_NAME, collection_name=COLLECTION_NAME, vector_index_name="vector_index")

pipeline = IngestionPipeline(
    transformations=[
        embed_model,
        parser
    ],
   vector_store=vector_store,
)



pipeline.run(documents=documents)