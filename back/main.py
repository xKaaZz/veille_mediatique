import os
import argparse
from back.core import DatabaseManager
from back.ingestion import RSSScraper
import asyncio
from back.workflow.workflow import get_news_workflow
from dotenv import load_dotenv

load_dotenv()

async def main(duration):
    print(f"🚀 Exécution du workflow pour les {duration} derniers jours...")
    news_workflow = get_news_workflow(duration=duration)
    result = await news_workflow.run(timeout=600)
    print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lancement du workflow avec une période personnalisée")
    parser.add_argument("--duration", type=int, default=1, help="Nombre de jours à analyser (ex: 1, 3, 7...)")
    args = parser.parse_args()

    asyncio.run(main(args.duration))