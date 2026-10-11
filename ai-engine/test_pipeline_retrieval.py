from vector_store.chroma_store import ChromaVectorStore


def main():
    store = ChromaVectorStore(
        persist_directory="chroma_db_pipeline_test",
        collection_name="mediassist_pipeline_test",
    )

    print("Stored chunks:", store.count())

    results = store.search(
        "medical diagnosis and patient information",
        top_k=2,
    )

    print("\n--- Retrieved Chunks ---")

    for index, result in enumerate(results, start=1):
        print(f"\nResult {index}")
        print("Text:", result["text"][:300])
        print("Metadata:", result["metadata"])
        print("Distance:", round(result["distance"], 4))

    assert store.count() == 2, "Expected two persisted chunks."
    assert len(results) > 0, "No chunks were retrieved."

    print("\nPersistent retrieval test passed!")


if __name__ == "__main__":
    main()