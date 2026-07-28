# BookRAG
Just a personal RAG


# Project-Structure
BookRAG/
├── 01_chunker.py
├── 02_embedder.py
├── 03_vector_store.py
├── 04_retriever.py
├── 05_generator.py
└── main.py



# Design principles followed:
The modules all are implementations of interfaces, as per the dependency injection design pattern. 


# Chunker
The chunking strategy followed is Recursive splitting