# BookRAG
A minimalist RAG pipeline for querying PDF books. It will also:
    - Write the results of a query into a docx file


# Project-Structure
BookRAG/
chunker.py
embedder.py
vectorStoreAndRetrieve.py
generator.py
main.py.
//TESTS
test_chunker.py
test_embedder.py
test_vectorStoreAndRetrieve.py
test_generator.py
/Interfaces
ChunkerAbstractBaseClass.py
EmbedderAbstractBaseClass.py
VectorStoreAndRetrieveAbstractBaseClass.py
GeneratorAbstractBaseClass.py



# Design principles followed:
The modules all are implementations of interfaces, as per the dependency injection design pattern. 


# Chunker
The chunking strategy followed is Recursive splitting

# Ollama 
Since we are using Ollama as the llm, make sure to download and install ollama. 


# HOW TO RUN:
To run the application, run the batch file: run_rag.bat. Make sure that ollama is properly installed and set up
