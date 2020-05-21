# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.core import MatchConditions
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import ClientAuthenticationError, ResourceNotFoundError

from ._generated import SearchServiceClient as _SearchServiceClient
from ._utils import get_access_conditions
from .._headers_mixin import HeadersMixin
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from ._generated.models import SearchIndexerSkill
    from typing import Any, List, Sequence, Union
    from azure.core.credentials import AzureKeyCredential


class SearchSkillsetsClient(HeadersMixin):
    """A client to interact with Azure search service Skillsets.

    This class is not normally instantiated directly, instead use
    `get_skillsets_client()` from a `SearchServiceClient`

    """

    _ODATA_ACCEPT = "application/json;odata.metadata=minimal"  # type: str

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, AzureKeyCredential, **Any) -> None

        self._endpoint = endpoint  # type: str
        self._credential = credential  # type: AzureKeyCredential
        self._client = _SearchServiceClient(
            endpoint=endpoint, sdk_moniker=SDK_MONIKER, **kwargs
        )  # type: _SearchServiceClient

    def __enter__(self):
        # type: () -> SearchSkillsetsClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        return self._client.__exit__(*args)  # pylint:disable=no-member

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.documents.SearchSkillsetsClient` session.

        """
        return self._client.close()

