# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Document abstraction."""
from abc import ABC
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class DocumentSource:
    """Document Source."""

    path: Optional[Path]
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
