import argparse
from pathlib import Path

from ingestion.loader import load_medical_document
from ingestion.chunker import chunk_documents
from vector_store.chroma_store import ChromaVectorStore


def main():
    parser = argparse.ArgumentParser(
        description="Ingest a medical PDF into ChromaDB."
    )

    parser.add_argument("pdf_path", help="Path to the input PDF")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum pages to ingest for testing",
    )
    parser.add_argument(
        "--db-path",
        default="chroma_db",
        help="Directory for persistent ChromaDB storage",
    )
    parser.add_argument(
        "--collection",
        default="medical_documents",
        help="Name of the ChromaDB collection",
    )

    args = parser.parse_args()

    if args.max_pages is not None and args.max_pages <= 0:
        parser.error("--max-pages must be greater than zero")

    pdf_path = Path(args.pdf_path)

    print("\nStep 1: Loading PDF...")
    documents = load_medical_document(str(pdf_path))

    if args.max_pages is not None:
        documents = documents[:args.max_pages]

    print(f"Pages selected: {len(documents)}")

    print("\nStep 2: Splitting text into chunks...")
    chunks = chunk_documents(
        documents,
        chunk_size=1000,
        chunk_overlap=150,
    )

    if not chunks:
        raise ValueError(
            "No text chunks were generated. Check the PDF's extracted text."
        )

    print(f"Chunks generated: {len(chunks)}")

    print("\nStep 3: Creating embeddings and storing in ChromaDB...")
    store = ChromaVectorStore(
        persist_directory=args.db_path,
        collection_name=args.collection,
    )

    added = store.add_documents(chunks)

    print(f"Chunks processed: {added}")
    print(f"Total chunks in collection: {store.count()}")
    print(f"Database directory: {Path(args.db_path).resolve()}")

    print("\n--- Sample Stored Chunk ---")
    print(chunks[0].page_content[:300])
    print("\nMetadata:", chunks[0].metadata)

    print("\nPDF ingestion completed successfully!")


if __name__ == "__main__":
    main()