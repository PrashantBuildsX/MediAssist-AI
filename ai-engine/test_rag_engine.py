from rag_engine import RAGEngine


def main():
    engine = RAGEngine()

    passed = 0
    failed = 0

    def run_test(name, test_function):
        nonlocal passed, failed

        print(f"\nRunning: {name}")

        try:
            test_function()
            passed += 1
            print(f"PASS: {name}")
        except Exception as error:
            failed += 1
            print(f"FAIL: {name}")
            print(f"Reason: {error}")

    def test_relevant_question():
        result = engine.ask("What is hypertension?")

        assert result["answer"].strip(), "Answer should not be empty."
        assert result["sources"], "Expected at least one source."
        assert (
            "hypertension" in result["answer"].lower()
            or "blood pressure" in result["answer"].lower()
        ), "Answer should address hypertension."

    def test_unsupported_question():
        result = engine.ask(
            "What is the recommended treatment for a rare genetic disorder?"
        )

        assert result["sources"] == [], (
            "Unsupported question should return no sources "
            "after relevance filtering."
        )

        assert (
            "could not find sufficiently relevant information"
            in result["answer"].lower()
        ), "Expected the insufficient-context response."

    def test_empty_question():
        try:
            engine.ask("   ")
        except ValueError:
            return

        raise AssertionError("Expected ValueError for an empty question.")

    def test_source_metadata():
        result = engine.ask("What is hypertension?")

        assert result["sources"], "Expected source metadata."

        source = result["sources"][0]

        assert "reference" in source
        assert "source" in source
        assert "page" in source
        assert "distance" in source

    run_test("Relevant question", test_relevant_question)
    run_test("Unsupported question", test_unsupported_question)
    run_test("Empty question", test_empty_question)
    run_test("Source metadata", test_source_metadata)

    print("\n" + "=" * 45)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print("=" * 45)

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()