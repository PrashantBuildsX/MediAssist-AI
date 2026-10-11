
from langchain_core.documents import Document


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[Document]:
    """
    Split documents into smaller text chunks while preserving metadata.

    Args:
        documents: List of LangChain Document objects.
        chunk_size: Maximum target size of each chunk, in characters.
        chunk_overlap: Number of overlapping characters between chunks.

    Returns:
        A list of chunked Document objects.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be non-negative and smaller than chunk_size."
        )

    chunks = []

    for document in documents:
        text = document.page_content.strip()

        if not text:
            continue

        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            # Prefer natural text boundaries when possible.
            if end < len(text):
                minimum_end = start + chunk_size // 2
                boundaries = [
                    text.rfind(separator, minimum_end, end)
                    for separator in ("\n\n", "\n", ". ", " ")
                ]
                boundary = max(boundaries)

                if boundary >= minimum_end:
                    end = boundary + 1

            chunk_text = text[start:end].strip()

            if chunk_text:
                metadata = dict(document.metadata)
                metadata["chunk_index"] = chunk_index

                chunks.append(
                    Document(
                        page_content=chunk_text,
                        metadata=metadata,
                    )
                )
                chunk_index += 1

            if end == len(text):
                break

            start = end - chunk_overlap

    return chunks
