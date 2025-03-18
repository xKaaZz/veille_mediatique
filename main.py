import os
import argparse  # ➤ Ajout pour gérer les arguments
from database_manager import DatabaseManager
from rss_scraper import RSSScraper
from embedding_generator import EmbeddingGenerator
import asyncio
from workflow import NewsProcessingWorkflow  # ➤ Import mis à jour pour utiliser la classe avec durée
from workflow import get_news_workflow
from dotenv import load_dotenv
load_dotenv()

async def main(duration):
    """
    # Ancien menu interactif (désactivé temporairement)
    db_manager = DatabaseManager()

    while True:
        print("\n=== MENU ===")
        print("1️⃣  Scraper les articles RSS")
        print("2️⃣  Générer les embeddings")
        print("3️⃣  Rechercher des articles similaires")
        print("4️⃣  Exécuter le workflow")
        print("5️⃣  Quitter")

        choice = input("➡️  Choisissez une option : ")

        if choice == "1":
            scraper = RSSScraper(db_manager)
            scraper.run()

        elif choice == "2":
            embedder = EmbeddingGenerator(db_manager, os.getenv("OPENAI_API_KEY"))
            embedder.update_embeddings()

        elif choice == "3":
            print("🔎 Recherche d'articles similaires via MongoDB...")
            results = await news_workflow.search_similar_articles()
            print(results)

        elif choice == "4":
            print("🚀 Exécution du workflow...")
            result = await news_workflow.run(duration=duration, timeout=600)
            print(result)

        elif choice == "5":
            print("👋 Bye !")
            db_manager.close()
            break

        else:
            print("❌ Option invalide, réessayez.")
    """

    # Nouvelle version : Lancement direct du workflow avec durée personnalisée
    print(f"🚀 Exécution du workflow pour les {duration} derniers jours...")
    news_workflow = get_news_workflow(duration=duration)
    result = await news_workflow.run(timeout=600)
    print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lancement du workflow avec une période personnalisée")
    parser.add_argument("--duration", type=int, default=1, help="Nombre de jours à analyser (ex: 1, 3, 7...)")
    args = parser.parse_args()

    asyncio.run(main(args.duration))
