
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document


ALLOWED_DOMAINS = {
    "www.who.int",
    "who.int",
}


def load_medical_webpage(url: str) -> list[Document]:
    """Extract readable text from an approved medical webpage."""

    parsed_url = urlparse(url)

    if parsed_url.scheme != "https":
        raise ValueError("Only HTTPS URLs are allowed.")

    if parsed_url.hostname not in ALLOWED_DOMAINS:
        raise ValueError("This website is not in the approved domain list.")

    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "MediAssistAI/1.0"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove page elements that are not article content.
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

    main_content = soup.find("main") or soup.find("article") or soup.body

    if main_content is None:
        raise ValueError("No readable webpage content was found.")

    text = main_content.get_text(separator="\n", strip=True)

    if len(text) < 200:
        raise ValueError("The webpage returned too little readable text.")

    return [
        Document(
            page_content=text,
            metadata={
                "source": url,
                "source_type": "webpage",
                "title": soup.title.get_text(strip=True) if soup.title else url,
            },
        )
    ]
