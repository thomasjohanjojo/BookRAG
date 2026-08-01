from abc import ABC, abstractmethod
from typing import Any

class VectorStoreAndRetrieveAbstractBaseClass(ABC):
    """Abstract base class for vector database operations."""
    
    @abstractmethod
    def storeToVectorDatabase(
        self, 
        chunks: list[str], 
        embeddings: list[list[float]], 
        metadatas: list[dict[str, Any]]
    ) -> None:
        """
        Ingestion Phase: Saves the text, vectors, and metadata into the database.
        """
        pass

    @abstractmethod
    def retrieveFromVectorDatabase(
        self, 
        query_embedding: list[float], 
        k: int = 3
    ) -> tuple[list[str], list[dict[str, Any]]]:
        """
        Retrieval Phase: Searches the database for the top 'k' closest matches.
        Returns a tuple containing the matching text chunks and their metadata.
        """
        pass