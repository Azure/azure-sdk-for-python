# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Document parsing and chunking utilities."""
import json
import re
from pathlib import Path
from typing import Callable, Iterable, Iterator, List, Optional, Union

from azure.ai.resources.index._documents.chunking import ChunkedDocument, split_documents
from azure.ai.resources.index._documents.cracking import (
    SUPPORTED_EXTENSIONS,
    BaseDocumentLoader,
    DocumentSource,
    crack_documents,
    files_to_document_source,
)
from azure.ai.resources.index._documents.document import Document, StaticDocument
from azure.ai.resources.index._utils.logging import get_logger

logger = get_logger(__name__)


class DocumentChunksIterator(Iterator):
    """Iterate over document chunks."""

    def __init__(
            self,
            files_source: Union[str, Path],
            glob: str,
            base_url: str = "",
            document_path_replacement_regex: Optional[str] = None,
            file_filter: Optional[Callable[[Iterable[DocumentSource]], Iterator[DocumentSource]]]=None,
            source_loader: Callable[[Iterable[DocumentSource]], Iterator[ChunkedDocument]]=crack_documents,
            chunked_document_processors: Optional[List[Callable[[Iterable[ChunkedDocument]], Iterator[ChunkedDocument]]]] = [
                lambda docs: split_documents(docs, splitter_args={"chunk_size": 1024, "chunk_overlap": 0})
            ]):
        """Initialize a document chunks iterator."""
        self.files_source = files_source
        self.glob = glob
        self.base_url = base_url
        self.document_path_replacement_regex = document_path_replacement_regex
        if file_filter is None:
            file_filter = self._document_statistics
        self.file_filter = file_filter
        self.source_loader = source_loader

        self.chunked_document_processors = chunked_document_processors
        self.document_chunks_iterator = None
        self.__document_statistics = None
        self.span = None

    def __iter__(self) -> Iterator[ChunkedDocument]:
        """Iterate over document chunks."""
        if self.document_path_replacement_regex:
            document_path_replacement = json.loads(self.document_path_replacement_regex)
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
        document_chunks_iterator = self.source_loader(source_documents)

        if self.chunked_document_processors is not None:
            for chunked_document_processor in self.chunked_document_processors:
                document_chunks_iterator = chunked_document_processor(document_chunks_iterator)

        self.document_chunks_iterator = document_chunks_iterator

        return self

    def __next__(self):
        """Get the next document chunk.""."""
        if self.document_chunks_iterator is None:
            raise StopIteration
        # if self.span is None:
        #     self.span = tracer.start_span('DocumentChunksIterator::__next__')
        try:
            return next(self.document_chunks_iterator)
        except StopIteration:
            self.document_chunks_iterator = None
            if self.span is not None:
                self.span.end()
            raise StopIteration

    def document_statistics(self):
        """
        Provide current statistics about the documents processed by iDocumentChunkIterator.

        **Note:** The statistics only include files which have already been pulled through the iterator, calling this before iterating will yield None.
        """
        return self.__document_statistics

    def _document_statistics(self, sources: Iterable[DocumentSource], allowed_extensions=SUPPORTED_EXTENSIONS) -> Iterator[DocumentSource]:
        """Filter out sources with extensions not in allowed_extensions."""
        if self.__document_statistics is None:
            self.__document_statistics = {
                "total_files": 0,
                "skipped_files": 0,
                "skipped_extensions": {},
                "kept_extensions": {}
            }
        for source in sources:
            self.__document_statistics["total_files"] += 1
            if allowed_extensions is not None:
                if source.path.suffix not in allowed_extensions:
                    self.__document_statistics["skipped_files"] += 1
                    ext_skipped = self.__document_statistics["skipped_extensions"].get(source.path.suffix.lower(), 0)
                    self.__document_statistics["skipped_extensions"][source.path.suffix.lower()] = ext_skipped + 1
                    logger.debug(f'Filtering out extension "{source.path.suffix.lower()}" source: {source.filename}')
                    continue
            ext_kept = self.__document_statistics["kept_extensions"].get(source.path.suffix.lower(), 0)
            self.__document_statistics["kept_extensions"][source.path.suffix.lower()] = ext_kept + 1
            yield source
        logger.info(f"[DocumentChunksIterator::filter_extensions] Filtered {self.__document_statistics['skipped_files']} files out of {self.__document_statistics['total_files']}")
        if self.span is not None:
            self.span.set_attributes({
                f"document_statistics.{k}": v for k, v in self.__document_statistics.items()
            })

    @staticmethod
    def _infer_base_url_from_git(files_source: Union[str, Path]) -> Optional[str]:
        """Try and infer base_url from git repo remote info if source is in a git repo."""
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
                    # TODO: url encode `repo.active_branch.name`
                    remote_url = f"https://{org}.visualstudio.com/DefaultCollection/{project}/_git/{repository}?version=GB{repo.active_branch.name}&path="
                except Exception as e:
                    logger.warning(f"Failed to parse org, project and repo from Azure DevOps remote url: {remote_url}\nbecause: {e}")
                    pass
            else:
                # Infer branch from repo
                remote_url = f"{remote_url}/blob/{repo.active_branch.name}"

            return remote_url
        except Exception:
            pass


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
