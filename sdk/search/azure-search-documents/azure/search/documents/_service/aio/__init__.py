# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from ._search_service_client_async import SearchServiceClient

from ._datasources_client import SearchDataSourcesClient
from ._indexers_client import SearchIndexersClient
from ._indexes_client import SearchIndexesClient
from ._skillsets_client import SearchSkillsetsClient
from ._synonym_maps_client import SearchSynonymMapsClient

__all__ = (
    "SearchServiceClient",
    "SearchDataSourcesClient",
    "SearchIndexersClient",
    "SearchIndexesClient",
    "SearchSkillsetsClient",
    "SearchSynonymMapsClient",
)
