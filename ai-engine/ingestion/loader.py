
from pathlib import Path

import pymupdf
from langchain_core.documents import Document


def load_medical_document(pdf_path: str) -> list[Document]:
    """
    Load a medical PDF and return its pages as LangChain Documents.

    Args:
        pdf_path: Path to the medical PDF.

    Returns:
        A list of LangChain Document objects.

    Raises:
        FileNotFoundError: If the PDF does not exist.
        ValueError: If the file is not a PDF or contains no pages.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"Medical PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, received: {path.suffix}")

    documents = []

    with pymupdf.open(str(path)) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            documents.append(
                Document(
                    page_content=page.get_text(),
                    metadata={
                        "source": str(path.resolve()),
                        "page": page_number - 1,
                    },
                )
            )

    if not documents:
        raise ValueError("The PDF was loaded, but no pages were found.")

    return documents
