import html
import json
import logging
import re
from typing import IO, Generator, Tuple, Union, NamedTuple

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentTable

from pypdf import PdfReader


logger = logging.getLogger("ingester")


def _table_to_html(table: DocumentTable):
    table_html = "<table>"
    rows = [
        sorted([cell for cell in table.cells if cell.row_index == i], key=lambda cell: cell.column_index)
        for i in range(table.row_count)
    ]
    for row_cells in rows:
        table_html += "<tr>"
        for cell in row_cells:
            tag = "th" if (cell.kind == "columnHeader" or cell.kind == "rowHeader") else "td"
            cell_spans = ""
            if cell.column_span is not None and cell.column_span > 1:
                cell_spans += f" colSpan={cell.column_span}"
            if cell.row_span is not None and cell.row_span > 1:
                cell_spans += f" rowSpan={cell.row_span}"
            table_html += f"<{tag}{cell_spans}>{html.escape(cell.content)}</{tag}>"
        table_html += "</tr>"
    table_html += "</table>"
    return table_html


def _cleanup_data(data: str) -> str:
    """Cleans up the given content using regexes
    Args:
        data: (str): The data to clean up.
    Returns:
        str: The cleaned up data.
    """
    # match two or more newlines and replace them with one new line
    output = re.sub(r"\n{2,}", "\n", data)
    # match two or more spaces that are not newlines and replace them with one space
    output = re.sub(r"[^\S\n]{2,}", " ", output)
    return output.strip()


class Page(NamedTuple):
    page_num: int
    offset: int
    text: str


class TextParser:
    """Parses simple text into a Page object."""

    def __call__(self, content: IO[bytes]) -> Generator[Tuple[int, int, str], None, None]:
        data = content.read()
        decoded_data = data.decode("utf-8")
        text = _cleanup_data(decoded_data)
        yield Page(page_num=0, offset=0, text=text)

class LocalPdfParser:
    """
    Concrete parser backed by PyPDF that can parse PDFs into pages
    To learn more, please visit https://pypi.org/project/pypdf/
    """

    def __call__(self, content: IO[bytes]) -> Generator[Tuple[int, int, str], None, None]:
        # logger.info("Extracting text from '%s' using local PDF parser (pypdf)", content.name)
        reader = PdfReader(content)
        pages = reader.pages
        offset = 0
        for page_num, p in enumerate(pages):
            page_text = p.extract_text()
            yield Page(page_num=page_num, offset=offset, text=page_text)
            offset += len(page_text)


class DocumentAnalysisParser:
    """
    Concrete parser backed by Azure AI Document Intelligence that can parse many document formats into pages
    To learn more, please visit https://learn.microsoft.com/azure/ai-services/document-intelligence/overview
    """

    def __init__(
        self, 
        client: DocumentIntelligenceClient,
        model_id="prebuilt-layout"
    ):
        self.model_id = model_id
        self.client = client

    def __call__(self, content: IO[bytes]) -> Generator[Tuple[int, int, str], None, None]:
        # logger.info("Extracting text from '%s' using Azure Document Intelligence", content.name)
        print("parsing document")
        poller = self.client.begin_analyze_document(
            model_id=self.model_id, analyze_request=content, content_type="application/octet-stream"
        )
        form_recognizer_results = poller.result()
        print("finished parsing")
        offset = 0
        for page_num, page in enumerate(form_recognizer_results.pages):
            tables_on_page = [
                table
                for table in (form_recognizer_results.tables or [])
                if table.bounding_regions and table.bounding_regions[0].page_number == page_num + 1
            ]

            # mark all positions of the table spans in the page
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

            # build page text by replacing characters in table spans with table html
            page_text = ""
            added_tables = set()
            for idx, table_id in enumerate(table_chars):
                if table_id == -1:
                    page_text += form_recognizer_results.content[page_offset + idx]
                elif table_id not in added_tables:
                    page_text += _table_to_html(tables_on_page[table_id])
                    added_tables.add(table_id)

            yield Page(page_num=page_num, offset=offset, text=page_text)
            offset += len(page_text)


class JsonParser:
    """
    Concrete parser that can parse JSON into Page objects. A top-level object becomes a single Page, while a top-level array becomes multiple Page objects.
    """

    def __call__(self, content: IO) -> Generator[Tuple[int, int, str], None, None]:
        offset = 0
        data = json.loads(content.read())
        if isinstance(data, list):
            for i, obj in enumerate(data):
                offset += 1  # For opening bracket or comma before object
                page_text = json.dumps(obj)
                yield Page(page_num=i, offset=offset, text=page_text)
                offset += len(page_text)
        elif isinstance(data, dict):
            yield Page(page_num=0, offset=0, text=json.dumps(data))
