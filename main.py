import os
from dotenv import load_dotenv
from database_manager import DatabaseManager
from rss_scraper import RSSScraper
from embedding_generator import EmbeddingGenerator
import asyncio
from workflow import news_workflow

load_dotenv()

async def main():
    """Menu interactif"""
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
            result = await news_workflow.run()
            print(result)

        elif choice == "5":
            print("👋 Bye !")
            db_manager.close()
            break

        else:
            print("❌ Option invalide, réessayez.")

if __name__ == "__main__":
    asyncio.run(main())
