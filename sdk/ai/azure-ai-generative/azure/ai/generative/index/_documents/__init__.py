# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Document parsing and chunking utilities."""
import re
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Iterable, Iterator, List, Optional, Union

from azure.ai.generative.index._documents.chunking import ChunkedDocument, split_documents
from azure.ai.generative.index._documents.cracking import (
    SUPPORTED_EXTENSIONS,
    BaseDocumentLoader,
    DocumentSource,
    crack_documents,
    files_to_document_source,
)
from azure.ai.generative.index._utils.logging import get_logger
from azure.ai.resources._index._documents.document import Document, StaticDocument

logger = get_logger(__name__)


class DocumentChunksIterator(Iterator):
    """Iterate over document chunks."""

    def __init__(
        self,
        files_source: Union[str, Path],
        glob: str,
        base_url: Optional[str],
        document_path_replacement_regex: Optional[Dict[str, str]] = None,
        file_filter: Optional[Callable[[Iterable[DocumentSource]], Iterator[DocumentSource]]] = None,
        source_loader: Callable[[Iterator[DocumentSource], Any], Iterator[ChunkedDocument]] = crack_documents,
        chunked_document_processors: Optional[
            List[Callable[[Iterable[ChunkedDocument]], Iterator[ChunkedDocument]]]
        ] = None,
    ):
        """Initialize a document chunks iterator."""
        self.files_source = files_source
        self.glob = glob
        self.base_url = base_url if base_url else ""
        self.document_path_replacement_regex = document_path_replacement_regex
        if file_filter is None:
            file_filter = self._document_statistics
        self.file_filter = file_filter
        self.source_loader = source_loader

        self.chunked_document_processors = (
            chunked_document_processors
            if chunked_document_processors is not None
            else [lambda docs: split_documents(docs, splitter_args={"chunk_size": 1024, "chunk_overlap": 0})]
        )
        self.document_chunks_iterator: Optional[Iterator[ChunkedDocument]] = None
        self.__document_statistics = None
        self.span = None

    def __iter__(self) -> Iterator[ChunkedDocument]:
        """
        Iterate over document chunks.

        :return: The Iterator object of document chunks.
        :rtype: Iterator[ChunkedDocument]
        """
        if self.document_path_replacement_regex:
            document_path_replacement = self.document_path_replacement_regex
            url_replacement_match = re.compile(document_path_replacement["match_pattern"])

            def process_url(url):
                return url_replacement_match.sub(document_path_replacement["replacement_pattern"], url)

        else:

            def process_url(url):
                return url

        if self.base_url is None:
            self.base_url = self._infer_base_url_from_git(self.files_source)

        source_documents = files_to_document_source(self.files_source, self.glob, self.base_url, process_url)
        if self.file_filter is not None:
            source_documents = self.file_filter(source_documents)
        document_chunks_iterator = self.source_loader(source_documents)  # type: ignore[call-arg]

        if self.chunked_document_processors is not None:
            for chunked_document_processor in self.chunked_document_processors:
                document_chunks_iterator = chunked_document_processor(document_chunks_iterator)

        self.document_chunks_iterator = document_chunks_iterator  # type: ignore[no-redef]

        return self

    def __next__(self) -> ChunkedDocument:
        """
        Get the next document chunk.

        :return: The next document chunk.
        :rtype: ChunkedDocument
        """
        if self.document_chunks_iterator is None:
            raise StopIteration
        # if self.span is None:
        #     self.span = tracer.start_span('DocumentChunksIterator::__next__')
        try:
            return next(self.document_chunks_iterator)
        except StopIteration as e:
            self.document_chunks_iterator = None
            if self.span is not None:
                self.span.end()
            raise StopIteration from e

    def document_statistics(self):
        """
        Provide current statistics about the documents processed by iDocumentChunkIterator.

        **Note:** The statistics only include files which have already been pulled through the iterator,
        calling this before iterating will yield None.
        """
        return self.__document_statistics

    def _document_statistics(  # pylint: disable=dangerous-default-value
        self, sources: Iterable[DocumentSource], allowed_extensions=SUPPORTED_EXTENSIONS
    ) -> Generator[DocumentSource, None, None]:
        """
        Filter out sources with extensions not in allowed_extensions.

        :keyword sources: An iterable of DocumentSource objects.
        :paramtype sources: Iterable[DocumentSource]
        :keyword allowed_extensions: A list of allowed file extensions.
        :paramtype allowed_extensions: List[str]
        :return: A Generator object of filtering out sources with extensions not in allowed_extensions.
        :rtype: Generator[DocumentSource, None, None]
        """
        if self.__document_statistics is None:
            self.__document_statistics = {  # type: ignore
                "total_files": 0,
                "skipped_files": 0,
                "skipped_extensions": {},
                "kept_extensions": {},
            }
        for source in sources:
            source_path: Path = Path(source.path)  # type: ignore[arg-type]
            self.__document_statistics: Dict[str, object]  # type: ignore[no-redef]
            self.__document_statistics["total_files"] += 1  # type: ignore[index]
            if allowed_extensions is not None:
                if source_path.suffix not in allowed_extensions:
                    self.__document_statistics["skipped_files"] += 1  # type: ignore[index]
                    _skipped_extensions = self.__document_statistics["skipped_extensions"]  # type: ignore[index]
                    ext_skipped = _skipped_extensions.get(source_path.suffix.lower(), 0)
                    _skipped_extensions[source_path.suffix.lower()] = ext_skipped + 1
                    logger.debug(f'Filtering out extension "{source_path.suffix.lower()}" source: {source.filename}')
                    continue
            _kept_extensions = self.__document_statistics["kept_extensions"]  # type: ignore[index]
            ext_kept = _kept_extensions.get(source_path.suffix.lower(), 0)
            _kept_extensions[source_path.suffix.lower()] = ext_kept + 1  # type: ignore[index]
            yield source
        logger.info(
            "[DocumentChunksIterator::filter_extensions] "
            + f"Filtered {self.__document_statistics['skipped_files']} files "  # type: ignore[index]
            + f"out of {self.__document_statistics['total_files']}"  # type: ignore[index]
        )
        if self.span is not None:
            self.span.set_attributes({f"document_statistics.{k}": v for k, v in self.__document_statistics.items()})

    @staticmethod
    def _infer_base_url_from_git(files_source: Union[str, Path]) -> Optional[str]:
        """
        Try and infer base_url from git repo remote info if source is in a git repo.

        :keyword files_source: The source directory of file.
        :paramtype files_source: Union[str, Path]
        :return: The inferred base URL.
        :rtype: Optional[str]
        """
        try:
            import git

            repo = git.Repo(str(files_source), search_parent_directories=True)
            remote_url = repo.remote().url
            if remote_url.endswith(".git"):
                remote_url = remote_url[:-4]
            if remote_url.startswith("git@"):
                remote_url = remote_url.replace(":", "/")
                remote_url = remote_url.replace("git@", "https://")

            if "dev.azure.com" in remote_url:
                remote_url = remote_url.replace("https://ssh.dev.azure.com/v3/", "")
                try:
                    parts = remote_url.split("/")
                    org, project, repository = parts[0], parts[1], parts[2]
                    repository = f"https://{org}.visualstudio.com/DefaultCollection/{project}/_git/{repository}"
                    # TODO: url encode `repo.active_branch.name`
                    remote_url = repository + f"?version=GB{repo.active_branch.name}&path="
                except ValueError as e:
                    logger.warning(
                        "Failed to parse org, project and repo from Azure DevOps remote url: "
                        + f"{remote_url}\nbecause: {e}"
                    )
            else:
                # Infer branch from repo
                remote_url = f"{remote_url}/blob/{repo.active_branch.name}"

            return remote_url
        except ImportError:
            return None


__all__ = [
    "BaseDocumentLoader",
    "ChunkedDocument",
    "Document",
    "DocumentChunksIterator",
    "DocumentSource",
    "StaticDocument",
    "SUPPORTED_EXTENSIONS",
    "crack_documents",
    "files_to_document_source",
    "split_documents",
]
