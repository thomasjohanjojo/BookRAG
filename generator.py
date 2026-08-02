import ollama
from typing import Any

# Assuming BaseGenerator is imported from your interfaces.py file
from Interfaces.GeneratorAbstractBaseClass import GeneratorAbstractBaseClass 

class OllamaGenerator(GeneratorAbstractBaseClass):
    """
    Concrete implementation of the Text Generator using a local Ollama model.
    """

    def __init__(self, model_name: str = "llama3.2:1b"):
        self.model_name = model_name
        
        # Test the connection to the local Ollama server during initialization
        try:
            ollama.show(self.model_name)
        except ollama.ResponseError:
            raise ValueError(
                f"Model '{self.model_name}' not found locally. "
                f"Please run 'ollama pull {self.model_name}' in your terminal."
            )

    def generate(self, query: str, chunks: list[str], metadatas: list[dict[str, Any]]) -> str:
        """
        Constructs a citation-aware prompt and generates an answer using a local model.
        """
        # Step 1: Construct the Context Blocks
        context_blocks = []
        
        for chunk, meta in zip(chunks, metadatas):
            source = meta.get("pdf_title", "Unknown Source")
            page = meta.get("page", "Unknown Page")
            
            block = f"[Source: {source} | Page: {page}]\n{chunk}"
            context_blocks.append(block)
            
        full_context = "\n\n".join(context_blocks)
        
        # Step 2: Assemble the Final Prompt
        # Note: Local, smaller models often need more explicit, simple system instructions
        system_instruction = (
            "You are an intelligent reasoning engine. Answer the user's question "
            "using ONLY the provided context below. If the answer cannot be found "
            "in the context, explicitly say 'I cannot answer this based on the provided documents.' "
            "Always cite your sources and page numbers based on the context tags."
        )
        
        user_prompt = f"Context:\n{full_context}\n\nQuestion: {query}"
        
        # Step 3: Send to the local Ollama server
        # We use the chat endpoint which is heavily optimized for these types of instructions
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Extract the string response. 
        # Fallback provided to satisfy the `str` return type in case of an empty response.
        return response.get('message', {}).get('content', '') or "Error: The model returned an empty response."