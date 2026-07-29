from abc import ABC, abstractmethod
class ChunkerAbstractBaseClass(ABC):
    """ Interface for the chunker. """

    @abstractmethod
    def chunkThisPage(self, text: str, page_number: int, pdf_title: str) -> tuple[list[str], list[dict]]:
        """ Splits each page into smaller chunks of text with the associated page number and title"""
        pass
