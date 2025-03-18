from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Event,
)
from back.core import DatabaseManager
from back.ingestion.rss_scraper import RSSScraper
from back.core.news_processing_utils import summarize_cluster, generate_cluster_label, send_telegram_message
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from datetime import date, timedelta
import numpy as np
import os
from sklearn.cluster import DBSCAN
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# Définition des événements
class ArticlesScrapedAndIndexed(Event):
    articles: list

class ArticlesClustered(Event):
    clusters: dict

class ClustersLabeled(Event):
    labeled_clusters: dict

class ArticlesSummarized(Event):
    summaries: dict

# Classe principale du workflow
class NewsProcessingWorkflow(Workflow):
    def __init__(self, duration=1):
        super().__init__(timeout=600, verbose=True)
        self.db_manager = DatabaseManager()
        self.scraper = RSSScraper(self.db_manager)
        self.docstore = MongoDocumentStore.from_uri(
            uri=os.getenv("MONGODB_URI")
        )
        self.duration = duration

    @step
    async def scrape_articles(self, ev: StartEvent) -> ArticlesScrapedAndIndexed:
        print("📡 Scraping des flux RSS en cours...")
        self.scraper.scrape_and_ingest()
        articles = self.db_manager.get_articles()
        print(f"📌 Articles à indexer : {len(articles)}")
        return ArticlesScrapedAndIndexed(articles=articles)

    
    @step
    async def refine_article_categories(self, ev: ArticlesScrapedAndIndexed) -> ArticlesClustered:
        print(f"🧩 Vérification et ajustement des catégories pour les {self.duration} derniers jours...")
        articles = self.db_manager.get_articles_since(self.duration)
        
        # 🔥 Pré-clustering manuel par catégorie
        categories = defaultdict(list)
        for article in articles:
            category = article["metadata"].get("category", "uncategorized")
            categories[category].append(article)
        
        # 🔥 Affinage avec DBSCAN pour regrouper par sujets similaires
        updated_clusters = {}
        for category, cat_articles in categories.items():
            if len(cat_articles) < 4:  # Pas assez d'articles pour clusteriser
                updated_clusters[category] = {"0": cat_articles}
                continue
            
            embeddings = np.array([a["metadata"].get("embedding") for a in cat_articles if "embedding" in a["metadata"]])
            if len(embeddings) < 4:
                updated_clusters[category] = {"0": cat_articles}  # Trop peu d'embeddings valides
                continue

            clustering = DBSCAN(eps=0.2, min_samples=4, metric='cosine').fit(embeddings)
            category_clusters = defaultdict(list)
            
            for label, article in zip(clustering.labels_, cat_articles):
                cluster_id = str(label) if label != -1 else "-1"  # -1 = bruit
                category_clusters[cluster_id].append(article)

            updated_clusters[category] = category_clusters

        return ArticlesClustered(clusters=updated_clusters)

    @step
    async def label_clusters(self, ev: ArticlesClustered) -> ClustersLabeled:
        print("🏷️ Génération des labels pour chaque cluster...")
        labeled_clusters = {}
        
        for category, category_clusters in ev.clusters.items():
            for cluster_id, articles in category_clusters.items():
                titles = [article["metadata"]["title"] for article in articles if "metadata" in article and "title" in article["metadata"]]
                label = generate_cluster_label(titles)
                labeled_clusters[(category, cluster_id)] = {
                    "label": label,
                    "category": category,
                    "articles": articles
                }

        print(f"✅ Labels générés pour {len(labeled_clusters)} clusters.")
        return ClustersLabeled(labeled_clusters=labeled_clusters)

    @step
    async def summarize_clusters(self, ev: ClustersLabeled) -> ArticlesSummarized:
        print("📝 Génération des résumés pour chaque cluster...")
        summaries = {}
        for (category, cluster_id), cluster_info in ev.labeled_clusters.items():
            label = cluster_info["label"]
            articles = cluster_info["articles"]
            summary = summarize_cluster(articles)
            summaries[f"{category} - {label}"] = summary
        return ArticlesSummarized(summaries=summaries)

    @step
    async def finalize_workflow(self, ev: ArticlesSummarized) -> StopEvent:
        print("📅 Synthèse des faits marquants du jour par thème :")
        for cluster_name, summary in ev.summaries.items():
            message = f"\n🌍 {cluster_name}\n{summary}"
            send_telegram_message(message)

        return StopEvent(result="✅ Workflow terminé avec succès !")

# Création du workflow
def get_news_workflow(duration=1):
    return NewsProcessingWorkflow(duration=duration)
