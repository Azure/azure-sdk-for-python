# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Langchain compatible Docstore which serializes to jsonl."""
from typing import Dict, Union

from azure.ai.generative.index._docstore import FileBasedDocstore
from azure.ai.generative.index._embeddings import WrappedLangChainDocument
from langchain.docstore.base import AddableMixin, Docstore
from langchain.docstore.document import Document as LangChainDocument


class FileBasedDocStore(Docstore, AddableMixin):
    """Simple docstore which serializes to file and loads into memory."""

    def __init__(self, docstore: FileBasedDocstore):
        """Initialize with azure.ai.generative.index._docstore.FileBasedDocstore."""
        self.docstore = docstore

    def add(self, texts: Dict[str, LangChainDocument]) -> None:
        """
        Add texts to in memory dictionary.

        Args:
        ----
            texts: dictionary of id -> document.

        Returns:
        -------
            None
        """
        return self.docstore.add({k: WrappedLangChainDocument(v) for (k, v) in texts.items()})

    def delete(self, ids: list) -> None:
        """Deleting IDs from in memory dictionary."""
        return self.docstore.delete(ids)

    def search(self, search: str) -> Union[LangChainDocument, str]:
        """
        Search via direct lookup.

        Args:
        ----
            search: id of a document to search for.

        Returns:
        -------
            Document if found, else error message.
        """
        doc = self.docstore.search(search)
        return LangChainDocument(page_content=doc.page_content, metadata=doc.metadata) if doc else doc

    def save(self, output_path: str):
        """
        Save to JSONL file.

        Args:
        ----
            output_path: folder to save doctore contents in.
        """
        return self.docstore.save(output_path)

    @classmethod
    def load(cls, input_path: str) -> "FileBasedDocstore":
        """Load from JSONL file."""
        return FileBasedDocStore.load(input_path)
