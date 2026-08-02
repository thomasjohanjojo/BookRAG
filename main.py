import os
from pypdf import PdfReader

# Import your abstract interfaces
from Interfaces import ChunkerAbstractBaseClass, EmbedderAbstractBaseClass, VectorStoreAndRetrieveAbstractBaseClass, GeneratorAbstractBaseClass

# Import your concrete implementations
from chunker import RecursiveSplittingPageChunker
from embedder import MiniLMEmbedder
from VectorStoreAndRetrieve import ChromaDBVectorStoreAndRetrieve
from generator import OllamaGenerator
# from 05_generator import OllamaGenerator # Swap this in if you updated your NVIDIA drivers!

def ingest_document(pdf_path: str, chunker: ChunkerAbstractBaseClass, embedder: EmbedderAbstractBaseClass, vector_store_and_retrieve: VectorStoreAndRetrieveAbstractBaseClass):
    """Phase 1: Read the PDF, chunk it, embed it, and store it."""
    print(f"--- Starting Ingestion for {pdf_path} ---")
    
    # Initialize the PDF reader
    reader = PdfReader(pdf_path)
    pdf_title = os.path.basename(pdf_path)
    
    all_chunks = []
    all_metadatas = []
    
    # 1. Parse and Chunk (Page by Page)
    print("Chunking document page by page...")
    for i, page in enumerate(reader.pages):
        page_number = i + 1
        text = page.extract_text()
        
        if text: # Ensure the page actually has text
            chunks, metadatas = chunker.chunkThisPage(text, page_number, pdf_title)
            all_chunks.extend(chunks)
            all_metadatas.extend(metadatas)
            
    print(f"Generated {len(all_chunks)} total chunks.")

    # 2. Embed the Chunks
    print("Generating mathematical embeddings...")
    embeddings = embedder.embed(all_chunks)

    # 3. Store in ChromaDB
    print("Saving to local vector database...")
    vector_store_and_retrieve.storeToVectorDatabase(all_chunks, embeddings, all_metadatas)
    print("--- Ingestion Complete! ---")


def query_system(question: str, embedder: EmbedderAbstractBaseClass, vector_store: VectorStoreAndRetrieveAbstractBaseClass, generator: GeneratorAbstractBaseClass) -> str:
    """Phase 2: Embed the question, retrieve context, and generate an answer."""
    print(f"\nUser Question: {question}")
    
    # 1. Embed the Question
    print("Embedding user query...")
    query_embedding = embedder.embed([question])[0] # Pull the first (and only) vector

    # 2. Retrieve Relevant Context
    print("Retrieving context from database...")
    retrieved_chunks, retrieved_metadatas = vector_store.retrieveFromVectorDatabase(query_embedding, k=3)
    
    # 3. Generate Citation-Aware Answer
    print("Generating answer...\n")
    answer = generator.generate(question, retrieved_chunks, retrieved_metadatas)
    
    return answer

if __name__ == "__main__":
    # Dependency Injection: Instantiate your concrete classes
    print("Initializing RAG components...")
    chunker = RecursiveSplittingPageChunker(chunk_size=500, chunk_overlap=100)
    embedder = MiniLMEmbedder()
    vector_store = ChromaDBVectorStoreAndRetrieve()
    generator = OllamaGenerator() 
    
    # === WORKFLOW TOGGLES ===
    
    # Step A: Provide a path to a real PDF on your computer
    sample_pdf_path = "samplePath.pdf" 
    
    # Toggle 1: Run this ONCE to ingest the document. 
    # Comment it out after running it so you don't keep re-saving the same data!
    # ingest_document(sample_pdf_path, chunker, embedder, vector_store)
    
    # Toggle 2: Run this whenever you want to ask a question.
    user_question = "What are the main concepts discussed in this document?"
    final_answer = query_system(user_question, embedder, vector_store, generator)
    
    print("\n=== FINAL ANSWER ===")
    print(final_answer)