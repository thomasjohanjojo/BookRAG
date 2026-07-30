from abc import ABC, abstractmethod

class EmbedderAbstractBaseClass(ABC):
    @abstractmethod
    def embed(self, text_chunks: list[str]) -> list[list[float]]:
        """Converts a list of text chunks into mathematical vector representations."""
        pass