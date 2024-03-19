# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Langchain compatible Docstore which serializes to jsonl."""
from typing import Dict, Union

from langchain.docstore.base import AddableMixin, Docstore  # pylint: disable=import-error
from langchain.docstore.document import Document as LangChainDocument  # pylint: disable=import-error
from azure.ai.generative.index._embeddings import WrappedLangChainDocument
from azure.ai.resources._index._documents import Document  # pylint: disable=import-error
from azure.ai.resources._index._docstore import FileBasedDocstore  # pylint: disable=import-error


class FileBasedDocStore(Docstore, AddableMixin):
    """Simple docstore which serializes to file and loads into memory."""

    def __init__(self, docstore: FileBasedDocstore):
        """Initialize with azure.ai.resources._index._docstore.FileBasedDocstore.

        :param docstore: The FileBasedDocstore instance.
        """
        self.docstore = docstore

    def add(self, texts: Dict[str, LangChainDocument]) -> None:
        """
        Add texts to in memory dictionary.

        :param texts: Dictionary of id -> document.
        :type texts: Dict[str, LangChainDocument]
        :return: None
        :rtype: None
        """
        return self.docstore.add({k: WrappedLangChainDocument(v) for (k, v) in texts.items()})

    def delete(self, ids: list) -> None:
        """
        Deleting IDs from in memory dictionary.

        :param ids: List of IDs to delete.
        :type ids: list
        :return: None
        :rtype: None
        """
        return self.docstore.delete(ids)

    def search(self, search: str) -> Union[LangChainDocument, str]:
        """
        Search via direct lookup.

        :param search: ID of a document to search for.
        :type search: str
        :return: Document if found, else error message.
        :rtype: Union[LangChainDocument, str]
        """
        doc = self.docstore.search(search)
        if isinstance(doc, Document):
            found_doc: Document = doc
            return LangChainDocument(page_content=found_doc.page_content, metadata=found_doc.metadata)
        return doc

    def save(self, output_path: str):
        """
        Save to JSONL file.

        :param output_path: Folder to save docstore contents in.
        :type output_path: str
        :return: None
        :rtype: None
        """
        return self.docstore.save(output_path)

    @classmethod
    def load(cls, input_path: str) -> "FileBasedDocstore":
        """
        Load from JSONL file.

        :param input_path: Path to the JSONL file.
        :type input_path: str
        :return: FileBasedDocstore instance.
        :rtype: FileBasedDocstore
        """
        return FileBasedDocStore.load(input_path)
