from llama_index.core import Document, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from datetime import datetime
import feedparser
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import time

class RSSScraper:
    def __init__(self, db_manager):
        """
        Initialise le scraper avec une connexion à la BDD.
        :param db_manager: Instance de DatabaseManager.
        """
        self.db_manager = db_manager
        self.failed_sources = set()  # 🔴 Liste des sources qui posent problème

    def get_rss_feeds_with_categories(self):
        """Récupère les flux RSS stockés dans MongoDB avec leur catégorie associée."""
        feeds = self.db_manager.db["sources"].find({}, {"_id": 0, "url": 1, "category": 1})
        return {feed["url"]: feed["category"] for feed in feeds}

    def scrape_feed(self, feed_url, category):
        """Scrape un flux RSS et stocke en base MongoDB avec la catégorie correspondante."""
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

            existing_content = self.db_manager.collection.find_one({"link": link}, {"content": 1})

            if existing_content and "content" in existing_content and existing_content["content"]:
                print(f"🔵 Article déjà en base, pas de mise à jour : {title}")
                continue

            # 🔥 Scraping du contenu complet
            content = self.scrape_full_article(link)

            if not content:
                print(f"❌ Impossible d'obtenir du contenu pour {link}. Article ignoré.")
                continue

            # 🔥 Insertion en base (sans toucher aux embeddings)
            article_data = {
                "title": title,
                "link": link,
                "pub_date": pub_date,
                "description": description,
                "content": content,
                "source": feed_url,
                "category": category
            }

            self.db_manager.collection.update_one(
                {"link": link},
                {"$set": article_data},
                upsert=True
            )

            print(f"✅ Article ajouté/mis à jour : {title}")

            # 🕒 Pause pour éviter le throttling
            time.sleep(1)

    def scrape_full_article(self, url):
        """Scrape le contenu complet d'un article avec Newspaper3k et BeautifulSoup en fallback."""
        try:
            # 🌍 On tente d'abord avec Newspaper3k
            article = Article(url)
            article.download()
            article.parse()

            if article.text and len(article.text) > 100:  # 🔍 Vérifier qu'on a du contenu valide
                return article.text.strip()
            else:
                print(f"⚠️ Contenu trop court avec Newspaper3k, on tente BeautifulSoup : {url}")
                self.failed_sources.add(url)  # 🔴 On garde en mémoire les sources problématiques
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
            paragraphs = soup.find_all("p")  # 🔍 On récupère tous les paragraphes

            text = "\n".join([p.get_text() for p in paragraphs if p.get_text()])
            return text.strip() if len(text) > 100 else None  # 🔍 Vérifier si le texte est utile

        except Exception as e:
            print(f"❌ Échec du fallback BeautifulSoup pour {url} : {e}")
            return None

    def run(self):
        """Lance le scraping pour tous les flux RSS enregistrés avec leurs catégories."""
        feeds_with_categories = self.get_rss_feeds_with_categories()
        if not feeds_with_categories:
            print("❌ Aucun flux RSS enregistré en base !")
            return

        for feed_url, category in feeds_with_categories.items():
            print(f"📡 Scraping {feed_url} ... (Catégorie : {category})")
            self.scrape_feed(feed_url, category)

        print("✅ Scraping terminé !")
