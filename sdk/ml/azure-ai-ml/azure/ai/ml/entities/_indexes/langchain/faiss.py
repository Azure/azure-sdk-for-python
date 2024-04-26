# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Faiss based VectorStore using a file based DocumentStore."""

from azure.ai.ml.entities._indexes.indexes.faiss import FaissAndDocStore
from azure.ai.ml.entities._indexes.langchain.docstore import FileBasedDocStore
from azure.ai.ml.entities._indexes.utils.logging import get_logger, langchain_version
from langchain.vectorstores.base import VectorStore
from packaging import version as pkg_version

langchain_pkg_version = pkg_version.parse(langchain_version)

if langchain_pkg_version >= pkg_version.parse("0.1.0"):
    from langchain_community.vectorstores import FAISS
else:
    from langchain.vectorstores import FAISS

logger = get_logger(__name__)


def azureml_faiss_as_langchain_faiss(faissanddocstore: FaissAndDocStore) -> VectorStore:
    """Convert an AzureML FaissAndDocStore to a langchain FAISS VectorStore."""
    return FAISS(
        faissanddocstore.query_embed,
        faissanddocstore.index,
        FileBasedDocStore(faissanddocstore.docstore),
        {int(k): v for (k, v) in faissanddocstore.index_to_doc_id.items()},
    )
