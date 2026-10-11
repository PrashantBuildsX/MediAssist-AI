
from sentence_transformers import SentenceTransformer
import numpy as np


class TextEmbedder:
    """Generate semantic embeddings for text using Sentence Transformers."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """
        Convert text strings into normalized embedding vectors.

        Returns:
            A NumPy array with shape (number_of_texts, 384).
        """
        if not texts:
            raise ValueError("At least one text is required.")

        if any(not text.strip() for text in texts):
            raise ValueError("Text inputs must not be empty.")

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embeddings
