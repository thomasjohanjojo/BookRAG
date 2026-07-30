from sentence_transformers import SentenceTransformer
from Interfaces.EmbedderAbstractBaseClass import EmbedderAbstractBaseClass

class MiniLMEmbedder(EmbedderAbstractBaseClass):
    """
    Concrete implementation of the embedder using the local all-MiniLM-L6-v2 model.
    """
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed(self, text_chunks: list[str]) -> list[list[float]]:
        """
        Takes a list of text chunks and returns their mathematical vector representations.
        """
        
        embeddings_in_numpy_datatype = self.model.encode(text_chunks)
        
        # 3. Convert the resulting numpy.ndarray to a standard Python list of lists
        embeddings_in_list_format = embeddings_in_numpy_datatype.tolist()
        
        return embeddings_in_list_format