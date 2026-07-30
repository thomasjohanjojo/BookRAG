import unittest
from embedder import MiniLMEmbedder 

class TestMiniLMEmbedder(unittest.TestCase):
    
    def setUp(self):
        """Runs once before the tests start to initialize our model."""
        # This will download/load the model into memory
        self.embedder = MiniLMEmbedder()
        
        # Simulating the list[str] output we would get from our chunker
        self.sample_chunks = [
            "This is the first test chunk.",
            "Here is the second test chunk, talking about vectors."
        ]

    def test_embed_contract(self):
        """Verifies that the embedder output strictly matches our interface rules."""
        
        # 1. Execute the embed method
        embeddings = self.embedder.embed(self.sample_chunks)

        # 2. Verify Outer Type: Is it a list?
        self.assertIsInstance(embeddings, list, "The outer structure must be a list.")
        
        # 3. Verify Batching: Did we get exactly 2 vectors back for our 2 chunks?
        self.assertEqual(len(embeddings), len(self.sample_chunks), "Should return exactly one vector per input chunk.")

        # 4. Verify Inner Types and Dimensions
        for vector in embeddings:
            # Is the inner structure a list?
            self.assertIsInstance(vector, list, "Each vector must be a standard Python list.")
            
            # Are there exactly 384 coordinates?
            self.assertEqual(len(vector), 384, "all-MiniLM-L6-v2 must return exactly 384 dimensions.")
            
            # Are the coordinates floating-point numbers?
            self.assertIsInstance(vector[0], float, "The vector coordinates must be floats.")

if __name__ == '__main__':
    # Running this script executes the test
    unittest.main()