import math
import re
from typing import List, Dict, Any

# Pattern matching indirect prompt injection attempts
_INJECTION_PATTERN = re.compile(
    r"(ignore\s+previous\s+instructions|system\s+prompt|system\s+instruction|forget\s+all\s+rules|override\s+policy)",
    re.IGNORECASE
)


def sanitize_untrusted_content(text: str) -> str:
    """
    Strips potential prompt injection markers and dangerous directives from untrusted evidence.
    """
    if not text:
        return ""
    # Neutralize injection attempts
    sanitized = _INJECTION_PATTERN.sub("[redacted instruction]", text)
    # Strip HTML tags
    sanitized = re.sub(r"<[^>]*>", "", sanitized)
    return sanitized.strip()


def generate_simple_embedding(text: str, dim: int = 64) -> List[float]:
    """
    Generates a deterministic 64-dimensional feature vector from text.
    In production with pgvector, this uses OpenAI/Gemini embedding APIs.
    """
    clean_text = sanitize_untrusted_content(text)
    vector = [0.0] * dim
    words = clean_text.lower().split()
    for idx, word in enumerate(words):
        hash_val = sum(ord(char) for char in word)
        pos = hash_val % dim
        vector[pos] += 1.0 / (idx + 1)

    # Normalize vector to unit length
    magnitude = math.sqrt(sum(val * val for val in vector))
    if magnitude > 0:
        vector = [val / magnitude for val in vector]
    return vector


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
    """Ranks evidence objects by semantic similarity to a query context."""
    query_vec = generate_simple_embedding(query)
    scored = []
    for item in evidence_list:
        raw_content = f"{item.get('title', '')} {item.get('content', '')}"
        item_vec = generate_simple_embedding(raw_content)
        score = cosine_similarity(query_vec, item_vec)
        # Store sanitized content
        clean_item = dict(item)
        clean_item["content"] = sanitize_untrusted_content(item.get("content", ""))
        scored.append((score, clean_item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]
