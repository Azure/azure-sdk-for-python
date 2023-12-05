# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Index Creation and Operation Functions."""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._build_mlindex import build_index
from ._functions import (
    get_langchain_embeddings_from_index,
    get_langchain_retriever_from_index,
    get_langchain_vectorstore_from_index,
    get_native_index_client_from_index
)

__all__ = [
    "build_index",
    "get_langchain_embeddings_from_index",
    "get_langchain_retriever_from_index",
    "get_langchain_vectorstore_from_index",
    "get_native_index_client_from_index"
]
