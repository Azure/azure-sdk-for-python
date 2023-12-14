# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Faiss based VectorStore using a file based DocumentStore."""
from azure.ai.resources._index._indexes.faiss import FaissAndDocStore
from azure.ai.resources._index._langchain.docstore import FileBasedDocStore
from azure.ai.resources._index._utils.logging import get_logger
from langchain.vectorstores import FAISS
from langchain.vectorstores.base import VectorStore

logger = get_logger(__name__)


def azureml_faiss_as_langchain_faiss(faiss_and_docstore: FaissAndDocStore) -> VectorStore:
    """Convert an AzureML FaissAndDocStore to a langchain FAISS VectorStore."""
    return FAISS(
        faiss_and_docstore.query_embed,
        faiss_and_docstore.index,
        FileBasedDocStore(faiss_and_docstore.docstore),
        {int(k): v for (k, v) in faiss_and_docstore.index_to_doc_id.items()}
    )
