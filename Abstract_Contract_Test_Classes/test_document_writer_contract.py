import os
import tempfile
import unittest
from abc import ABC, abstractmethod
from Interfaces.DocumentWriterToolAbstractBaseClass import DocumentWriterToolAbstractBaseClass


class DocumentWriterContractTestSuite(ABC):
    """
    Contract test suite defining required behaviors for ALL document writers.
    Any concrete test suite must inherit this class and implement unittest.TestCase
    """

    @abstractmethod
    def create_writer(self) -> DocumentWriterToolAbstractBaseClass:
        """Factory method returning the writer instance under test."""
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Returns the expected file extension (e.g., '.docx', '.md', '.txt')."""
        pass

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.writer = self.create_writer()

    def tearDown(self):
        self.test_dir.cleanup()

    def _get_path(self, prefix: str) -> str:
        return os.path.join(self.test_dir.name, f"{prefix}{self.get_file_extension()}")

    # --- Standardized Contract Assertions ---

    def test_contract_creates_new_file_with_heading(self):
        """Must create a new file, apply heading, and return a success string."""
        path = self._get_path("note_with_heading")
        result = self.writer.write_note_to_document(
            content="Summary content",
            file_path=path,
            heading="Section 1",
            append=True
        )

        self.assertTrue(os.path.exists(path))
        self.assertIsInstance(result, str)
        self.assertIn("Success", result)
        self.assertIn("Section 1", result)

    def test_contract_creates_new_file_without_heading(self):
        """Must handle optional heading=None gracefully."""
        path = self._get_path("note_no_heading")
        result = self.writer.write_note_to_document(
            content="Plain content without heading",
            file_path=path,
            heading=None,
            append=True
        )

        self.assertTrue(os.path.exists(path))
        self.assertIn("Success", result)

    def test_contract_append_to_existing_file(self):
        """Must append to an existing file when append=True without throwing errors."""
        path = self._get_path("append_note")

        # Initial write
        self.writer.write_note_to_document("First entry", path, heading="H1", append=True)

        # Second write (append)
        result = self.writer.write_note_to_document("Second entry", path, heading="H2", append=True)

        self.assertIn("Success", result)
        self.assertIn("Appended", result)

    def test_contract_overwrite_file(self):
        """Must clear existing file contents when append=False."""
        path = self._get_path("overwrite_note")

        self.writer.write_note_to_document("Old text", path, append=True)
        result = self.writer.write_note_to_document("New text", path, heading="New H1", append=False)

        self.assertIn("Success", result)
        self.assertIn("Created and wrote", result)

    def test_contract_automatic_directory_creation(self):
        """Must create parent directories if passed a nested directory path."""
        nested_path = os.path.join(
            self.test_dir.name, "nested", "subfolder", f"note{self.get_file_extension()}"
        )
        result = self.writer.write_note_to_document("Nested content", nested_path)

        self.assertTrue(os.path.exists(nested_path))
        self.assertIn("Success", result)

    def test_contract_error_handling_does_not_crash(self):
        """Must catch write errors and return an error string rather than crashing."""
        invalid_path = self.test_dir.name  # Target is an existing folder, not a file path

        result = self.writer.write_note_to_document("Content", invalid_path)

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Error:"))