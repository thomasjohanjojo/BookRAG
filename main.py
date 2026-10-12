import os
from pypdf import PdfReader

from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, START, END
from langchain_core.tools import StructuredTool
from typing import Annotated, TypedDict, Any
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Import your abstract interfaces
from Interfaces.ChunkerAbstractBaseClass import ChunkerAbstractBaseClass
from Interfaces.EmbedderAbstractBaseClass import EmbedderAbstractBaseClass
from Interfaces.VectorStoreAndRetrieveAbstractBaseClass import VectorStoreAndRetrieveAbstractBaseClass
from Interfaces.GeneratorAbstractBaseClass import GeneratorAbstractBaseClass
from Interfaces.DocumentWriterToolAbstractBaseClass import DocumentWriterToolAbstractBaseClass

# Import your concrete implementations
from chunker import RecursiveSplittingPageChunker
from embedder import MiniLMEmbedder
from VectorStoreAndRetrieve import ChromaDBVectorStoreAndRetrieve
from generator import OllamaGenerator
from AI_Tools.DocxDocumentWriter import DocxDocumentWriter


# Langgraph section
class BookRAGGraph:
    def __init__(self, chunker : ChunkerAbstractBaseClass, embedder : EmbedderAbstractBaseClass, vector_store_and_retrieve : VectorStoreAndRetrieveAbstractBaseClass, generator : GeneratorAbstractBaseClass, document_writer : DocumentWriterToolAbstractBaseClass ):
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store_and_retrieve = vector_store_and_retrieve
        self.generator = generator
        self.document_writer = document_writer

        self.write_to_document_tool = StructuredTool.from_function(
            func = self.document_writer.write_note_to_document,
            name = "write_to_document_tool",
            description = "Creates or opens a Word document (.docx) and writes the given note content to it."
        )

        self.graph = self._build_graph()

    class BookState(TypedDict) :
        """The shared memeory and data schema for the graph."""
        action : str
        pdf_path : str
        querry : str
        retrieved_chunks_and_metadata_tuple : tuple[list[str], list[dict[str, Any]]]
        response_from_llm: str
        # Appendable message history
        messages: Annotated[list, add_messages]

    def ask_user_node(self, state: BookState):
        """Prompts the user to choose an action and collects the necessary input."""
        print("\n" + "="*30)
        print("      SYSTEM MAIN MENU")
        print("="*30)
    
        # Get the user's choice
        choice = input("Would you like to 'ingest' a document or 'query' or 'exit' the system? ").strip().lower()
    
        if choice == "ingest":
            user_pdf_path = input("Please enter the path to the PDF: ").strip()
            return {
                "action": "ingest", 
                "pdf_path": user_pdf_path
            }
        
        elif choice == "query":
            user_question = input("What is your question? ").strip()
            return {
                "action": "query", 
                "querry": user_question
            }
        elif choice == "exit":
            return {
                "action": "exit"
            }
        
        else:
            print("Invalid choice. Defaulting to 'query'...")
            return {
                "action": "query", 
                "querry": "Summarize the document."
            }

    def ingest_node(self, state: BookState):
        """Phase 1: Read the PDF, chunk it, embed it, and store it."""
        print(f"--- Starting Ingestion for {state.get("pdf_path","")} ---")
        
        # Initialize the PDF reader
        reader = PdfReader(state.get("pdf_path", ""))
        pdf_title = os.path.basename(state.get("pdf_path", ""))
        
        all_chunks = []
        all_metadatas = []
        
        # 1. Parse and Chunk (Page by Page)
        print("Chunking document page by page...")
        for i, page in enumerate(reader.pages):
            page_number = i + 1
            text = page.extract_text()
            
            if text: # Ensure the page actually has text
                chunks, metadatas = self.chunker.chunkThisPage(text, page_number, pdf_title)
                all_chunks.extend(chunks)
                all_metadatas.extend(metadatas)
                
        print(f"Generated {len(all_chunks)} total chunks.")
    
        # 2. Embed the Chunks
        print("Generating mathematical embeddings...")
        embeddings = self.embedder.embed(all_chunks)
    
        # 3. Store in ChromaDB
        print("Saving to local vector database...")
        self.vector_store_and_retrieve.storeToVectorDatabase(all_chunks, embeddings, all_metadatas)
        print("--- Ingestion Complete! ---")    
        return {"response_from_llm": "Ingestion complete."}

    def retrieve_node(self, state: BookState):
        print("\nSearching database for relevant context...")
        
        query_embedding = self.embedder.embed([state["querry"]])[0]
        chunks, metadatas = self.vector_store_and_retrieve.retrieveFromVectorDatabase(query_embedding, k=1)
        return {"retrieved_chunks_and_metadata_tuple": (chunks, metadatas)}

    def generate_node(self, state: BookState):
        chunks, metadatas = state["retrieved_chunks_and_metadata_tuple"]
    
        print("\nThinking... (Generating response)")
    
        # 1. Pass the bound tool and current message history to the generator
        tools = [self.write_to_document_tool]
        response_msg = self.generator.generate(
            query=state["querry"],
            chunks=chunks,
            metadatas=metadatas,
            tools=tools,
            messages=state.get("messages", [])
        )
    
        # 2. Extract textual content for display and backwards compatibility
        content_text = response_msg.content if hasattr(response_msg, "content") else str(response_msg)
    
        # 3. Print either the tool call execution or the final response to the terminal
        print("\n" + "=" * 30)
        if getattr(response_msg, "tool_calls", None):
            print("AI ACTION (TOOL CALL):")
            print("=" * 30)
            for tool_call in response_msg.tool_calls:
                print(f"Tool: {tool_call.get('name')}")
                print(f"Arguments: {tool_call.get('args')}")
        else:
            print("AI RESPONSE:")
            print("=" * 30)
            print(content_text)
        print("=" * 30 + "\n")
    
        # 4. Return the message to append to graph history, plus the string fallback
        return {
            "messages": [response_msg],
            "response_from_llm": content_text
        }

    def conditional_routing_after_choice_function(self, state: BookState):
        if(state["action"] == "query") :
            return "retrieve"
        elif(state["action"] == "ingest"):
            return "ingest"
        elif(state["action"] == "exit"):
            return "exit"

    def conditional_routing_after_generate(self, state: BookState):
        """Checks if the last message contains tool calls."""
        messages = state.get("messages", [])
        if messages and getattr(messages[-1], "tool_calls", None):
            return "tools"
        return "ask_user"

    

    def _build_graph(self):
        builder = StateGraph(self.BookState)

        tool_node = ToolNode(tools=[self.write_to_document_tool])

        builder.add_node("ask_user",self.ask_user_node)
        builder.add_node("ingest", self.ingest_node)
        builder.add_node("retrieve", self.retrieve_node)
        builder.add_node("generate", self.generate_node)
        # Add the ToolNode to the graph
        builder.add_node("tools", tool_node)
        # ... add edges and compile ...
        builder.add_edge(START, "ask_user")
        builder.add_edge("ingest", "ask_user")
        builder.add_edge("retrieve", "generate")
        # NEW: After the tool runs, loop back to the generator
        builder.add_edge("tools", "generate")

        # ... conditional edges...
        builder.add_conditional_edges("ask_user", self.conditional_routing_after_choice_function, 
                                      {
                                          "ingest": "ingest",
                                          "retrieve": "retrieve",
                                          "exit": END
                                      })
        builder.add_conditional_edges(
            "generate",
            self.conditional_routing_after_generate,
            {
                "tools": "tools",
                "ask_user": "ask_user"
            }
            )
        
        return builder.compile()


if __name__ == "__main__":
    # Dependency Injection: Instantiate your concrete classes
    print("Initializing RAG components...")
    chunker = RecursiveSplittingPageChunker(chunk_size=500, chunk_overlap=100)
    embedder = MiniLMEmbedder()
    vector_store = ChromaDBVectorStoreAndRetrieve()
    generator = OllamaGenerator() 
    document_writer = DocxDocumentWriter()
    
    # Setting up the graph
    bookRAGGraphObject = BookRAGGraph(chunker= chunker,
                                      embedder= embedder,
                                      vector_store_and_retrieve=vector_store,
                                      generator=generator,
                                      document_writer=document_writer)
    

    # === WORKFLOW TOGGLES ===
    
    # Create an empty initial state to satisfy your BookState TypedDict
    initial_state = {
        "action": "",
        "pdf_path": "",
        "querry": "",
        "retrieved_chunks_and_metadata_tuple": ([], []),
        "response_from_llm": "",
        "messages": []
    }
    
    # Trigger the graph execution
    bookRAGGraphObject.graph.invoke(initial_state)