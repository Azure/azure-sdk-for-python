# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Faiss based VectorStore using a file based DocumentStore."""

import logging
from azure.ai.ml.entities._indexes.entities.faiss import FaissAndDocStore
from .docstore import FileBasedDocStore
from langchain.vectorstores.base import VectorStore

from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)


def azureml_faiss_as_langchain_faiss(faissanddocstore: FaissAndDocStore) -> VectorStore:
    """Convert an AzureML FaissAndDocStore to a langchain FAISS VectorStore."""
    return FAISS(
        faissanddocstore.query_embed,
        faissanddocstore.index,
        FileBasedDocStore(faissanddocstore.docstore),
        {int(k): v for (k, v) in faissanddocstore.index_to_doc_id.items()},
    )
