# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Document cracking utilities."""
import json
import re
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import IO, Any, Callable, Iterator, List, Optional, Tuple, Type, Union

from azure.ai.generative.index._documents.chunking import ChunkedDocument, DocumentSource
from azure.ai.generative.index._langchain.vendor.document_loaders.unstructured import UnstructuredFileIOLoader
from azure.ai.generative.index._utils.logging import get_logger, safe_mlflow_log_metric
from azure.ai.resources._index._documents.document import Document, StaticDocument

logger = get_logger(__name__)


# TODO: Should handle uris via fsspec/MLTable
# https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.spec.AbstractFileSystem.glob
def files_to_document_source(
    files_source: Union[str, Path],
    glob: str = "**/*",
    base_url: Optional[str] = None,
    process_url: Optional[Callable[[str], str]] = None,
) -> Iterator[DocumentSource]:
    """
    Convert files to DocumentSource.

    :keyword files_source: The source directory containing the files or a specific file.
    :paramtype files_source: Union[str, Path]
    :keyword glob: The glob pattern to match files within the source directory.
    :paramtype glob: str
    :keyword base_url: The base URL to prepend to each file's path.
    :paramtype base_url: Optional[str]
    :keyword process_url: A function to process the URL before use.
    :paramtype process_url: Optional[Callable[[str], str]]
    :return: A DocumentSource object representing a file.
    :rtype: Iterator[DocumentSource]
    """
    file_source_path = Path(files_source)
    if file_source_path.is_file():
        url: str = base_url  # type: ignore[assignment]
        yield DocumentSource(
            path=file_source_path, filename=file_source_path.name, url=url, mtime=file_source_path.stat().st_mtime
        )
        return
    for file in file_source_path.glob(glob):
        if not file.is_file():
            continue
        relative_path = file.relative_to(files_source)
        url = str(relative_path)
        if base_url:
            url = f"{base_url}/{relative_path}"
        if process_url:
            url = process_url(url)

        yield DocumentSource(path=file, filename=str(relative_path), url=url, mtime=file.stat().st_mtime)


class BaseDocumentLoader(ABC):
    """Base class for document loaders."""

    def __init__(self, file: IO, document_source: DocumentSource, metadata: dict):
        """
        Initialize loader.

        :keyword file: The file object representing the document.
        :paramtype file: IO
        :keyword document_source: The source of the document.
        :paramtype document_source: DocumentSource
        :keyword metadata: Metadata associated with the document.
        :paramtype metadata: dict
        """
        self.file = file
        self.document_source = document_source
        self.metadata = metadata

    def load_chunked_document(self) -> ChunkedDocument:
        """
        Load file contents into ChunkedDocument.

        :return: A ChunkedDocument object representing file contents.
        :rtype: ChunkedDocument
        """
        if "source" in self.metadata:
            if "title" not in self.metadata["source"]:
                self.metadata["source"]["title"] = Path(self.document_source.filename).name
        else:
            self.metadata["source"] = {"title": Path(self.document_source.filename).name}
        pages = self.load()
        return ChunkedDocument(chunks=pages, source=self.document_source, metadata=self.metadata)

    @classmethod
    def file_io_mode(cls) -> str:
        """
        Return the file io mode.

        :return: The file io mode.
        :rtype: str
        """
        return "r"

    @abstractmethod
    def file_extensions(self) -> List[str]:
        """
        Return the file extensions of the file types to be loaded.

        :return: The file extensions of the file types to be loaded.
        :rtype: List[str]
        """

    @abstractmethod
    def load(self) -> List[Document]:
        """
        Load file contents into Document(s).

        :return: A list of Document object representing file contents.
        :rtype: List[Document]
        """


class TextFileIOLoader(BaseDocumentLoader):
    """Load text files."""

    def load(self) -> List[Document]:
        """
        Load file contents into Document.

        :return: A list of Document object representing file contents.
        :rtype: List[Document]
        """
        try:
            text = self.file.read().decode()
        except UnicodeDecodeError:
            self.file.seek(0)
            # Instead of trying to guess the correct text encoding if not 'utf-8', just ignore errors and log a warning
            logger.warning(f"UnicodeDecodeError has been ignored when reading file: {self.document_source.filename}")
            text = self.file.read().decode("utf-8", errors="ignore")

        title, clean_title = extract_text_document_title(text, self.document_source.filename)
        self.metadata = {**self.metadata, "source": {"title": clean_title}}
        chunk_prefix = title + "\n\n"
        self.metadata = {"chunk_prefix": chunk_prefix, **self.metadata}
        return [StaticDocument(data=text, metadata=self.metadata)]

    @classmethod
    def file_io_mode(cls) -> str:
        """
        Return the file io mode.

        :return: The file io mode.
        :rtype: str
        """
        return "rb"

    def file_extensions(self) -> List[str]:
        """
        Return the file extensions of the file types to be loaded.

        :return: The file extensions of the file types to be loaded.
        :rtype: List[str]
        """
        return [".txt", ".md", ".py"]


class UnstructuredHTMLFileIOLoader(UnstructuredFileIOLoader, BaseDocumentLoader):
    """Loader that uses unstructured to load HTML files."""

    def __init__(
        self, file: IO, document_source: DocumentSource, metadata: dict, mode="single", **unstructured_kwargs: Any
    ):
        """
        Initialize a text file loader.

        :keyword file: The file to load.
        :paramtype file: IO
        :keyword document_source: The source of the document.
        :paramtype document_source: DocumentSource
        :keyword metadata: Metadata associated with the document.
        :paramtype metadata: dict
        :keyword mode: The mode of loading.
        :paramtype mode: str
        """
        self.metadata = metadata
        self.document_source = document_source
        super().__init__(file=file, **unstructured_kwargs)

    def load(self) -> List[Document]:
        """
        Load file contents into Documents.

        :return: A list of Document object representing file contents.
        :rtype: List[Document]
        """
        docs = super().load()  # type: ignore[safe-super]
        # TODO: Bug 2878421
        # TODO: Extract html file title and add to metadata
        return [StaticDocument(data=doc.page_content, metadata=doc.metadata) for doc in docs]

    @classmethod
    def file_io_mode(cls) -> str:
        """
        Return the file io mode.

        :return: The file io mode.
        :rtype: str
        """
        return "rb"

    def file_extensions(self) -> List[str]:
        """
        Return the file extensions of the file types to be loaded.

        :return: The file extensions of the file types to be loaded.
        :rtype: List[str]
        """
        return [".html", ".htm"]

    def _get_elements(self) -> List:
        from unstructured.partition.html import partition_html

        return partition_html(file=self.file, **self.unstructured_kwargs)

    def _get_metadata(self):
        return self.metadata


class PDFFileLoader(BaseDocumentLoader):
    """Load PDF files."""

    def load_chunked_document(self) -> ChunkedDocument:
        """
        Load file contents into ChunkedDocument.

        :return: A ChunkedDocument object representing file contents.
        :rtype: ChunkedDocument
        """
        pages = self.load()
        chunk_prefix = f"Title: {Path(self.document_source.filename).name}"
        return ChunkedDocument(
            chunks=pages, source=self.document_source, metadata={**self.metadata, "chunk_prefix": chunk_prefix}
        )

    def load(self) -> List[Document]:
        """
        Load file contents into Document(s).

        :return: A list of Document object representing file contents.
        :rtype: List[Document]
        """
        try:
            from pypdf import PdfReader
        except ImportError:
            try:
                # pylint: disable=import-error
                from PyPDF2 import PdfReader  # type: ignore[no-redef]
            except Exception as e:
                raise RuntimeError("Unable to import pypdf or PyPDF2.") from e

        docs: List[Document] = []
        reader = PdfReader(self.file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text is not None:
                metadata = {"page_number": reader.get_page_number(page), **self.metadata}
                docs.append(StaticDocument(page_text, metadata=metadata))
        if len(docs) == 0:
            msg = f"Unable to extract text from file: {self.document_source.filename} "
            logger.warning(msg + "This can happen if a PDF contains only images.")
        return docs

    @classmethod
    def file_io_mode(cls) -> str:
        """
        Return the file io mode.

        :return: The file io mode.
        :rtype: str
        """
        return "rb"

    def file_extensions(self) -> List[str]:
        """
        Return the file extensions of the file types to be loaded.

        :return: The file extensions of the file types to be loaded.
        :rtype: List[str]
        """
        return [".pdf"]

    @staticmethod
    def fallback_loader() -> Type[BaseDocumentLoader]:
        """
        Return a fallback loader for this loader.

        :return: A fallback loader for this loader.
        :rtype: Type[BaseDocumentLoader]
        """
        return TikaLoader


class TikaLoader(BaseDocumentLoader):
    """Load various unstructured files formats using Apache Tika."""

    def load_chunked_document(self) -> ChunkedDocument:
        """
        Load file contents into ChunkedDocument.

        :return: A ChunkedDocument object representing file contents.
        :rtype: ChunkedDocument
        """
        doc = self.load()
        chunk_prefix = f"Title: {Path(self.document_source.filename).name}"
        return ChunkedDocument(
            chunks=doc, source=self.document_source, metadata={"chunk_prefix": chunk_prefix, **self.metadata}
        )

    def load(self) -> List[Document]:
        """
        Load file content into Document(s).

        :return: A list of Document object representing file contents.
        :rtype: List[Document]
        """
        from tika import parser

        parsed = parser.from_file(self.file)
        content = parsed["content"]
        if content is None:
            logger.warning(f"Unable to extract text from file: {self.document_source.filename}")
            return []

        try:
            text = re.sub(r"\n{3,}", "\n\n", content)
        except TypeError as e:
            if "expected string or bytes-like object" in str(e):
                raise Exception(f"content needs to be of type str but it was of type {type(content)}.") from e
            raise e
        return [StaticDocument(data=text, metadata=self.metadata)]

    @classmethod
    def file_io_mode(cls) -> str:
        """
        Return the file io mode.

        :return: The file io mode.
        :rtype: str
        """
        return "rb"

    def file_extensions(self) -> List[str]:
        """
        Return the file extensions of the file types to be loaded.

        :return: The file extensions of the file types to be loaded.
        :rtype: List[str]
        """
        return [".ppt", ".pptx", ".doc", ".docx", ".xls", ".xlsx"]


def extract_text_document_title(text: str, file_name: str) -> Tuple[str, str]:
    """
    Extract a title from a text document.

    :keyword text: The content of the text document.
    :paramtype text: str
    :keyword file_name: The name of the file.
    :paramtype file_name: str
    :return: A tuple containing the original title extracted and the cleaned title.
    :rtype: Tuple[str, str]
    """
    file_extension = Path(file_name).suffix
    title: Any = None
    if file_extension == ".md":
        heading_0 = re.search(r"#\s.*", text)
        if heading_0:
            title = heading_0.group(0).strip()
            return title, title[2:]

        import markdown  # type: ignore[import]
        from bs4 import BeautifulSoup

        html_content = markdown.markdown(text)
        soup = BeautifulSoup(html_content, "html.parser")
        title = ""
        clean_title = ""
        try:
            title = next(soup.stripped_strings)
            for entry in title.split("\n"):
                if entry.startswith("title") and not entry.startswith("titleSuffix"):
                    clean_title += entry[len("title: ") :].rstrip()
                    break
        except StopIteration:
            title = file_name
        return title, (clean_title if len(clean_title) > 0 else file_name)
    if file_extension == ".py":
        import ast

        def _get_topdocstring(text):
            tree = ast.parse(text)
            docstring = ast.get_docstring(tree)  # returns top docstring
            return docstring

        title = file_name
        try:
            docstring = _get_topdocstring(text)
            if docstring:
                title = f"{file_name}: {docstring}"
        except IOError as e:
            logger.warning(f"Failed to get docstring for {file_name}. Exception message: {e}")

        return f"Title: {title}", title
    if file_extension in {".html", ".htm"}:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(text, "html.parser")
        try:
            title = next(soup.stripped_strings)
        except StopIteration:
            title = file_name
        return f"Title: {title}", title
    first_text_line = None
    title_prefix = "title: "
    for line in text.splitlines():
        if line.startswith(title_prefix):
            title = line[len(title_prefix) :].strip()
            break
        if first_text_line is None and any(c.isalnum() for c in line):
            first_text_line = line.strip()

    if title is None:
        title = first_text_line if first_text_line is not None else file_name

    return f"Title: {title}", title


file_extension_loaders_dict = {
    ".txt": TextFileIOLoader,
    ".md": TextFileIOLoader,
    ".html": UnstructuredHTMLFileIOLoader,
    ".htm": UnstructuredHTMLFileIOLoader,
    ".py": TextFileIOLoader,
    ".pdf": PDFFileLoader,
    ".ppt": TikaLoader,
    ".pptx": TikaLoader,
    ".doc": TikaLoader,
    ".docx": TikaLoader,
    # TODO: we should probably not convert this to text and find a way to keep the table structure
    ".xls": TikaLoader,
    ".xlsx": TikaLoader,
}


SUPPORTED_EXTENSIONS = list(file_extension_loaders_dict.keys())


def crack_documents(sources: Iterator[DocumentSource], file_extension_loaders=None) -> Iterator[ChunkedDocument]:
    """
    Crack documents into chunks.

    :keyword sources: An iterator over document sources.
    :paramtype sources: Iterator[DocumentSource]
    :keyword file_extension_loaders: A dictionary mapping file extensions to loader classes.
    :paramtype file_extension_loaders: Optional[dict]
    :return: An iterator over chunked documents.
    :rtype: Iterator[ChunkedDocument]
    """
    if file_extension_loaders is None:
        file_extension_loaders = file_extension_loaders_dict
    total_time: float = 0.0
    files_by_extension = {str(ext): 0.0 for ext in file_extension_loaders}
    log_batch_size = 100
    for i, source in enumerate(sources):
        file_start_time = time.time()
        assert isinstance(source.path, Path)
        files_by_extension[source.path.suffix.lower()] += 1
        loader_cls = file_extension_loaders.get(source.path.suffix.lower())
        if i % log_batch_size == 0:
            for ext in files_by_extension:
                if files_by_extension[ext] > 0:
                    safe_mlflow_log_metric(ext, files_by_extension[ext], logger=logger, step=int(time.time() * 1000))
        mode = "r"
        if loader_cls is None:
            raise RuntimeError(f"Unsupported file extension '{source.path.suffix}': {source.filename}")

        if hasattr(loader_cls, "file_io_mode"):
            mode = loader_cls.file_io_mode()
        elif loader_cls is TikaLoader or loader_cls is PDFFileLoader or loader_cls is TextFileIOLoader:
            mode = "rb"

        try:
            with open(source.path, mode=mode, encoding="utf-8") as f:
                loader = loader_cls(**{
                    "file": f,
                    "document_source": source,
                    "metadata": {}
                })
                file_pre_yield_time = time.time()
                total_time += file_pre_yield_time - file_start_time
                yield loader.load_chunked_document()
        except Exception as e:  # pylint: disable=broad-except
            # if loader_cls has a fallback_loader, try that
            if hasattr(loader_cls, "fallback_loader"):
                fallback_loader_cls = loader_cls.fallback_loader()
                with open(source.path, mode=mode, encoding="utf-8") as f:
                    loader = fallback_loader_cls(**{
                        "file": f,
                        "document_source": source,
                        "metadata": {}
                    })
                    file_pre_yield_time = time.time()
                    total_time += file_pre_yield_time - file_start_time
                    yield loader.load_chunked_document()
            else:
                raise e

    for ext in files_by_extension:
        if files_by_extension[ext] > 0:
            safe_mlflow_log_metric(ext, files_by_extension[ext], logger=logger, step=int(time.time() * 1000))
    logger.info(
        "[DocumentChunksIterator::crack_documents] "
        + f"Total time to load files: {total_time}\n{json.dumps(files_by_extension, indent=2)}"
    )
