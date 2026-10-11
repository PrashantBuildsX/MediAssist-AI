from ingestion.loader import load_medical_document


PDF_PATH = "../data/medical_diagnosis_manual.pdf"


def main():
    documents = load_medical_document(PDF_PATH)

    print(f"Successfully loaded {len(documents)} pages.")

    first_page = documents[0]

    print("\n--- First Page Preview ---")
    print(first_page.page_content[:500])

    print("\n--- First Page Metadata ---")
    print(first_page.metadata)


if __name__ == "__main__":
    main()