
from ingestion.loader import load_medical_document
from ingestion.chunker import chunk_documents


PDF_PATH = "../data/medical_diagnosis_manual.pdf"


def main():
    # Use only the first two pages for this initial test.
    documents = load_medical_document(PDF_PATH)[:2]

    chunks = chunk_documents(
        documents,
        chunk_size=1000,
        chunk_overlap=150,
    )

    print(f"Pages tested: {len(documents)}")
    print(f"Chunks generated: {len(chunks)}")

    if chunks:
        print("\n--- First Chunk Preview ---")
        print(chunks[0].page_content[:300])

        print("\n--- First Chunk Metadata ---")
        print(chunks[0].metadata)

        assert all(
            len(chunk.page_content) <= 1000
            for chunk in chunks
        ), "A chunk exceeded the configured size."

        print("\nChunking test passed!")


if __name__ == "__main__":
    main()
