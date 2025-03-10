from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Event,
)
from database_manager import DatabaseManager
from rss_scraper import RSSScraper
from embedding_generator import EmbeddingGenerator
from search_embeddings import SearchEmbeddings
from news_processing_utils import summarize_cluster, generate_cluster_label, send_telegram_message
from mongo_docstore import MongoDBDocStore
from datetime import date
import numpy as np
import os
from sklearn.cluster import DBSCAN
from collections import defaultdict
from dotenv import load_dotenv
from llama_index.utils.workflow import draw_all_possible_flows
from datetime import date, timedelta

load_dotenv()

# Définition des événements
class ArticlesScraped(Event):
    articles: list

class ArticlesIndexed(Event):
    articles: list

class ArticlesClustered(Event):
    clusters: dict

class ClustersLabeled(Event):
    labeled_clusters: dict

class ArticlesSummarized(Event):
    summaries: dict

# Classe principale du workflow
class NewsProcessingWorkflow(Workflow):
    def __init__(self, duration):  
        self.db_manager = DatabaseManager()
        self.scraper = RSSScraper(self.db_manager)
        self.docstore = MongoDBDocStore(
            uri=os.getenv("MONGO_URI"),
            db_name=os.getenv("MONGO_DB_NAME"),
            collection_name=os.getenv("MONGO_COLLECTION")
        )
        self.embedder = EmbeddingGenerator(self.db_manager, self.docstore, os.getenv("OPENAI_API_KEY"))
        self.duration = duration  
        

    @step
    async def scrape_articles(self, ev: StartEvent) -> ArticlesScraped:
        print("📡 Scraping des flux RSS en cours...")

        feeds_with_categories = self.scraper.get_rss_feeds_with_categories()
        if not feeds_with_categories:
            print("❌ Aucun flux RSS enregistré en base !")
            return ArticlesScraped(articles=[])

        for feed_url, category in feeds_with_categories.items():
            print(f"📡 Scraping {feed_url} (Catégorie : {category})")
            self.scraper.scrape_feed(feed_url, category)

        articles = self.docstore.get_all_documents()
        print(f"📌 Articles à indexer : {len(articles)}")
        return ArticlesScraped(articles=articles)

    @step
    async def index_articles(self, ev: ArticlesScraped) -> ArticlesIndexed:
        print("🔍 Génération des embeddings...")

        articles_to_update = [
            article for article in ev.articles 
            if not article.get("content_vector")
        ]

        print(f"📌 Articles nécessitant un embedding : {len(articles_to_update)}")

        for article in articles_to_update:
            text = f"{article['title']} {article.get('content', '')}"
            embedding = self.embedder.generate_embedding(text)
            if embedding:
                self.docstore.update_document(article["_id"], {"content_vector": embedding})

        updated_articles = self.docstore.get_all_documents()
        return ArticlesIndexed(articles=updated_articles)

    @step
    async def refine_article_categories(self, ev: ArticlesIndexed) -> ArticlesClustered:
        print(f"🧩 Vérification et ajustement des catégories des articles publiés ces {self.duration} derniers jours...")

        # Calcul de la date de début en fonction de la durée
        start_date = date.today() - timedelta(days=self.duration)

        # Récupération des articles selon cette période
        articles = self.db_manager.get_articles_since(start_date)

        # Log pour vérification
        print(f"📅 Nombre d'articles récupérés : {len(articles)}")
        categories = defaultdict(list)

        for article in articles:
            category = article.get("category", "uncategorized")
            categories[category].append(article)

        updated_clusters = {}

        for category, cat_articles in categories.items():
            print(f"📌 Analyse de la catégorie : {category} ({len(cat_articles)} articles)")

            # Vérification qu'on a assez d'articles
            if len(cat_articles) < 3:
                print(f"⚠️ Pas assez d'articles dans {category} pour un clustering pertinent.")
                updated_clusters[category] = {"0": cat_articles}  # ✅ Fixe le format de la structure
                continue  

            embeddings = np.array([article["content_vector"] for article in cat_articles if article.get("content_vector")])

            if embeddings.shape[0] < 3:  # ✅ Vérification qu'on a assez d'embeddings valides
                print(f"⚠️ Pas assez de données pour clusteriser {category}.")
                updated_clusters[category] = {"0": cat_articles}
                continue

            # 🔥 Clustering avec DBSCAN (on garde un eps raisonnable)
            clustering = DBSCAN(eps=0.2, min_samples=4, metric='cosine').fit(embeddings)

            category_clusters = defaultdict(list)
            isolated_articles = []

            for label, article in zip(clustering.labels_, cat_articles):
                if label == -1:
                    isolated_articles.append(article)
                else:
                    category_clusters[label].append(article)

            updated_clusters[category] = {str(label): articles for label, articles in category_clusters.items()}

            # 📌 Vérification des articles isolés
            for article in isolated_articles:
                best_category = None
                best_distance = float("inf")

                for other_category, other_articles in categories.items():
                    if other_category == category or len(other_articles) < 3:
                        continue
                    
                    other_embeddings = np.array([a["content_vector"] for a in other_articles if a.get("content_vector")])

                    if other_embeddings.shape[0] < 3:
                        continue

                    avg_distance = np.mean([np.linalg.norm(article["content_vector"] - emb) for emb in other_embeddings])

                    if avg_distance < best_distance:
                        best_distance = avg_distance
                        best_category = other_category

                if best_category and best_distance < 0.2:
                    print(f"🔄 Changement de catégorie : {article['title']} passe de {category} à {best_category}")
                    if "0" not in updated_clusters[best_category]:
                        updated_clusters[best_category]["0"] = []  # 🛠️ Initialisation correcte
                    updated_clusters[best_category]["0"].append(article)
                else:
                    print(f"❌ {article['title']} reste dans {category}.")
                    if "0" not in updated_clusters[category]:  
                        updated_clusters[category]["0"] = []  # 🛠️ Initialisation correcte
                    updated_clusters[category]["0"].append(article)

        print(f"✅ Vérification des catégories terminée avec {len(updated_clusters)} catégories mises à jour.")
        return ArticlesClustered(clusters=updated_clusters)

    @step
    async def label_clusters(self, ev: ArticlesClustered) -> ClustersLabeled:
        print("🏷️ Génération des labels pour chaque cluster...")

        labeled_clusters = {}
        
        for category, category_clusters in ev.clusters.items():
            for cluster_id, articles in category_clusters.items():
                titles = [article["title"] for article in articles]
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

        def split_message(text, max_length=4096):
            """Divise un texte en morceaux compatibles avec la limite de caractères de Telegram."""
            messages = []
            while len(text) > max_length:
                split_index = text[:max_length].rfind('\n')  # Couper proprement à la fin d'une ligne si possible
                if split_index == -1:
                    split_index = max_length  # Au pire, couper au maximum autorisé
                messages.append(text[:split_index])
                text = text[split_index:].strip()
            if text:
                messages.append(text)
            return messages

        for cluster_name, summary in ev.summaries.items():
            category, label = cluster_name.split(" - ", 1)
            message = f"\n🌍 {category.capitalize()} : {label}\n{summary}"

            for chunk in split_message(message):
                try:
                    # Utilise ton code d'envoi de message ici (ajuste en fonction de ton implémentation Telegram)
                    send_telegram_message(chunk)
                except Exception as e:
                    print(f"❌ Erreur lors de l'envoi du message : {e}")

        return StopEvent(result="✅ Workflow terminé avec succès !")



# Création du workflow
news_workflow = NewsProcessingWorkflow()
#draw_all_possible_flows(NewsProcessingWorkflow, filename="NewsProcessingWorkflow.html")