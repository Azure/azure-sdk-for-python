#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Any, Union

from ._generated._monitor_query_client import (
    MonitorQueryClient,
)

from ._helpers import get_authentication_policy

if TYPE_CHECKING:
    from azure.identity import DefaultAzureCredential
    from azure.core.credentials import TokenCredential

class LogQueryClient(object):
    """LogQueryClient
    """

    def __init__(self, credential, **kwargs):
        # type: (Union[DefaultAzureCredential, TokenCredential], Any) -> None
        self._client = MonitorQueryClient(
            credential=credential,
            authentication_policy=get_authentication_policy(credential),
            **kwargs
        )
        self._query_op = self._client.query

    def query(self, workspace_id, query, **kwargs):
        # type: (str, str, Any) -> None
        """Execute an Analytics query.

        Executes an Analytics query for data.
        """
        return self._query_op.get(workspace_id, query, **kwargs)

    def batch_query(self, batch, **kwargs):
        # type: (str, Any) -> None
        """Execute an Analytics query.

        Executes an Analytics query for data.
        """
        return self._query_op.batch(batch, **kwargs)

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.monitor.query.LogQueryClient` session."""
        return self._client.close()

    def __enter__(self):
        # type: () -> LogQueryClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
