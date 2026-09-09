import os
from pypdf import PdfReader

from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, START, END

# Import your abstract interfaces
from Interfaces import ChunkerAbstractBaseClass, EmbedderAbstractBaseClass, VectorStoreAndRetrieveAbstractBaseClass, GeneratorAbstractBaseClass

# Import your concrete implementations
from chunker import RecursiveSplittingPageChunker
from embedder import MiniLMEmbedder
from VectorStoreAndRetrieve import ChromaDBVectorStoreAndRetrieve
from generator import OllamaGenerator

# Langgraph section
class BookRAGGraph:
    def __init__(self, chunker : ChunkerAbstractBaseClass, embedder : EmbedderAbstractBaseClass, vector_store_and_retrieve : VectorStoreAndRetrieveAbstractBaseClass, generator : GeneratorAbstractBaseClass):
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store_and_retrieve = vector_store_and_retrieve
        self.generator = generator
        self.graph = self._build_graph()

    class BookState(TypedDict) :
        """The shared memeory and data schema for the graph."""
        action : str
        pdf_path : str
        querry : str
        retrieved_chunks_and_metadata_tuple : tuple[list[str], list[dict[str, Any]]]
        response_from_llm: str

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
        chunks, metadatas = self.vector_store_and_retrieve.retrieveFromVectorDatabase(query_embedding, k=50)
        return {"retrieved_chunks_and_metadata_tuple": (chunks, metadatas)}

    def generate_node(self, state: BookState):
        chunks, metadatas = state["retrieved_chunks_and_metadata_tuple"]
        
        print("\nThinking... (Generating response)")
        ans = self.generator.generate(state["querry"], chunks, metadatas)
        
        # Print the answer to the terminal!
        print("\n" + "="*30)
        print("AI RESPONSE:")
        print("="*30)
        print(ans)
        print("="*30 + "\n")
        
        return {"response_from_llm": ans}

    def conditional_routing_after_choice_function(self, state: BookState):
        if(state["action"] == "query") :
            return "retrieve"
        elif(state["action"] == "ingest"):
            return "ingest"
        elif(state["action"] == "exit"):
            return "exit"

    def _build_graph(self):
        builder = StateGraph(self.BookState)
        builder.add_node("ask_user",self.ask_user_node)
        builder.add_node("ingest", self.ingest_node)
        builder.add_node("retrieve", self.retrieve_node)
        builder.add_node("generate", self.generate_node)
        # ... add edges and compile ...
        builder.add_edge(START, "ask_user")
        builder.add_edge("ingest", "ask_user")
        builder.add_edge("retrieve", "generate")
        builder.add_edge("generate", "ask_user")
        # ... conditional edges...
        builder.add_conditional_edges("ask_user", self.conditional_routing_after_choice_function, 
                                      {
                                          "ingest": "ingest",
                                          "retrieve": "retrieve",
                                          "exit": END
                                      })
        return builder.compile()


if __name__ == "__main__":
    # Dependency Injection: Instantiate your concrete classes
    print("Initializing RAG components...")
    chunker = RecursiveSplittingPageChunker(chunk_size=500, chunk_overlap=100)
    embedder = MiniLMEmbedder()
    vector_store = ChromaDBVectorStoreAndRetrieve()
    generator = OllamaGenerator() 
    
    # Setting up the graph
    bookRAGGraphObject = BookRAGGraph(chunker= chunker,
                                      embedder= embedder,
                                      vector_store_and_retrieve=vector_store,
                                      generator=generator)
    

    # === WORKFLOW TOGGLES ===
    
    # Create an empty initial state to satisfy your BookState TypedDict
    initial_state = {
        "action": "",
        "pdf_path": "",
        "querry": "",
        "retrieved_chunks_and_metadata_tuple": ([], []),
        "response_from_llm": ""
    }
    
    # Trigger the graph execution
    bookRAGGraphObject.graph.invoke(initial_state)