from typing import Any
import ollama
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

# Assuming BaseGenerator is imported from your interfaces.py file
from Interfaces.GeneratorAbstractBaseClass import GeneratorAbstractBaseClass 


class OllamaGenerator(GeneratorAbstractBaseClass):
    """
    Concrete implementation of the Text Generator using a local Ollama model.
    """

    def __init__(self, model_name: str = "qwen2.5:3b"):
        self.model_name = model_name
        
        # Test the connection to the local Ollama server during initialization
        try:
            ollama.show(self.model_name)
        except ollama.ResponseError:
            raise ValueError(
                f"Model '{self.model_name}' not found locally. "
                f"Please run 'ollama pull {self.model_name}' in your terminal."
            )

        # Initialize the LangChain chat wrapper for tool calling and message handling
        self.llm = ChatOllama(model=self.model_name, temperature=0)

    def generate(
        self, 
        query: str, 
        chunks: list[str], 
        metadatas: list[dict[str, Any]], 
        tools: list[Any] | None = None, 
        messages: list[Any] | None = None
    ) -> AIMessage:
        """
        Constructs a citation-aware prompt and generates an answer or tool call
        using a local model.
        """
        # Step 1: Construct the Context Blocks
        context_blocks = []
        
        for chunk, meta in zip(chunks, metadatas):
            source = meta.get("pdf_title", "Unknown Source")
            page = meta.get("page", "Unknown Page")
            
            block = f"<source>{source}</source> | <page>{page}</page>\n{chunk}"
            context_blocks.append(block)
            
        full_context = "\n\n".join(context_blocks)
        
        # Step 2: Assemble the Final Prompt
        # Note: Local, smaller models often need more explicit, simple system instructions
        system_instruction = (
            "You are an autonomous AI agent equipped with file-writing tools. "
            "Use the provided context to find information. "
            "If the user asks you to save, write, or export a document, you MUST use the provided tool. "
            "Do NOT output conversational confirmation text when using a tool; just execute the tool directly. "
            "Always cite your sources and page numbers based on the context tags."
        )
        
        user_prompt = f"Context:\n{full_context}\n\nQuestion: {query}"
        
        # Step 3: Bind Tools (if provided)
        bound_llm = self.llm.bind_tools(tools) if tools else self.llm

        # Step 4: Handle Message History
        # If no prior messages exist, construct initial System + Human messages.
        # If returning from a tool run, preserve existing conversation while keeping system rules.
        if not messages:
            conversation = [
                SystemMessage(content=system_instruction),
                HumanMessage(content=user_prompt)
            ]
        else:
            has_system = any(
                isinstance(m, SystemMessage) or (isinstance(m, dict) and m.get("role") == "system") 
                for m in messages
            )
            if not has_system:
                conversation = [SystemMessage(content=system_instruction)] + list(messages)
            else:
                conversation = list(messages)

        # Step 5: Invoke the model
        response: AIMessage = bound_llm.invoke(conversation)
        
        # Fallback in case of an empty text response without any tool calls
        if not response.content and not getattr(response, "tool_calls", None):
            response.content = "Error: The model returned an empty response."

        return response