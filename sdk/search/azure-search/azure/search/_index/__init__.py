# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from ._credential import SearchApiKeyCredential
from ._index_batch import IndexBatch
from ._search_index_client import SearchIndexClient
from ._queries import (  # pylint: disable=unused-import
    AutocompleteQuery,
    SearchQuery,
    SuggestQuery,
)
