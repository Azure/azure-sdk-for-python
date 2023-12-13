# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DocumentStore."""
from pathlib import Path
from typing import Dict, Optional, Union

from azure.ai.generative.index._documents import Document, StaticDocument
from azure.ai.generative.index._utils.logging import get_logger

logger = get_logger(__name__)


class FileBasedDocstore:
    """Simple docstore which serializes to file and loads into memory."""

    def __init__(self, _dict: Optional[Dict[str, Document]] = None):
        """Initialize with dict."""
        self._dict = _dict if _dict is not None else {}

    def add(self, texts: Dict[str, Document]) -> None:
        """
        Add texts to in memory dictionary.

        Args:
        ----
            texts: dictionary of id -> document.

        Returns:
        -------
            None
        """
        overlapping = set(texts).intersection(self._dict)
        if overlapping:
            raise ValueError(f"Tried to add ids that already exist: {overlapping}")
        self._dict = {**self._dict, **texts}

    def delete(self, ids: list) -> None:
        """Deleting IDs from in memory dictionary."""
        overlapping = set(ids).intersection(self._dict)
        if not overlapping:
            raise ValueError(f"Tried to delete ids that does not  exist: {ids}")
        for _id in ids:
            self._dict.pop(_id)

    def search(self, search: str) -> Union[Document, str]:
        """
        Search via direct lookup.

        Args:
        ----
            search: id of a document to search for.

        Returns:
        -------
            Document if found, else error message.
        """
        if search not in self._dict:
            return f"ID {search} not found."
        else:
            return self._dict[search]

    def save(self, output_path: str):
        """
        Save to JSONL file.

        Args:
        ----
            output_path: folder to save doctore contents in.
        """
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        with (output_path / "docs.jsonl").open("w", encoding="utf-8") as f:
            for doc in self._dict.values():
                json_line = doc.dumps()
                f.write(json_line + "\n")

    @classmethod
    def load(cls, input_path: str) -> "FileBasedDocstore":
        """Load from JSONL file."""
        from fsspec.core import url_to_fs

        fs, uri = url_to_fs(input_path)

        documents = {}
        with fs.open(f"{input_path.rstrip('/')}/docs.jsonl") as f:
            for line in f:
                document = StaticDocument.loads(line.strip())
                documents[document.document_id] = document
        return cls(documents)
