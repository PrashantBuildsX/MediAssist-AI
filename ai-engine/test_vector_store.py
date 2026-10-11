from langchain_core.documents import Document

from vector_store.chroma_store import ChromaVectorStore


def main():
    # Use synthetic sample text for testing; no real patient records.
    documents = [
        Document(
            page_content=(
                "Hypertension is a condition involving persistently "
                "elevated blood pressure."
            ),
            metadata={"source": "sample_medical_text", "page": 0, "chunk_index": 0},
        ),
        Document(
            page_content=(
                "Diabetes is a disease characterized by problems "
                "regulating blood glucose."
            ),
            metadata={"source": "sample_medical_text", "page": 1, "chunk_index": 0},
        ),
        Document(
            page_content=(
                "Regular maintenance helps keep a computer running properly."
            ),
            metadata={"source": "sample_general_text", "page": 0, "chunk_index": 0},
        ),
    ]

    store = ChromaVectorStore(
        persist_directory="chroma_db_test",
        collection_name="mediassist_test",
    )

    added = store.add_documents(documents)

    print("Chunks processed:", added)
    print("Total chunks in database:", store.count())

    results = store.search(
        "What condition causes high blood pressure?",
        top_k=2,
    )

    print("\n--- Search Results ---")
    for index, result in enumerate(results, start=1):
        print(f"\nResult {index}")
        print("Text:", result["text"])
        print("Metadata:", result["metadata"])
        print("Distance:", round(result["distance"], 4))

    assert store.count() == 3, "Expected three stored chunks."
    assert len(results) == 2, "Expected two search results."

    print("\nVector store test passed!")


if __name__ == "__main__":
    main()