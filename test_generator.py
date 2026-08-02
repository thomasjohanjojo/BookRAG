import unittest
import os
from typing import Any
# IMPORTANT: Adjust the import below to match your actual file and class name.
# For example, if your file is 05_generator.py and the class is GeminiGenerator:
from generator import OllamaGenerator # Replace with your actual import

class TestGenerator(unittest.TestCase):
    """
    Test suite for the Text Generator component.
    Validates that the generator respects the BaseGenerator contract
    and successfully communicates with the LLM.
    """

    def setUp(self):
        """
        Set up the test environment. Initialize the generator and 
        create dummy retrieved context.
        """
        # Ensure you have your API key set up in your environment or .env file
        # if testing the Gemini Generator.
        
        try:
            self.generator = OllamaGenerator()
        except Exception as e:
            self.fail(f"Failed to initialize the Generator. Check credentials or local model: {e}")

        # Dummy data simulating what the Retriever would hand to the Generator
        self.dummy_query = "What did the astronauts find on the moon?"
        self.dummy_chunks = [
            "Upon landing, the astronauts discovered that the moon's surface was entirely made of green cheese.",
            "The mission commander collected 50 pounds of cheese to bring back to Earth."
        ]
        self.dummy_metadatas = [
            {"pdf_title": "fake_apollo_report.pdf", "page": 42},
            {"pdf_title": "fake_apollo_report.pdf", "page": 43}
        ]

    def test_generate_returns_string(self):
        """
        Tests if the generate method successfully returns a string,
        satisfying the BaseGenerator interface contract.
        """
        result = self.generator.generate(
            query=self.dummy_query,
            chunks=self.dummy_chunks,
            metadatas=self.dummy_metadatas
        )

        # 1. Type Check: Enforce the -> str contract
        self.assertIsInstance(
            result, 
            str, 
            "The generator MUST return a string according to the BaseGenerator contract."
        )

        # 2. Value Check: Ensure the string is not empty
        self.assertGreater(
            len(result), 
            0, 
            "The generated string should not be empty. Check if the LLM returned a response."
        )

        print("\n--- TEST: GENERATED RESPONSE ---")
        print(result)
        print("--------------------------------\n")


if __name__ == '__main__':
    unittest.main()