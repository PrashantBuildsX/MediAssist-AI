
from ingestion.web_loader import load_medical_webpage

url = "https://www.who.int/news-room/fact-sheets/detail/diabetes"

documents = load_medical_webpage(url)

print("Documents loaded:", len(documents))
print("Source:", documents[0].metadata["source"])
print("Extracted characters:", len(documents[0].page_content))
print("\nPreview:\n", documents[0].page_content[:1000])
