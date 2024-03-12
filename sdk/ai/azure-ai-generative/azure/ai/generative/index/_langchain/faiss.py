# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Faiss based VectorStore using a file based DocumentStore."""
from langchain.vectorstores import FAISS  # pylint: disable=import-error
from langchain.vectorstores.base import VectorStore  # pylint: disable=import-error
from azure.ai.generative.index._langchain.docstore import FileBasedDocStore
from azure.ai.generative.index._utils.logging import get_logger
from azure.ai.resources._index._indexes.faiss import FaissAndDocStore

logger = get_logger(__name__)


def azureml_faiss_as_langchain_faiss(faissanddocstore: FaissAndDocStore) -> VectorStore:
    """Convert an AzureML FaissAndDocStore to a langchain FAISS VectorStore.

    :param faissanddocstore: The AzureML FaissAndDocStore to convert.
    :type faissanddocstore: FaissAndDocStore
    :return: The converted langchain FAISS VectorStore.
    :rtype: VectorStore
    """
    return FAISS(
        faissanddocstore.query_embed,
        faissanddocstore.index,
        FileBasedDocStore(faissanddocstore.docstore),
        {int(k): v for (k, v) in faissanddocstore.index_to_doc_id.items()},
    )
