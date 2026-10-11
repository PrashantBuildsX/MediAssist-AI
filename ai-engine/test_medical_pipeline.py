from langchain_core.documents import Document

from vector_store.chroma_store import ChromaVectorStore


def main():
    documents = [
        Document(
            page_content=(
                "Hypertension is persistently elevated blood pressure. "
                "Blood pressure measurements help clinicians assess it."
            ),
            metadata={
                "source": "synthetic_medical_sample",
                "page": 0,
                "chunk_index": 0,
            },
        ),
        Document(
            page_content=(
                "Diabetes affects blood glucose regulation. "
                "Blood glucose testing helps monitor glucose levels."
            ),
            metadata={
                "source": "synthetic_medical_sample",
                "page": 1,
                "chunk_index": 0,
            },
        ),
        Document(
            page_content=(
                "The computer laboratory contains desktop computers "
                "and network equipment."
            ),
            metadata={
                "source": "synthetic_general_sample",
                "page": 0,
                "chunk_index": 0,
            },
        ),
    ]

    store = ChromaVectorStore(
        persist_directory="chroma_db_quality_test",
        collection_name="medical_quality_test",
    )

    store.add_documents(documents)

    query = "Which condition involves persistently high blood pressure?"
    results = store.search(query, top_k=3)

    print("Stored chunks:", store.count())
    print("\nQuery:", query)
    print("\n--- Ranked Results ---")

    for index, result in enumerate(results, start=1):
        print(f"\n{index}. {result['text']}")
        print("Distance:", round(result["distance"], 4))

    assert store.count() == 3
    assert results, "No results returned."
    assert "hypertension" in results[0]["text"].lower(), (
        "Expected hypertension to rank first."
    )

    print("\nMedical retrieval quality test passed!")


if __name__ == "__main__":
    main()