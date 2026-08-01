import uuid
import chromadb
from typing import Any, cast
from Interfaces.VectorStoreAndRetrieveAbstractBaseClass import VectorStoreAndRetrieveAbstractBaseClass

class ChromaDBVectorStoreAndRetrieve(VectorStoreAndRetrieveAbstractBaseClass):
    """Concrete implementation of the vector store using ChromaDB."""
    
    def __init__(self, collection_name: str = "rag_collection", persist_directory: str = "./chroma_db"):
        """Initializes the ChromaDB client and collection."""
        # Sets up persistent storage to save the index to local disk
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def storeToVectorDatabase(
        self, 
        chunks: list[str], 
        embeddings: list[list[float]], 
        metadatas: list[dict[str, Any]]
    ) -> None:
        """
        Ingestion Phase: Saves the text, vectors, and metadata into the database.
        """
        # ChromaDB requires a unique string ID for every entry
        chunk_ids = [str(uuid.uuid4()) for _ in chunks]
        
        self.collection.add(
            documents=chunks,
            embeddings=cast(Any, embeddings),
            metadatas=cast(Any, metadatas),
            ids=chunk_ids
        )

    def retrieveFromVectorDatabase(
        self, 
        query_embedding: list[float], 
        k: int = 3
    ) -> tuple[list[str], list[dict[str, Any]]]:
        """
        Retrieval Phase: Searches the database for the top 'k' closest matches.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # ChromaDB returns nested lists (batch processing format). 
        # We extract index 0 since we only passed in a single query embedding.
        matched_chunks = results["documents"][0] #type: ignore
        matched_metadatas = results["metadatas"][0] #type: ignore
        
        return matched_chunks, matched_metadatas #type: ignore