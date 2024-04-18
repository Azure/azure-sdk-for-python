# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Document Intelligence PDF loader."""

import os
import re
from pathlib import Path
from typing import IO, List

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.ml.entities._indexes.documents import (
    ChunkedDocument,
    Document,
    DocumentSource,
    StaticDocument,
)
from azure.ai.ml.entities._indexes.documents.cracking import BaseDocumentLoader
from azure.ai.ml.entities._indexes.utils.logging import get_logger, version

logger = get_logger("document_intelligence_loader")


class SingletonDocumentIntelligenceClient:
    """Singleton class for FormRecognizerClient."""

    instance = None
    url = None
    key = None

    def __new__(cls, *args, **kwargs):
        """Create a new instance of FormRecognizerClient if not already created."""
        if not cls.instance:
            logger.info("SingletonFormRecognizerClient: Creating instance of FormRecognizerClient per process")

            cls.url = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
            cls.key = os.getenv("DOCUMENT_INTELLIGENCE_KEY")

            if cls.url and cls.key:
                cls.instance = DocumentAnalysisClient(
                    endpoint=cls.url,
                    credential=AzureKeyCredential(cls.key),
                    headers={"x-ms-useragent": f"azureml-rag/{version}"},
                )
            else:
                logger.info(
                    "SingletonFormRecognizerClient: Skipping since credentials not provided. Assuming NO form recognizer extensions(like .pdf) in directory"
                )
                cls.instance = object()  # dummy object
        return cls.instance

    def __getstate__(self):
        """Return the state of the singleton instance."""
        return self.url, self.key

    def __setstate__(self, state):
        """Set the state of the singleton instance."""
        url, key = state
        self.instance = DocumentAnalysisClient(
            endpoint=url,
            credential=AzureKeyCredential(key),
            headers={"x-ms-useragent": f"azureml-rag/{version}"},
        )


class DocumentIntelligencePDFLoader(BaseDocumentLoader):
    """Load PDF files."""

    document_intelligence_client = None
    use_layout = None

    def __init__(self, file: IO, document_source: DocumentSource, metadata: dict = None):
        """Initialize a PDF loader."""
        if file.mode == "r":
            file = file.buffer
        super().__init__(file, document_source, metadata=metadata)

        if DocumentIntelligencePDFLoader.document_intelligence_client is None:
            DocumentIntelligencePDFLoader.document_intelligence_client = SingletonDocumentIntelligenceClient()

        if self.use_layout is None:
            self.use_layout = os.environ.get("AZURE_AI_DOCUMENT_INTELLIGENCE_USE_LAYOUT", "false").lower() == "true"
        logger.info(f"{self.use_layout = }")

    def load_chunked_document(self) -> ChunkedDocument:
        """Load file contents into ChunkedDocument."""
        pages = self.load()
        chunk_prefix = f"Title: {Path(self.document_source.filename).name}"
        document_source = self.document_source
        if self.use_layout:
            # use_layout=True means the pdf structure has been converted to html, so we change the document_source
            # filename suffix to html so the html chunk is used.
            document_source = DocumentSource(
                path=self.document_source.path.with_suffix(".html"),
                filename=self.document_source.filename,
                url=self.document_source.url,
                mtime=self.document_source.mtime,
            )
        return ChunkedDocument(
            chunks=pages,
            source=document_source,
            metadata={**self.metadata, "chunk_prefix": chunk_prefix},
        )

    def load(self) -> List[Document]:
        """Load file contents into Document(s)."""
        import copy

        from azure.ai.ml.entities._indexes.utils import merge_dicts

        page_map = _extract_pdf_content(self.file, self.document_intelligence_client, use_layout=self.use_layout)
        # full_text = "".join([page_text for _, _, page_text in page_map])
        metadata = copy.deepcopy(self.metadata)
        return [
            StaticDocument(
                _cleanup_content(page_text) if self.use_layout else page_text,
                metadata=merge_dicts(metadata, {"source": {"page_number": page_num}}),
            )
            for page_num, _, page_text in page_map
        ]

    @classmethod
    def file_io_mode(self) -> str:
        """Return the file io mode."""
        return "rb"

    def file_extensions(self) -> List[str]:
        """Return the file extensions of the file types to be loaded."""
        return [".pdf"]


PDF_HEADERS = {"title": "h1", "sectionHeading": "h2"}


def _table_to_html(table):
    """Convert a table to html."""
    import html

    table_html = "<table>"
    rows = [
        sorted(
            [cell for cell in table.cells if cell.row_index == i],
            key=lambda cell: cell.column_index,
        )
        for i in range(table.row_count)
    ]
    for row_cells in rows:
        table_html += "<tr>"
        for cell in row_cells:
            tag = "th" if (cell.kind == "columnHeader" or cell.kind == "rowHeader") else "td"
            cell_spans = ""
            if cell.column_span > 1:
                cell_spans += f" colSpan={cell.column_span}"
            if cell.row_span > 1:
                cell_spans += f" rowSpan={cell.row_span}"
            table_html += f"<{tag}{cell_spans}>{html.escape(cell.content)}</{tag}>"
        table_html += "</tr>"
    table_html += "</table>"
    return table_html


def _extract_pdf_content(file, form_recognizer_client, use_layout=False):
    """Extract the content from a PDF file using Form Recognizer."""
    offset = 0
    page_map = []
    model = "prebuilt-layout" if use_layout else "prebuilt-read"
    poller = form_recognizer_client.begin_analyze_document(model, document=file)
    form_recognizer_results = poller.result()

    # (if using layout) mark all the positions of headers
    roles_start = {}
    roles_end = {}
    for paragraph in form_recognizer_results.paragraphs:
        if paragraph.role is not None:
            para_start = paragraph.spans[0].offset
            para_end = paragraph.spans[0].offset + paragraph.spans[0].length
            roles_start[para_start] = paragraph.role
            roles_end[para_end] = paragraph.role

    for page_num, page in enumerate(form_recognizer_results.pages):
        tables_on_page = [
            table for table in form_recognizer_results.tables if table.bounding_regions[0].page_number == page_num + 1
        ]

        # (if using layout) mark all positions of the table spans in the page
        page_offset = page.spans[0].offset
        page_length = page.spans[0].length
        table_chars = [-1] * page_length
        for table_id, table in enumerate(tables_on_page):
            for span in table.spans:
                # replace all table spans with "table_id" in table_chars array
                for i in range(span.length):
                    idx = span.offset - page_offset + i
                    if idx >= 0 and idx < page_length:
                        table_chars[idx] = table_id

        # build page text by replacing characters in table spans with table html and replace the characters corresponding to headers with html headers, if using layout
        page_text = ""
        added_tables = set()
        for idx, table_id in enumerate(table_chars):
            if table_id == -1:
                position = page_offset + idx
                if position in roles_start:
                    role = roles_start[position]
                    if role in PDF_HEADERS:
                        page_text += f"<{PDF_HEADERS[role]}>"
                if position in roles_end:
                    role = roles_end[position]
                    if role in PDF_HEADERS:
                        page_text += f"</{PDF_HEADERS[role]}>"

                page_text += form_recognizer_results.content[page_offset + idx]

            elif table_id not in added_tables:
                page_text += _table_to_html(tables_on_page[table_id])
                added_tables.add(table_id)

        page_text += " "
        page_map.append((page_num, offset, page_text))
        offset += len(page_text)

    # full_text = "".join([page_text for _, _, page_text in page_map])
    return page_map


def _cleanup_content(content: str) -> str:
    """
    Cleans up the given content using RegExes.

    Args:
    ----
        content (str): The content to clean up.

    Returns
    -------
        str: The cleaned up content.

    """
    output = re.sub(r"\n{2,}", "\n", content)
    output = re.sub(r"[^\S\n]{2,}", " ", output)
    output = re.sub(r"-{2,}", "--", output)

    return output.strip()
