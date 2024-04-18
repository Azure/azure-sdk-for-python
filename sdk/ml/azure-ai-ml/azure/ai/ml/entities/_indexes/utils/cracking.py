# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Extension loader utilities."""

import copy
import os

from azure.ai.ml.entities._indexes.documents.cracking import file_extension_loaders
from azure.ai.ml.entities._indexes.utils.logging import get_logger

logger = get_logger("extension_loader")


def get_extension_loaders_with_document_intelligence(doc_intel_connection_id: str = None) -> dict:
    """Retrieve the extension loaders. Using DocumentIntelligencePDFLoader if a document intelligence connection id is provided."""
    extension_loaders = copy.deepcopy(file_extension_loaders)
    # If doc_intel_connection is provided, try to use Document intelligence service to crack the document
    if doc_intel_connection_id is not None:
        from azure.ai.ml.entities._indexes.utils.connections import (
            connection_to_credential,
            get_connection_by_id_v2,
            get_metadata_from_connection,
        )

        # Get and update endpoint in environment variable
        connection = get_connection_by_id_v2(connection_id=doc_intel_connection_id)
        endpoint = get_metadata_from_connection(connection).get("endpoint", None)
        if endpoint is not None:
            os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"] = endpoint

        # Get and update the api key in environment variable
        connection_credential = connection_to_credential(connection, data_plane=True)
        if connection_credential.key is not None:
            os.environ["DOCUMENT_INTELLIGENCE_KEY"] = connection_credential.key

        # set PDF loader if both endpoint and api key are not None
        if endpoint is not None and connection_credential.key is not None:
            from azure.ai.ml.entities._indexes.documents.document_intelligence_loader import DocumentIntelligencePDFLoader

            extension_loaders[".pdf"] = DocumentIntelligencePDFLoader
            logger.info(f"Document Intelligence is set as PDF loader. Endpoint: {endpoint}")
        else:
            # Raising ValueError instead of returning default extension_loaders
            # as we want to fail fast if the connection is provided but not valid.
            logger.error(f"Failed to retrieve endpoint and api key for {doc_intel_connection_id}.")
            raise ValueError(f"Document Intelligence connection '{doc_intel_connection_id}' is not valid.")
    return extension_loaders
