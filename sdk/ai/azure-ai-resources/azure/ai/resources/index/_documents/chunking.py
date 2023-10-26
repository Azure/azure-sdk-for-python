# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Document parsing and chunking utilities."""
import copy
import re
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Iterable, Iterator, List, Optional

from azure.ai.resources.index._documents.document import Document, DocumentSource, StaticDocument
from azure.ai.resources.index._langchain.vendor.text_splitter import TextSplitter
from azure.ai.resources.index._utils import merge_dicts
from azure.ai.resources.index._utils.logging import get_logger, safe_mlflow_log_metric
from azure.ai.resources.index._utils.tokens import tiktoken_cache_dir, token_length_function

logger = get_logger(__name__)


@dataclass
class ChunkedDocument:
    """Chunked Document."""

    chunks: List[Document]
    source: DocumentSource
    metadata: dict

    def __post_init__(self):
        """Post init."""
        self.metadata = merge_dicts(self.metadata, {"source": self.source.get_metadata()})

    @property
    def page_content(self) -> str:
        """Get the page content of the chunked document."""
        return "\n\n".join([chunk.page_content for chunk in self.chunks])

    def get_metadata(self) -> dict:
        """Get the metadata of the chunked document."""
        return self.metadata

    def flatten(self) -> List[Document]:
        """Flatten the chunked document."""
        chunks = []
        for i, chunk in enumerate(self.chunks):
            chunk.metadata["source"]["chunk_id"] = str(i)
            chunks.append(chunk)
        return chunks


@lru_cache(maxsize=1)
def _init_nltk():
    import nltk
    nltk.download("punkt")


def get_langchain_splitter(file_extension: str, arguments: dict) -> TextSplitter:
    """Get a text splitter for a given file extension."""
    use_nltk = False
    if "use_nltk" in arguments:
        use_nltk = arguments["use_nltk"] is True
        del arguments["use_nltk"]
    use_rcts = False
    if "use_rcts" in arguments:
        use_rcts = arguments["use_rcts"] is True
        del arguments["use_rcts"]

    # Handle non-natural language splitters
    if file_extension == ".py":
        from azure.ai.resources.index._langchain.vendor.text_splitter import Language, RecursiveCharacterTextSplitter
        with tiktoken_cache_dir():
            return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                **{
                    **arguments,
                    "encoding_name": "cl100k_base",
                    "separators": RecursiveCharacterTextSplitter.get_separators_for_language(Language.PYTHON),
                    "is_separator_regex": True,
                    "disallowed_special": (),
                    "allowed_special": "all"
                }
            )

    # If configured to use NLTK for splitting on sentence boundaries use that for non-code text formats
    if use_nltk:
        _init_nltk()
        from azure.ai.resources.index._langchain.vendor.text_splitter import NLTKTextSplitter

        return NLTKTextSplitter(
            length_function=token_length_function(),
            **arguments
        )

    # TODO: Support NLTK for splitting text as default?
    # Though want to keep MD specific splitting, only using NLTK on large chunks of plain text.

    # Finally use any text format specific splitters
    formats_to_treat_as_txt_once_loaded = [".pdf", ".ppt", ".pptx", ".doc", ".docx", ".xls", ".xlsx"]
    if file_extension == ".txt" or file_extension in formats_to_treat_as_txt_once_loaded:
        from azure.ai.resources.index._langchain.vendor.text_splitter import TokenTextSplitter

        with tiktoken_cache_dir():
            return TokenTextSplitter(
                encoding_name="cl100k_base",
                length_function=token_length_function(),
                **{**arguments, "disallowed_special": (), "allowed_special": "all"}
            )
    elif file_extension == ".html" or file_extension == ".htm":
        from azure.ai.resources.index._langchain.vendor.text_splitter import TokenTextSplitter

        logger.info("Using HTML splitter.")
        with tiktoken_cache_dir():
            return TokenTextSplitter(
                encoding_name="cl100k_base",
                length_function=token_length_function(),
                **{**arguments, "disallowed_special": (), "allowed_special": "all"}
            )
    elif file_extension == ".md":
        if use_rcts:
            from azure.ai.resources.index._langchain.vendor.text_splitter import MarkdownTextSplitter

            with tiktoken_cache_dir():
                return MarkdownTextSplitter.from_tiktoken_encoder(
                    encoding_name="cl100k_base",
                    **{**arguments, "disallowed_special": (), "allowed_special": "all"}
                )
        else:
            with tiktoken_cache_dir():
                return MarkdownHeaderSplitter.from_tiktoken_encoder(
                    encoding_name="cl100k_base",
                    remove_hyperlinks=True,
                    remove_images=True,
                    **{**arguments, "disallowed_special": (), "allowed_special": "all"}
                )
    else:
        raise ValueError(f"Invalid file_extension: {file_extension}")


file_extension_splitters = {
    # Plain text
    ".txt": lambda **kwargs: get_langchain_splitter(".txt", kwargs),
    ".md": lambda **kwargs: get_langchain_splitter(".md", kwargs),
    ".html": lambda **kwargs: get_langchain_splitter(".html", kwargs),
    ".htm": lambda **kwargs: get_langchain_splitter(".htm", kwargs),
    # Encoded text
    ".pdf": lambda **kwargs: get_langchain_splitter(".pdf", kwargs),
    ".ppt": lambda **kwargs: get_langchain_splitter(".ppt", kwargs),
    ".pptx": lambda **kwargs: get_langchain_splitter(".pptx", kwargs),
    ".doc": lambda **kwargs: get_langchain_splitter(".doc", kwargs),
    ".docx": lambda **kwargs: get_langchain_splitter(".docx", kwargs),
    ".xls": lambda **kwargs: get_langchain_splitter(".xls", kwargs),
    ".xlsx": lambda **kwargs: get_langchain_splitter(".xlsx", kwargs),
    # Code
    ".py": lambda **kwargs: get_langchain_splitter(".py", kwargs),
    # TODO: Fill in other languages supported by RecursiveCharacterTextSplitter
}


def split_documents(documents: Iterable[ChunkedDocument], splitter_args: dict, file_extension_splitters=file_extension_splitters) -> Iterator[ChunkedDocument]:
    """Split documents into chunks."""
    total_time = 0
    total_documents = 0
    total_splits = 0
    log_batch_size = 100
    for i, document in enumerate(documents):
        if len(document.chunks) < 1:
            logger.warning(f"Skipped document with no chunks: {document.source.filename}")
            # TODO: Log this warning to telemetry with document metadata (extension, size, etc.) to get signal for improvements to parsing.
            continue
        file_start_time = time.time()
        total_documents += len(document.chunks)
        if i % log_batch_size == 0:
            safe_mlflow_log_metric("total_source_documents", total_documents, logger=logger, step=int(time.time() * 1000))

        local_splitter_args = splitter_args.copy()

        document_metadata = document.get_metadata()
        chunk_prefix = document_metadata.get("chunk_prefix", "")
        if len(chunk_prefix) > 0:
            if "chunk_size" in local_splitter_args:
                prefix_token_length = token_length_function()(chunk_prefix)
                if prefix_token_length > local_splitter_args["chunk_size"] // 2:
                    chunk_prefix = chunk_prefix[:local_splitter_args["chunk_size"] // 2]
                    # should we update local_splitter_args['chunk_size'] here?
                else:
                    local_splitter_args["chunk_size"] = local_splitter_args["chunk_size"] - prefix_token_length

        if "chunk_prefix" in document_metadata:
            del document_metadata["chunk_prefix"]

        # TODO: Move out as own filter
        chunk_overlap = 0
        if "chunk_overlap" in local_splitter_args:
            chunk_overlap = local_splitter_args["chunk_overlap"]

        def filter_short_docs(chunked_document):
            for doc in chunked_document.chunks:
                doc_len = len(doc.page_content)
                if doc_len < chunk_overlap:
                    logger.info(f"Filtering out doc_chunk shorter than {chunk_overlap}: {chunked_document.source.filename}")
                    continue
                yield doc

        def merge_metadata(chunked_document):
            for chunk in chunked_document.chunks:
                chunk.metadata = merge_dicts(chunk.metadata, document_metadata)
            return chunked_document

        splitter = file_extension_splitters.get(document.source.path.suffix.lower())(**local_splitter_args)
        split_docs = splitter.split_documents(list(filter_short_docs(merge_metadata(document))))

        i = -1
        file_chunks = []
        for chunk in split_docs:
            i += 1
            if "chunk_prefix" in chunk.metadata:
                del chunk.metadata["chunk_prefix"]
            # Normalize line endings to just '\n'
            file_chunks.append(StaticDocument(
                chunk_prefix.replace("\r", "") + chunk.page_content.replace("\r", ""),
                merge_dicts(chunk.metadata, document_metadata),
                document_id=document.source.filename + str(i),
                mtime=document.source.mtime
            ))

        file_pre_yield_time = time.time()
        total_time += file_pre_yield_time - file_start_time
        if len(file_chunks) < 1:
            logger.info("No file_chunks to yield, continuing")
            continue
        total_splits += len(file_chunks)
        if i % log_batch_size == 0:
            safe_mlflow_log_metric("total_chunked_documents", total_splits, logger=logger, step=int(time.time() * 1000))
        document.chunks = file_chunks
        yield document

    safe_mlflow_log_metric("total_source_documents", total_documents, logger=logger, step=int(time.time() * 1000))
    safe_mlflow_log_metric("total_chunked_documents", total_splits, logger=logger, step=int(time.time() * 1000))
    logger.info(f"[DocumentChunksIterator::split_documents] Total time to split {total_documents} documents into {total_splits} chunks: {total_time}")


@dataclass
class MarkdownBlock:
    """Markdown Block."""

    header: Optional[str]
    content: str
    parent: Optional["MarkdownBlock"] = None

    @property
    def header_level(self) -> int:
        """Get the header level of the block."""
        if self.header is None:
            return 0
        return self.header.count("#", 0, self.header.find(" "))


class MarkdownHeaderSplitter(TextSplitter):
    """Split text by markdown headers."""

    def __init__(self, remove_hyperlinks: bool = True, remove_images: bool = True, **kwargs: Any):
        """Initialize Markdown Header Splitter."""
        from azure.ai.resources.index._langchain.vendor.text_splitter import TokenTextSplitter
        self._remove_hyperlinks = remove_hyperlinks
        self._remove_images = remove_images
        with tiktoken_cache_dir():
            self._sub_splitter = TokenTextSplitter(encoding_name="cl100k_base", **kwargs)
        super().__init__(**kwargs)

    def split_text(self, text: str) -> List[str]:
        """Split text into multiple components."""
        blocks = self.get_blocks(text)
        return [block.content for block in blocks]

    def create_documents(
        self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> List[StaticDocument]:
        """Create documents from a list of texts."""
        _metadatas = metadatas or [{}] * len(texts)
        documents = []

        def get_nested_heading_string(md_block):
            nested_headings = []
            current_block = md_block
            while current_block is not None:
                if current_block.header is not None:
                    nested_headings.append(current_block.header)
                current_block = current_block.parent
            return "\n".join(nested_headings[::-1]) if len(nested_headings) > 0 else ""

        for i, text in enumerate(texts):
            for md_block in self.get_blocks(text):
                # TODO: Handle chunk being much smaller than ideal
                # Add to list for concat with other chunk? Make deep linking much harder,
                # could concat sections but still chunk other sections separately if large enough?
                block_nested_headings = get_nested_heading_string(md_block)
                if self._length_function(block_nested_headings + md_block.content) > self._chunk_size:
                    logger.info(f"Splitting section in chunks: {md_block.header}")
                    chunks = [f"{block_nested_headings}\n{chunk}" for chunk in self._sub_splitter.split_text(md_block.content)]
                else:
                    chunks = [f"{block_nested_headings}\n{md_block.content}"]

                metadata = _metadatas[i]
                metadata["markdown_heading"] = {
                    "heading": re.sub(
                        r"#",
                        "",
                        md_block.header if md_block.header is not None else metadata["source"]["filename"]
                    ).strip(),
                    "level": md_block.header_level
                }
                if len(chunks) > 0:
                    for chunk in chunks:
                        new_doc = StaticDocument(
                            chunk, metadata=copy.deepcopy(metadata)
                        )
                        documents.append(new_doc)
        return documents

    def get_blocks(self, markdown_text: str) -> List[MarkdownBlock]:
        """Parse blocks from markdown text."""
        blocks = re.split(r"(^#+\s.*)", markdown_text, flags=re.MULTILINE)
        blocks = [b for b in blocks if b.strip()]

        markdown_blocks = []
        header_stack = []

        if not blocks[0].startswith("#"):
            markdown_blocks.append(MarkdownBlock(header=None, content=blocks[0]))
            blocks = blocks[1:]

        for i in range(0, len(blocks), 2):
            header = blocks[i].strip()
            content = blocks[i + 1].strip() if i + 1 < len(blocks) else ""
            current_block = MarkdownBlock(header=header, content=content)
            header_level = current_block.header_level

            while len(header_stack) > 0 and header_stack[-1][0] >= header_level:
                header_stack.pop()

            parent_block = header_stack[-1][1] if len(header_stack) > 0 else None
            current_block.parent = parent_block

            header_stack.append((header_level, current_block))
            markdown_blocks.append(current_block)

        return markdown_blocks

    @staticmethod
    def _clean_markdown(text: str) -> str:
        # Remove html tags
        # If there's a <!-- comment -->, remove it, otherwise remove each <> pairing
        # TODO: Consider keeping some info from `<img src="img/img_name.PNG" alt="my img desc"/>`?`
        # Finding the image and doing img2text could be useful for linking back to the image,
        # would ideally know the text came from an image to link back to it (or inline it) in a particular way.
        text = re.sub(r"<!-- (.*?)->|<.*?>", "", text)
        # Cleanup whole line comments
        text = re.sub(r"<!-+\s*$", "", text)
        # Strip surrounding whitespace
        text = text.strip()
        return text
