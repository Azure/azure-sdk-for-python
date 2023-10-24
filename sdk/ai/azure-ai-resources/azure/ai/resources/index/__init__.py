# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""MLIndex Creation and Operation Functions."""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._build_mlindex import build_mlindex
from ._functions import (
    get_langchain_embeddings_from_mlindex,
    get_langchain_retriever_from_mlindex,
    get_langchain_vectorstore_from_mlindex,
    get_native_index_client_from_mlindex
)

__all__ = [
    "build_mlindex",
    "get_langchain_embeddings_from_mlindex",
    "get_langchain_retriever_from_mlindex",
    "get_langchain_vectorstore_from_mlindex",
    "get_native_index_client_from_mlindex"
]
