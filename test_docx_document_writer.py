import os
import unittest
from docx import Document

from Interfaces.DocumentWriterToolAbstractBaseClass import DocumentWriterToolAbstractBaseClass
from AI_Tools.DocxDocumentWriter import DocxDocumentWriter
from Abstract_Contract_Test_Classes.test_document_writer_contract import DocumentWriterContractTestSuite


class TestDocxDocumentWriter(DocumentWriterContractTestSuite, unittest.TestCase):
    """
    Concrete test suite for DocxDocumentWriter.
    Inherits all contract assertions and adds python-docx-specific validations.
    """

    def create_writer(self) -> DocumentWriterToolAbstractBaseClass:
        return DocxDocumentWriter()

    def get_file_extension(self) -> str:
        return ".docx"

    # --- Docx-Specific XML Inspections ---

    def test_docx_xml_paragraph_and_heading_structure(self):
        """Specific to python-docx: Verify heading levels and paragraph order."""
        path = self._get_path("docx_structure_test")

        self.writer.write_note_to_document(
            content="Paragraph body text.",
            file_path=path,
            heading="Document Title",
            append=True
        )

        doc = Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

        self.assertEqual(len(paragraphs), 2)
        self.assertEqual(paragraphs[0], "Document Title")
        self.assertEqual(paragraphs[1], "Paragraph body text.")

    def test_docx_append_preserves_earlier_elements(self):
        """Specific to python-docx: Verify multi-entry XML trees persist sequentially."""
        path = self._get_path("docx_multi_entry")

        self.writer.write_note_to_document("Entry 1 content", path, heading="Heading 1", append=True)
        self.writer.write_note_to_document("Entry 2 content", path, heading="Heading 2", append=True)

        doc = Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

        expected = ["Heading 1", "Entry 1 content", "Heading 2", "Entry 2 content"]
        self.assertEqual(paragraphs, expected)


if __name__ == "__main__":
    unittest.main()