# BookRAG
Just a personal RAG


# Project-Structure
BookRAG/
chunker.py
embedder.py
vector_store.py
retriever.py
generator.py
main.py
test_chunker.py
/Interfaces
ChunkerAbstractBaseClass.py
EmbedderAbstractBaseClass.py



# Design principles followed:
The modules all are implementations of interfaces, as per the dependency injection design pattern. 


# Chunker
The chunking strategy followed is Recursive splitting