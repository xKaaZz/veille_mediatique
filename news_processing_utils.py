# news_processing_utils.py

import numpy as np
from sklearn.cluster import DBSCAN
import openai
import tiktoken
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

def cluster_articles(articles, eps=0.3, min_samples=2):
    embeddings = np.array([article["content_vector"] for article in articles])
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine').fit(embeddings)
    
    clusters = {}
    for label, article in zip(clustering.labels_, articles):
        if label != -1:
            clusters.setdefault(label, []).append(article)
    return clusters


def num_tokens(text):
    return len(tokenizer.encode(text))

def chunk_text(texts, max_tokens=14000):
    chunks, current_chunk, current_length = [], [], 0
    for text in texts:
        tokens = num_tokens(text)
        if current_length + tokens > max_tokens:
            chunks.append(current_chunk)
            current_chunk, current_length = [text], tokens
        else:
            current_chunk.append(text)
            current_length += tokens
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def summarize_text(text):
    prompt = (
        "Tu es un expert en synthèse d'actualités. Résume ces articles bullets points de bullet points afin d'avoir une synthèse complète :\n\n"
        f"{text}"
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es un expert en synthèse d'actualités. Résume ces articles bullets points de bullet points afin d'avoir une synthèse complète"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

def summarize_cluster(cluster_articles):
    articles_texts = [f"{a['title']}. {a.get('content', '')}" for a in cluster_articles]

    chunks = chunk_text(articles_texts)

    intermediate_summaries = []
    for chunk in chunks:
        combined_text = "\n\n".join(chunk)
        summary = summarize_text(combined_text)
        intermediate_summaries.append(summary)

    final_summary = summarize_text("\n\n".join(intermediate_summaries))

    return final_summary

def generate_cluster_label(titles):
    prompt = (
        "Tu es un expert en catégorisation de l'actualité. "
        "Génère un **titre explicite et descriptif** en 4-5 mots maximum pour le **thème principal** de ces articles :\n"
        + "\n".join(titles)
        + "\n\nRéponds uniquement par un titre court et explicite qui pourrait être utilisé comme catégorie d'un journal."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=12,  # Légèrement augmenté pour éviter les raccourcis
        temperature=0
    )

    return response.choices[0].message.content.strip()


