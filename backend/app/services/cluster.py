import os
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
import numpy as np
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

embedder = SentenceTransformer("all-MiniLM-L6-v2")
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def extract_topic_label(comment_body: str) -> str:
    """Ask the LLM for a short topic label for a single suggestion comment."""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=30,
        messages=[{
            "role": "user",
            "content": f"In 3-6 words, name the video topic this comment suggests. "
            f"Return only the label, nothing else.\n\nComment: {comment_body}"
        }],
    )
    return response.content[0].text.strip()

def cluster_labels(labels: list[str], distance_threshold: float = 0.6) -> list[int]:
    """Returns a cluster index per label, using cosine distance on embeddings."""
    if len(labels) <= 1:
        return [0] * len(labels)

    embeddings = embedder.encode(labels)
    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric="cosine",
        linkage="average",
    )
    return clustering.fit_predict(embeddings).tolist()

def name_cluster(labels_in_cluster: list[str]) -> str:
    """Ask the LLM to produce one clean name for a group of similar labels."""
    joined = ": ".join(labels_in_cluster)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=30,
        messages=[{
            "role": "user",
            "content": f"These are similar video topic suggestions: {joined}\n\n"
            f"Return one clean 3-6 word name covering all of them. Only the name."
        }],
    )
    return response.content[0].text.strip()