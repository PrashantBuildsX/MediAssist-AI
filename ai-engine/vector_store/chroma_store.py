from pathlib import Path

import chromadb

from embeddings.embedder import TextEmbedder


class ChromaVectorStore:
    """Store and retrieve text chunks using ChromaDB."""

    def __init__(
        self,
        persist_directory: str = "chroma_db",
        collection_name: str = "medical_documents",
        embedder: TextEmbedder | None = None,
    ):
        self.persist_directory = str(Path(persist_directory).resolve())
        self.embedder = embedder or TextEmbedder()

        self.client = chromadb.PersistentClient(
            path=self.persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "MediAssist AI medical document chunks"},
        )

    def add_documents(self, documents) -> int:
        """Embed and store document chunks. Return the number added."""
        if not documents:
            return 0

        texts = [document.page_content for document in documents]

        if any(not text.strip() for text in texts):
            raise ValueError("Documents must not contain empty text.")

        embeddings = self.embedder.embed_texts(texts)

        # Use deterministic IDs so rerunning the same ingestion
        # does not create duplicate entries.
        ids = []
        for index, document in enumerate(documents):
            metadata = document.metadata
            source = str(metadata.get("source", "unknown"))
            page = metadata.get("page", "unknown")
            chunk_index = metadata.get("chunk_index", index)

            ids.append(f"{source}::page_{page}::chunk_{chunk_index}")

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=[
                {
                    key: value
                    for key, value in document.metadata.items()
                    if value is not None
                    and isinstance(value, (str, int, float, bool))
                }
                for document in documents
            ],
        )

        return len(documents)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Return the most relevant stored chunks for a query."""
        if not query.strip():
            raise ValueError("Query must not be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if self.collection.count() == 0:
            return []

        query_embedding = self.embedder.embed_texts([query])

        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        matches = []

        for index, text in enumerate(results["documents"][0]):
            matches.append(
                {
                    "text": text,
                    "metadata": results["metadatas"][0][index],
                    "distance": results["distances"][0][index],
                }
            )

        return matches

    def count(self) -> int:
        """Return the number of chunks currently stored."""
        return self.collection.count()