# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Document abstraction."""
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

import mmh3
from azure.ai.resources.index._utils.tokens import token_length_function


@dataclass
class DocumentSource:
    """Document Source."""

    path: str
    filename: str
    url: str
    mtime: float

    def __post_init__(self):
        """Normalize path and url to use forward slashes."""
        self.filename = self.filename.replace("\\", "/")
        if self.url.startswith("file://"):
            self.url = self.url.replace("\\", "/")

    def get_metadata(self) -> dict:
        """Get the metadata of the document source."""
        return {
            "filename": self.filename,
            "url": self.url,
            "mtime": self.mtime,
        }


class Document(ABC):
    """Document."""

    document_id: str

    def __init__(self, document_id: str):
        """Initialize Document."""
        self.document_id = document_id

    @abstractmethod
    def modified_time(self) -> Any:
        """Get the modified time of the document."""
        pass

    @abstractmethod
    def load_data(self) -> str:
        """Load the data of the document."""
        pass

    @abstractmethod
    def get_metadata(self) -> dict:
        """Get the metadata of the document."""
        pass

    @abstractmethod
    def set_metadata(self, metadata: dict):
        """Set the metadata of the document."""
        pass

    @property
    def page_content(self) -> str:
        """Get the page content of the document."""
        return self.load_data()

    @property
    def metadata(self) -> dict:
        """Get the metadata of the document."""
        return self.get_metadata()

    @metadata.setter
    def metadata(self, value: dict):
        """Set the metadata of the document."""
        self.set_metadata(value)

    @abstractmethod
    def dumps(self) -> str:
        """Dump the document to a json string."""
        pass

    @classmethod
    @abstractmethod
    def loads(cls, data: str) -> "Document":
        """Load the document from a json string."""
        pass


class StaticDocument(Document):
    """Static Document holds data in-memory."""

    data: str
    _metadata: dict

    def __init__(self, data: str, metadata: dict, document_id: Optional[str] = None, mtime=None):
        """Initialize StaticDocument."""
        if document_id is None:
            filename = metadata.get("source", {}).get("filename", None)
            if filename is not None:
                document_id = f"{filename}{metadata.get('source', {}).get('chunk_id', '')}"
            else:
                document_id = str(mmh3.hash128(data))

        super().__init__(document_id)
        self.data = data
        self._metadata = metadata
        self.mtime = mtime

    def modified_time(self) -> Any:
        """Get the modified time of the document."""
        return self.mtime

    def load_data(self) -> str:
        """Load the data of the document."""
        return self.data

    def get_metadata(self) -> dict:
        """Get the metadata of the document."""
        # if "stats" in self._metadata:
        #     if "source" not in self._metadata:
        #         self._metadata["source"] = {}
        #     self._metadata["source"]["stats"] = self._metadata["stats"]
        #     del self._metadata["stats"]

        self._metadata = {**self._metadata, "stats": self.document_stats()}
        return self._metadata

    def set_metadata(self, metadata: dict):
        """Set the metadata of the document."""
        self._metadata = metadata

    def document_stats(self) -> dict:
        """Get the stats of the document."""
        return {
            "tiktokens": token_length_function()(self.data),
            "chars": len(self.data),
            "lines": len(self.data.splitlines()),
        }

    def __repr__(self):
        """Get the representation of the document."""
        return f"StaticDocument(id={self.document_id}, mtime={self.mtime}, metadata={self._metadata})"

    def dumps(self) -> str:
        """Dump the document to a json string."""
        return json.dumps({"content": self.data, "metadata": self._metadata, "document_id": self.document_id})

    @classmethod
    def loads(cls, data: str) -> "Document":
        """Load the document from a json string."""
        data_dict = json.loads(data)
        metadata = data_dict["metadata"]
        return cls(data_dict["content"], metadata, data_dict.get("document_id", metadata.get("document_id", metadata.get("id", mmh3.hash128(data_dict["content"])))))
