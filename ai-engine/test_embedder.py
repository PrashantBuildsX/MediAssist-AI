
from embeddings.embedder import TextEmbedder


def main():
    texts = [
        "The patient has a history of high blood pressure.",
        "The patient previously experienced hypertension.",
        "The hospital building is located near the main road.",
    ]

    embedder = TextEmbedder()
    vectors = embedder.embed_texts(texts)

    print("Number of input texts:", len(texts))
    print("Embedding shape:", vectors.shape)

    # Verify the output dimensions.
    assert vectors.shape == (3, 384)

    # Verify that embeddings are normalized.
    norms = (vectors ** 2).sum(axis=1) ** 0.5
    assert np.allclose(norms, 1.0, atol=1e-5)

    print("\nEmbedding test passed!")


if __name__ == "__main__":
    import numpy as np
    main()
