# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from ._credential import SearchApiKeyCredential
from ._index_operation import IndexOperationBatch
from ._search_index_client import SearchIndexClient
from ._queries import (  # pylint: disable=unused-import
    AutocompleteQuery,
    SearchQuery,
    SuggestQuery,
)

__all__ = (
    "IndexOperationBatch",
    "SearchApiKeyCredential",
    "SearchIndexClient",
    "SearchQuery",
)
