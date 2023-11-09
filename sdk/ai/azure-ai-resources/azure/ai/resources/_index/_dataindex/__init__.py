# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DataIndex configuration and operations."""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from azure.ai.resources._index._dataindex.entities import Data, CitationRegex, DataIndex, Embedding, IndexSource, IndexStore, index_data
from azure.ai.resources._index._dataindex.operations import DataOperations

__all__ = [
    "DataOperations",
    "DataIndex",
    "IndexSource",
    "Data",
    "CitationRegex",
    "Embedding",
    "IndexStore",
    "index_data",
]
