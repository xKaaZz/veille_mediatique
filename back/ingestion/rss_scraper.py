from llama_index.core import Document, StorageContext
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.storage.index_store.mongodb import MongoIndexStore
from datetime import datetime
import feedparser
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import time
import os

class RSSScraper:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.failed_sources = set()

        # Initialisation du pipeline
        uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("MONGO_DB_NAME")
        collection_name = os.getenv("MONGO_COLLECTION")

        self.docstore = MongoDocumentStore.from_uri(uri=uri)
        self.vector_store = MongoDBAtlasVectorSearch(
            uri=uri, db_name=db_name, collection_name=collection_name, vector_index_name="vector_index"
        )
        self.index_store = MongoIndexStore.from_uri(uri=uri)

        self.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")

        self.pipeline = IngestionPipeline(
            transformations=[
                self.embed_model,
                SentenceSplitter(chunk_size=500, chunk_overlap=0)
            ],
            vector_store=self.vector_store
        )

        self.storage_context = StorageContext.from_defaults(
            docstore=self.docstore,
            vector_store=self.vector_store,
            index_store=self.index_store
        )

    def get_rss_feeds_with_categories(self):
        """Récupère les flux RSS stockés dans MongoDB avec leur catégorie associée."""
        feeds = self.db_manager.db["sources"].find({}, {"_id": 0, "url": 1, "category": 1})
        return {feed["url"]: feed["category"] for feed in feeds}

    def scrape_feed(self, feed_url, category):
        """Scrape un flux RSS et stocke les articles en base MongoDB avec leur catégorie."""
        if feed_url in self.failed_sources:
            print(f"🚫 Source bloquée, on la saute : {feed_url}")
            return

        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            if 'link' not in entry:
                print(f"❌ Impossible de récupérer le lien pour l'article : {entry.get('title', 'Sans titre')}")
                continue

            title = entry.title
            link = entry.link
            pub_date = datetime(*entry.published_parsed[:6]) if "published_parsed" in entry else datetime.now()
            description = entry.summary if "summary" in entry else None

            existing_article = self.db_manager.collection.find_one({"metadata.link": link})
            if existing_article:
                print(f"🔵 Article déjà en base, pas de réinsertion : {title}")
                continue

            # 🔥 Scraping du contenu complet
            content = self.scrape_full_article(link)

            if not content:
                print(f"❌ Impossible d'obtenir du contenu pour {link}. Article ignoré.")
                continue

            # 🔥 Envoi direct au vecteur store via le pipeline
            document = Document(
                text=content,
                metadata={
                    "link": link,
                    "category": category,
                    "description": description or "",
                    "source": feed_url,
                    "title": title,
                    "pub_date": pub_date.isoformat()
                }
            )

            self.pipeline.run(documents=[document])

            print(f"✅ Article ajouté/mis à jour : {title}")
            time.sleep(1)

    def scrape_full_article(self, url):
        """Scrape le contenu complet d'un article avec Newspaper3k et BeautifulSoup en fallback."""
        try:
            article = Article(url)
            article.download()
            article.parse()

            if article.text and len(article.text) > 100:
                return article.text.strip()
            else:
                print(f"⚠️ Contenu trop court avec Newspaper3k, on tente BeautifulSoup : {url}")
                self.failed_sources.add(url)
                return self.scrape_fallback(url)

        except Exception as e:
            print(f"❌ Newspaper3k a échoué pour {url} : {e}")
            self.failed_sources.add(url)
            return self.scrape_fallback(url)

    def scrape_fallback(self, url):
        """Fallback avec BeautifulSoup si Newspaper3k échoue."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code} - Impossible de récupérer {url}")
                return None

            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = soup.find_all("p")

            text = "\n".join([p.get_text() for p in paragraphs if p.get_text()])
            return text.strip() if len(text) > 100 else None

        except Exception as e:
            print(f"❌ Échec du fallback BeautifulSoup pour {url} : {e}")
            return None

    def scrape_and_ingest(self):
        """Lance le scraping pour tous les flux RSS enregistrés avec leurs catégories."""
        feeds_with_categories = self.get_rss_feeds_with_categories()
        if not feeds_with_categories:
            print("❌ Aucun flux RSS enregistré en base !")
            return

        for feed_url, category in feeds_with_categories.items():
            print(f"📡 Scraping {feed_url} ... (Catégorie : {category})")
            self.scrape_feed(feed_url, category)

        print("✅ Scraping terminé !")
