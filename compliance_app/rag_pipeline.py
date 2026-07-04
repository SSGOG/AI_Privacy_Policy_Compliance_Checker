"""
RAG Pipeline: ChromaDB vector store + sentence-transformers embeddings.
Pre-loaded with GDPR and CCPA legal articles for evidence retrieval.
"""

from __future__ import annotations
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline backed by ChromaDB.
    Embeds legal articles using sentence-transformers and retrieves
    the most relevant articles for a given policy clause.
    """

    COLLECTION_PREFIX = "legal_compliance_"

    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        self._client = None
        self._embedder = None
        self._collections: Dict[str, Any] = {}
        self._initialized = False

    def _get_client(self):
        if self._client is None:
            import chromadb
            try:
                self._client = chromadb.PersistentClient(path=self.persist_dir)
            except Exception:
                # Fallback to in-memory if persistence fails
                self._client = chromadb.Client()
        return self._client

    def _get_embedder(self):
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
        return self._embedder

    def _embed(self, texts: List[str]) -> List[List[float]]:
        embedder = self._get_embedder()
        return embedder.encode(texts, show_progress_bar=False).tolist()

    def initialize(self) -> None:
        """Initialize ChromaDB collections and populate with legal articles."""
        if self._initialized:
            return

        from legal_texts import LAW_ARTICLES

        client = self._get_client()

        for law, articles in LAW_ARTICLES.items():
            collection_name = f"{self.COLLECTION_PREFIX}{law.lower()}"

            # Get or create collection
            try:
                collection = client.get_collection(name=collection_name)
                # Check if already populated
                if collection.count() >= len(articles):
                    self._collections[law] = collection
                    continue
                # Delete and recreate if incomplete
                client.delete_collection(name=collection_name)
            except Exception:
                pass

            collection = client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )

            # Build documents for embedding
            docs = []
            for art in articles:
                # Combine title + text + requirement for richer embedding
                doc_text = (
                    f"{art['article']}: {art['title']}. "
                    f"{art['text']} "
                    f"Requirement: {art['requirement']}"
                )
                docs.append(doc_text)

            embeddings = self._embed(docs)

            collection.add(
                ids=[art["id"] for art in articles],
                embeddings=embeddings,
                documents=docs,
                metadatas=[
                    {
                        "law": art["law"],
                        "article": art["article"],
                        "title": art["title"],
                        "text": art["text"],
                        "requirement": art["requirement"],
                    }
                    for art in articles
                ],
            )

            self._collections[law] = collection
            logger.info(f"Loaded {len(articles)} articles for {law}")

        self._initialized = True

    def get_evidence(
        self, clause_text: str, law: str, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the top-k most relevant legal articles for a policy clause.

        Returns a list of dicts with article metadata and similarity score.
        """
        self.initialize()

        collection = self._collections.get(law)
        if collection is None:
            return []

        query_embedding = self._embed([clause_text])

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, collection.count()),
            include=["metadatas", "distances"],
        )

        evidence = []
        if results and results["metadatas"]:
            for meta, dist in zip(
                results["metadatas"][0], results["distances"][0]
            ):
                # Convert cosine distance → similarity (0-1)
                similarity = max(0.0, 1.0 - dist)
                evidence.append(
                    {
                        "article": meta.get("article", ""),
                        "title": meta.get("title", ""),
                        "text": meta.get("text", ""),
                        "requirement": meta.get("requirement", ""),
                        "similarity": round(similarity, 3),
                    }
                )

        return evidence

    def get_all_requirements(self, law: str) -> List[str]:
        """Return all requirement strings for a law (used for classification)."""
        from legal_texts import LAW_ARTICLES
        articles = LAW_ARTICLES.get(law, [])
        return [art["requirement"] for art in articles]
