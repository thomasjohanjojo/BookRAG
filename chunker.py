from Interfaces.ChunkerAbstractBaseClass import ChunkerAbstractBaseClass

class RecursiveSplittingPageChunker(ChunkerAbstractBaseClass):
    """Concrete implementation of Chunker Abstract Base Class that 
    splits a page into smaller chunks recursively based on a specified maximum chunk size."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        # Configuration parameters as instance variables
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Prioritized list of separators
        self.separators = ["\n\n", "\n", ". ", " ",""]


    def chunkThisPage(
        self, text: str, page_number: int, pdf_title: str
    ) -> tuple[list[str], list[dict]]:
        """Splits page text into overlapping chunks and pairs them with metadata.

        Args:
            text: Raw string content from a single PDF page.
            page_number: Integer page number of the PDF.
            pdf_title: Title or filename of the PDF.

        Returns:
            A tuple containing (list_of_chunks, list_of_metadata_dicts).
        """
        if not text or not text.strip():
            return [], []

        # =========================================================================
        # STEP 1: Call the recursive function to break text into atomic snippets
        # =========================================================================
        snippets = self._split_text_recursively(text.strip())

        # =========================================================================
        # STEP 2: Reassemble snippets into overlapping chunks up to self.chunk_size
        # =========================================================================
        chunks: list[str] = []
        proposed_chunk_snippets: list[str] = []
        length_of_proposed_chunk_snippets = 0

        for snippet in snippets:
            snippet_length = len(snippet)

            if length_of_proposed_chunk_snippets + snippet_length <= self.chunk_size:
                proposed_chunk_snippets.append(snippet)
                length_of_proposed_chunk_snippets += snippet_length
            else:
                if proposed_chunk_snippets != []:
                    individual_chunk = "".join(proposed_chunk_snippets).strip() #This line joins all the snippets together into one chunk
                    if individual_chunk:
                        chunks.append(individual_chunk)

                # Collect trailing snippets from the previous chunk for overlap
                overlap_buffer: list[str] = []
                overlap_length = 0

                for prev_snippet in reversed(proposed_chunk_snippets):
                    if overlap_length + len(prev_snippet) <= self.chunk_overlap:
                        overlap_buffer.insert(0, prev_snippet)
                        overlap_length += len(prev_snippet)
                    else:
                        break

                snippet_that_was_too_big = snippet
                proposed_chunk_snippets = overlap_buffer + [snippet_that_was_too_big]
                length_of_proposed_chunk_snippets = sum(len(s) for s in proposed_chunk_snippets)

        # Flush any remaining text in the buffer
        if proposed_chunk_snippets != []:
            leftover_individual_chunk = "".join(proposed_chunk_snippets).strip()
            if leftover_individual_chunk != []:
                chunks.append(leftover_individual_chunk)

        # =========================================================================
        # STEP 3: Pair every chunk string with its metadata dictionary
        # =========================================================================
        metadatas = [
            {"page": page_number, "pdf_title": pdf_title} for _ in chunks
        ]

        return chunks, metadatas

    def _split_text_recursively(self, text: str, separator_index: int = 0) -> list[str]:
        """Recursively splits the text based on the prioritized list of separators."""

        if len(text) <= self.chunk_size:
            return [text] if text else []
        
        if separator_index >= len(self.separators):
            return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]

        current_separator = self.separators[separator_index]
        
        # FIX 1: Prevent crash when separator is ""
        if current_separator == "":
            splits = list(text)
        else:
            splits = text.split(current_separator)

        snippets = []
        for piece in splits:
            # FIX 2: Skip empty strings
            if not piece:
                continue

            # FIX 5: Reattach punctuation for natural readability
            piece_with_sep = piece if current_separator in ["", "\n\n", "\n"] else piece + current_separator

            # FIX 3: Use <= for exact chunk_size matches
            if len(piece_with_sep) <= self.chunk_size:
                snippets.append(piece_with_sep)
            else:
                sub_snippets = self._split_text_recursively(
                    text=piece_with_sep, 
                    separator_index=separator_index + 1
                )
                snippets.extend(sub_snippets)

        return snippets