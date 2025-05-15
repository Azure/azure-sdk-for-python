# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, Optional, Union
from typing_extensions import Self

from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace

class ChangeFeedClient:  # pylint: disable=client-accepts-api-version-keyword
    def __init__(
        self,
        account_url: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        secondary_hostname: Optional[str] = None,
        max_single_get_size: Optional[int] = None,
        max_chunk_get_size: Optional[int] = None,
        api_version: Optional[str] = None,
        **kwargs: Any
    ) -> None: ...
    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        secondary_hostname: Optional[str] = None,
        max_single_get_size: Optional[int] = None,
        max_chunk_get_size: Optional[int] = None,
        api_version: Optional[str] = None,
        **kwargs: Any
    ) -> Self: ...
    @distributed_trace
    def list_changes(
        self,
        *,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        results_per_page: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]: ...
