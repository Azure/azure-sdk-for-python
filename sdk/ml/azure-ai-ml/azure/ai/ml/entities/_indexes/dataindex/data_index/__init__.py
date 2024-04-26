# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DataIndex configuration and operations."""

from azure.ai.ml.entities._indexes.dataindex.data_index.models import build_model_protocol
from azure.ai.ml.entities._indexes.dataindex.entities.data_index import CitationRegex, Data, DataIndex, Embedding, IndexSource, IndexStore
from azure.ai.ml.entities._indexes.dataindex.entities._builders.data_index_func import index_data

__all__ = [
    "DataIndex",
    "IndexSource",
    "Data",
    "CitationRegex",
    "Embedding",
    "IndexStore",
    "index_data",
    "build_model_protocol",
]
