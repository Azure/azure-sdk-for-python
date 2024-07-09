# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Not all of this file has been vendor, just the parts we use.
# Last Sync: 2023-08-24
# Commit: 3e5cda3405ec1aa369fe90253d88f3e26a03db10
"""Abstract interface for document loader implementations."""
from abc import ABC, abstractmethod
from typing import Iterator, List, Optional

from azure.ai.resources._index._langchain.vendor.schema.document import Document
from azure.ai.resources._index._langchain.vendor.text_splitter import RecursiveCharacterTextSplitter, TextSplitter


class BaseLoader(ABC):
    """Interface for Document Loader.

    Implementations should implement the lazy-loading method using generators
    to avoid loading all Documents into memory at once.

    The `load` method will remain as is for backwards compatibility, but its
    implementation should be just `list(self.lazy_load())`.
    """

    # Sub-classes should implement this method
    # as return list(self.lazy_load()).
    # This method returns a List which is materialized in memory.
    @abstractmethod
    def load(self) -> List[Document]:
        """Load data into Document objects."""

    def load_and_split(self, text_splitter: Optional[TextSplitter] = None) -> List[Document]:
        """Load Documents and split into chunks. Chunks are returned as Documents.

        :param text_splitter: TextSplitter instance to use for splitting documents.
            Defaults to RecursiveCharacterTextSplitter.
        :type text_splitter: Optional[TextSplitter]
        :return: List of Documents.
        :rtype: List[Document]
        """
        if text_splitter is None:
            _text_splitter: TextSplitter = RecursiveCharacterTextSplitter()
        else:
            _text_splitter = text_splitter
        docs = self.load()
        return _text_splitter.split_documents(docs)

    # Attention: This method will be upgraded into an abstractmethod once it's
    #            implemented in all the existing subclasses.
    def lazy_load(self) -> Iterator[Document]:
        """A lazy loader for Documents.

        :return: An iterator of Document objects.
        :rtype: Iterator[Document]
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not implement lazy_load()")
