from abc import ABC, abstractmethod
from typing import Optional

class DocumentWriterToolAbstractBaseClass(ABC):
    """Abstract interface for creating, opening, and saving notes to documents."""

    @abstractmethod
    def write_note_to_document(
        self,
        content: str,
        file_path: str,
        heading: Optional[str] = None,
        append: bool = True
    ) -> str:
        """
        Creates or opens a document and writes the given note content.

        Args:
            content (str): The body text of the note to write.
            file_path (str): Path to the document (e.g., 'notes.docx').
            heading (Optional[str]): Optional title or section header.
            append (bool): If True, appends to existing document. If False, overwrites.

        Returns:
            str: A status message confirming the file update or detailing an error.
        """
        pass