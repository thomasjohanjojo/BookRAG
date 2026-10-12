from abc import ABC, abstractmethod
from typing import Any

class GeneratorAbstractBaseClass(ABC):
    """Abstract interface defining standard LLM generation behavior."""

    @abstractmethod
    def generate(
        self, 
        query: str, 
        chunks: list[str], 
        metadatas: list[dict[str, Any]], 
        tools: list[Any] | None = None, 
        messages: list[Any] | None = None
    ) -> Any:
        """
        Generates an answer or tool call from context.
        
        Args:
            query: The user question.
            chunks: Retrieved context text strings.
            metadatas: Metadata dictionaries corresponding to chunks.
            tools: Optional list of tools bound to the model.
            messages: Optional message history for conversational loops.
        """
        pass