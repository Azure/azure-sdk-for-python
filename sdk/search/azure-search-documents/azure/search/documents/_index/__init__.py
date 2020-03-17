# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from ._credential import SearchApiKeyCredential  # pylint: disable=unused-import
from ._index_documents_batch import IndexDocumentsBatch  # pylint: disable=unused-import
from ._search_index_client import (  # pylint: disable=unused-import
    odata,
    SearchItemPaged,
    SearchIndexClient,
)
from ._queries import (  # pylint: disable=unused-import
    AutocompleteQuery,
    SearchQuery,
    SuggestQuery,
)
from ._generated.models import (  # pylint: disable=unused-import
    IndexAction,
    IndexingResult,
)
