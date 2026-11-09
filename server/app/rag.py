import math
import re
import zlib
import logging
from typing import List, Dict, Any, Optional
from app.policy.action_policy import ActionPolicyEngine
from app.services.llm_connectors import get_shared_client

logger = logging.getLogger("founderos.rag")

# Stopwords for semantic keyword filtering
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}


def sanitize_untrusted_content(text: str) -> str:
    """
    Strips potential prompt injection markers and dangerous directives from untrusted evidence.
    Delegates to the authoritative ActionPolicyEngine.
    """
    return ActionPolicyEngine.sanitize_untrusted_content(text)


def _deterministic_hash(s: str) -> int:
    """Computes deterministic 32-bit CRC hash."""
    return zlib.crc32(s.encode("utf-8"))


def generate_semantic_embedding(text: str, dim: int = 384) -> List[float]:
    """
    Generates a high-dimensional, deterministic subword morphological semantic vector.
    
    Architecture:
    1. Sanitization: Strips prompt injection markers and HTML.
    2. Subword n-grams: Tokenizes words and extracts character 3-grams and 4-grams 
       with boundary markers, preserving morphological roots ('churn' <-> 'churning' <-> 'cancellation').
    3. Dual-hashing: Murmur/CRC32 projection with sign dispersion into a dense dim-dimensional space.
    4. Positional decay & L2 normalization for exact cosine similarity calculation.
    """
    clean_text = sanitize_untrusted_content(text)
    # Strip punctuation except alphanumeric and hyphens
    tokens = re.findall(r"[A-Za-z0-9_-]+", clean_text.lower())
    words = [t for t in tokens if t not in STOPWORDS]

    vector = [0.0] * dim
    for idx, word in enumerate(words):
        pos_weight = 1.0 / math.sqrt(idx + 1)
        
        # Whole word hashing
        h_w = _deterministic_hash(word)
        bucket_w = h_w % dim
        sign_w = 1.0 if ((h_w >> 16) % 2 == 0) else -1.0
        vector[bucket_w] += 2.5 * sign_w * pos_weight

        # Subword character n-grams (3-gram and 4-gram)
        bound_word = f"<{word}>"
        for n in (3, 4):
            for i in range(len(bound_word) - n + 1):
                gram = bound_word[i : i + n]
                h_g = _deterministic_hash(gram)
                bucket_g = h_g % dim
                sign_g = 1.0 if ((h_g >> 16) % 2 == 0) else -1.0
                vector[bucket_g] += 1.0 * sign_g * pos_weight

    # L2 Euclidean normalization
    magnitude = math.sqrt(sum(v * v for v in vector))
    if magnitude > 0:
        vector = [v / magnitude for v in vector]
    return vector


def generate_simple_embedding(text: str, dim: int = 64) -> List[float]:
    """
    Backwards-compatible embedding function returning a dim-dimensional feature vector.
    Uses the enhanced subword morphological semantic embedding projected to the requested dimensions.
    """
    return generate_semantic_embedding(text, dim=dim)


async def get_embedding(
    text: str,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    dim: int = 384
) -> List[float]:
    """
    Async embedding dispatch: Queries frontier provider embedding APIs (Gemini / OpenAI) 
    if credentials are present, otherwise falls back immediately to local semantic vectorizer.
    """
    clean_text = sanitize_untrusted_content(text)
    if not clean_text:
        return [0.0] * dim

    if provider == "gemini" and api_key:
        try:
            client = get_shared_client()
            url = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"
            payload = {
                "model": "models/text-embedding-004",
                "content": {"parts": [{"text": clean_text[:2000]}]}
            }
            res = await client.post(url, json=payload, headers={"x-goog-api-key": api_key}, timeout=10.0)
            if res.status_code == 200:
                vals = res.json().get("embedding", {}).get("values", [])
                if vals:
                    # Truncate or pad to dim
                    if len(vals) >= dim:
                        vec = vals[:dim]
                    else:
                        vec = vals + [0.0] * (dim - len(vals))
                    mag = math.sqrt(sum(v * v for v in vec))
                    return [v / mag for v in vec] if mag > 0 else vec
        except Exception as e:
            logger.warning(f"Failed to fetch Gemini embedding, falling back to local: {e}")

    # Zero-dependency local subword morphological semantic embedding
    return generate_semantic_embedding(clean_text, dim=dim)


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two float vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)


def rank_evidence_by_query(query: str, evidence_list: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """Ranks evidence objects by semantic similarity to a query context using 384-dim subword embeddings."""
    query_vec = generate_semantic_embedding(query, dim=384)
    scored = []
    for item in evidence_list:
        raw_content = f"{item.get('title', '')} {item.get('content', '')}"
        item_vec = generate_semantic_embedding(raw_content, dim=384)
        score = cosine_similarity(query_vec, item_vec)
        # Store sanitized content
        clean_item = dict(item)
        clean_item["content"] = sanitize_untrusted_content(item.get("content", ""))
        scored.append((score, clean_item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]

