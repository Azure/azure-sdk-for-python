# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os

from typing import Optional, Union
from azure.core.credentials import TokenCredential
from azure.ai.resources.entities import Index

from ._mlindex import MLIndex as DataplaneMLIndex

def get_langchain_embeddings_from_index(
    path: Union[str, os.PathLike, Index],
    credential: Optional[TokenCredential] = None,
):
    return DataplaneMLIndex(path).get_langchain_embeddings(credential=credential)


def get_langchain_vectorstore_from_index(
    path: Union[str, os.PathLike, Index],
    credential: Optional[TokenCredential] = None,
):
    return DataplaneMLIndex(path).as_langchain_vectorstore(credential=credential)


def get_langchain_retriever_from_index(
    path: Union[str, os.PathLike, Index],
    credential: Optional[TokenCredential] = None,
    **kwargs,
):
    return DataplaneMLIndex(path).as_langchain_retriever(credential=credential, **kwargs)


def get_native_index_client_from_index(
    path: Union[str, os.PathLike, Index],
    credential: Optional[TokenCredential] = None,
):
    return DataplaneMLIndex(path).as_native_index_client(credential=credential)
