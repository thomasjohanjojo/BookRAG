from chunker import RecursiveSplittingPageChunker

def test_chunker_execution():
    # 1. Instantiate chunker with a small chunk_size (e.g., 200 chars)
    # Using smaller sizes during testing makes boundary splits easy to inspect.
    chunker = RecursiveSplittingPageChunker(chunk_size=200, chunk_overlap=120)

    # 2. Prepare sample text representing a page from a PDF
    sample_page_text = """
    Retrieval-Augmented Generation (RAG) is an architectural pattern that improves the accuracy of Large Language Models by fetching relevant document snippets.

    When processing text, recursive splitting attempts to break text at paragraph boundaries first. If a paragraph is larger than the chunk size limit, it falls back to sentence boundaries or word spaces.

    This guarantees that complete thoughts remain intact within the vector store, preventing degraded retrieval performance.
    """.strip()

    # 3. Execute the chunking function
    chunks, metadatas = chunker.chunkThisPage(
        text=sample_page_text,
        page_number=1,
        pdf_title="rag_architecture_guide.pdf",
    )

    # 4. Print overall summary
    print(f"Total Chunks Generated: {len(chunks)}\n")
    print("=" * 70)

    # 5. Inspect each chunk and its corresponding metadata
    for index, (chunk_str, meta) in enumerate(zip(chunks, metadatas), start=1):
        print(f"Chunk #{index} | Length: {len(chunk_str)} characters")
        print(f"Metadata : {meta}")
        print(f"Content  :\n{chunk_str}")
        print("-" * 70)


if __name__ == "__main__":
    test_chunker_execution()

