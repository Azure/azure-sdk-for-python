# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure Cognitive Search based Vector Index."""
from types import ModuleType

from azure.ai.generative.index._utils.logging import get_logger, version

logger = get_logger("indexes.azure_search")


def import_azure_search_or_so_help_me() -> ModuleType:
    """Import azure-search-documents if available, otherwise raise error."""
    try:
        import azure.search.documents as azure_search_documents
    except ImportError as e:
        raise ImportError(
            "Could not import azure-search-documents python package. "
            f"Please install it with `pip install azure-ai-generative[cognitive_search]=={version}`"
        ) from e
    return azure_search_documents
