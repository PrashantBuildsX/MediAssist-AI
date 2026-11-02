
from pathlib import Path

from ingestion.web_loader import load_medical_webpage
from ingestion.chunker import chunk_documents
from vector_store.chroma_store import ChromaVectorStore


URL = "https://www.who.int/news-room/fact-sheets/detail/diabetes"

AI_ENGINE_DIR = Path(__file__).resolve().parent
DB_PATH = AI_ENGINE_DIR / "chroma_db_medical_knowledge"
COLLECTION_NAME = "medical_knowledge"


def main():
    print("Step 1: Loading medical webpage...")
    documents = load_medical_webpage(URL)

    print(f"Webpages loaded: {len(documents)}")
    print(f"Source: {documents[0].metadata['source']}")
    print(f"Characters extracted: {len(documents[0].page_content)}")

    print("\nStep 2: Splitting text into chunks...")
    chunks = chunk_documents(
        documents,
        chunk_size=1000,
        chunk_overlap=150,
    )
    print(f"Chunks generated: {len(chunks)}")

    if not chunks:
        raise ValueError("No text chunks were generated.")

    print("\nStep 3: Storing chunks in ChromaDB...")
    store = ChromaVectorStore(
        persist_directory=str(DB_PATH),
        collection_name=COLLECTION_NAME,
    )

    stored = store.add_documents(chunks)

    print(f"Chunks processed: {stored}")
    print(f"Total chunks in collection: {store.count()}")
    print(f"Database directory: {DB_PATH}")
    print(f"Collection: {COLLECTION_NAME}")

    print("\nStep 4: Testing diabetes retrieval...")
    results = store.search(
        query="What are the symptoms and complications of diabetes?",
        top_k=3,
    )

    if not results:
        print("No results retrieved.")
        return

    for index, result in enumerate(results, start=1):
        print(f"\nResult {index}")
        print("Distance:", round(result["distance"], 4))
        print("Source:", result["metadata"].get("source"))
        print("Text:", result["text"][:500])


if __name__ == "__main__":
    main()
