import unittest
import os
import shutil
from VectorStoreAndRetrieve import ChromaDBVectorStoreAndRetrieve

class TestChromaDBVectorStoreAndRetrieve(unittest.TestCase):
    """Test suite for the ChromaDB Vector Store implementation."""

    def setUp(self):
        """
        Phase 1: The Setup
        Runs BEFORE every single test. Initializes a temporary database path.
        """
        self.test_dir = "./test_chroma_db"
        self.collection_name = "test_collection"
        
        # Initialize our concrete class with the temporary test directory
        self.vector_store = ChromaDBVectorStoreAndRetrieve(
            collection_name=self.collection_name, 
            persist_directory=self.test_dir
        )
        
        # Create minimal dummy data (using small 3D vectors for speed)
        self.chunks = ["Apple is a fruit.", "A dog is a canine animal."]
        self.embeddings = [
            [0.1, 0.1, 0.1],  # Represents "Apple"
            [0.9, 0.9, 0.9]   # Represents "Dog"
        ]
        self.metadatas = [
            {"page_number": 1, "source": "food.pdf"},
            {"page_number": 2, "source": "animals.pdf"}
        ]

    def test_add_and_query_contract(self):
        """
        Phase 2: The Test
        Verifies that data is properly ingested and the closest mathematical match is returned.
        """
        # 1. Ingest the data
        self.vector_store.storeToVectorDatabase(self.chunks, self.embeddings, self.metadatas)
        
        # 2. Create a query vector that is mathematically almost identical to the "Dog" vector
        query_embedding = [0.85, 0.85, 0.85]
        
        # 3. Retrieve the top 1 closest match
        matched_chunks, matched_metadatas = self.vector_store.retrieveFromVectorDatabase(
            query_embedding=query_embedding, 
            k=1
        )
        
        # 4. Assertions to prove our contract holds
        self.assertEqual(len(matched_chunks), 1, "Should return exactly 1 chunk.")
        self.assertEqual(matched_chunks[0], "A dog is a canine animal.", "Should retrieve the semantically closest chunk.")
        self.assertEqual(matched_metadatas[0]["source"], "animals.pdf", "Should retrieve the correct corresponding metadata.")

    def tearDown(self):
        """
        Phase 3: The Cleanup
        Runs AFTER every single test, regardless of whether it passed or failed.
        Wipes the test database off the hard drive.
        """
        # Ignore errors is used here to prevent Windows file-lock permission errors 
        # when deleting directories that were just accessed.
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()