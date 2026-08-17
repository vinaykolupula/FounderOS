"""
Scoped Notebook Memory & Fact Indexing Service

Inspired by Y Combinator QM's memory architecture (notebook.ts & memory-service.ts):
1. Stores durable, line-oriented institutional facts and founder learnings.
2. Uses SHA-256 revision tokens for optimistic concurrency and point-in-time rollbacks.
3. Automatically applies sliding-window memory caps (300 facts max) and date stamping.
"""

import hashlib
import datetime
from typing import List, Dict, Any, Optional, Tuple

MAX_FACTS = 300
MEMORY_HEADER = "# FounderOS Institutional Memory\n"


def compute_revision_token(content: str) -> str:
    """Computes a unique SHA-256 hash for memory state versioning."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class NotebookMemoryService:
    """
    Manages structured, durable memory facts for the startup workspace.
    """

    @staticmethod
    def fold_capture(existing_content: str, new_facts: List[str], author: str = "FounderOS") -> Tuple[str, int, str]:
        """
        Folds new facts into the notebook memory body with date stamps, duplicate suppression,
        and sliding-window fact capping. Returns (new_content, added_count, revision_token).
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Clean and sanitize incoming facts
        clean_facts = []
        for fact in new_facts:
            f = fact.strip().lstrip("-* ").strip()
            if f:
                clean_facts.append(f)

        if not clean_facts:
            rev = compute_revision_token(existing_content)
            return existing_content, 0, rev

        # Parse existing facts to avoid duplicate entries
        existing_lines = [line.strip() for line in existing_content.splitlines() if line.strip().startswith("-")]
        seen_facts = set(line.lower() for line in existing_lines)

        added = []
        for f in clean_facts:
            entry = f"- ({today}) {f} [logged_by: {author}]"
            if entry.lower() not in seen_facts:
                seen_facts.add(entry.lower())
                added.append(entry)

        if not added:
            rev = compute_revision_token(existing_content)
            return existing_content, 0, rev

        # Construct updated memory body
        base_body = existing_content.strip()
        if not base_body or not base_body.startswith("#"):
            base_body = MEMORY_HEADER

        updated_body = f"{base_body}\n" + "\n".join(added)

        # Enforce 300 facts maximum limit (dropping oldest facts when limit exceeded)
        lines = updated_body.splitlines()
        fact_indices = [i for i, line in enumerate(lines) if line.strip().startswith("-")]
        
        if len(fact_indices) > MAX_FACTS:
            overflow_count = len(fact_indices) - MAX_FACTS
            drop_indices = set(fact_indices[:overflow_count])
            lines = [line for i, line in enumerate(lines) if i not in drop_indices]
            updated_body = "\n".join(lines)

        revision_token = compute_revision_token(updated_body)
        return updated_body, len(added), revision_token

    @staticmethod
    def query_facts(memory_content: str, search_query: str, limit: int = 10) -> List[str]:
        """Queries institutional facts matching keyword search terms."""
        terms = [t.lower() for t in search_query.split() if t.strip()]
        if not terms:
            return []

        results = []
        for line in memory_content.splitlines():
            if line.strip().startswith("-"):
                line_lower = line.lower()
                if all(term in line_lower for term in terms):
                    results.append(line.strip())
                    if len(results) >= limit:
                        break

        return results
