# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines,no-self-use
from typing import (  # pylint: disable=unused-import
    Optional, Any, TYPE_CHECKING, Dict
)

from azure.core.paging import ItemPaged
from azure.storage.blob import BlobServiceClient  # pylint: disable=no-name-in-module

from azure.storage.blob._shared.base_client import parse_connection_str
from ._models import ChangeFeedPaged
if TYPE_CHECKING:
    from datetime import datetime


class ChangeFeedClient(object):  # pylint: disable=too-many-public-methods
    """A client to interact with a specific account change feed.

    :param str account_url:
        The URI to the storage account.
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string,
        an instance of a AzureSasCredential from azure.core.credentials, an account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the resource URI already contains a SAS token, this will be ignored in favor of an explicit credential
        - except in the case of AzureSasCredential, where the conflicting SAS tokens will raise a ValueError.
    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    :keyword int max_single_get_size:
        The maximum size for a changefeed blob to be downloaded in a single call,
        the exceeded part will be downloaded in chunks.
    :keyword int max_chunk_get_size:
        The maximum chunk size used for downloading a changefeed blob.
    :keyword str api_version:
        The Storage API version to use for requests. Default value is the most recent service version that is
        compatible with the current SDK. Setting to an older version may result in reduced feature compatibility.

    .. admonition:: Example:

        .. literalinclude:: ../samples/change_feed_samples.py
            :start-after: [START create_change_feed_client]
            :end-before: [END create_change_feed_client]
            :language: python
            :dedent: 8
            :caption: Creating the ChangeFeedClient from a URL to a public blob (no auth needed).
    """
    def __init__(
            self, account_url,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        self._blob_service_client = BlobServiceClient(account_url, credential, **kwargs)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):  # type: (...) -> ChangeFeedClient
        """Create ChangeFeedClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string,
            an instance of a AzureSasCredential from azure.core.credentials, an account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
            Credentials provided here will take precedence over those in the connection string.
        :returns: A change feed client.
        :rtype: ~azure.storage.blob.changefeed.ChangeFeedClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_authentication.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the BlobServiceClient using account_key as credential.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'blob')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(account_url, credential=credential, **kwargs)

    def list_changes(self, **kwargs):
        # type: (**Any) -> ItemPaged[Dict]
        """Returns a generator to list the change feed events.
        The generator will lazily follow the continuation tokens returned by
        the service.

        :keyword datetime start_time:
            Filters the results to return only events which happened after this time.
        :keyword datetime end_time:
            Filters the results to return only events which happened before this time.
        :keyword int results_per_page:
            The page size when list events by page using by_page() method on the generator.
        :returns: An iterable (auto-paging) response of events whose type is dictionary.
        :rtype: ~azure.core.paging.ItemPaged[dict]

        .. admonition:: Example:

            .. literalinclude:: ../samples/change_feed_samples.py
                :start-after: [START list_all_events]
                :end-before: [END list_all_events]
                :language: python
                :dedent: 8
                :caption: List all change feed events.

            .. literalinclude:: ../samples/change_feed_samples.py
                :start-after: [START list_events_by_page]
                :end-before: [END list_events_by_page]
                :language: python
                :dedent: 8
                :caption: List change feed events by page.
        """
        results_per_page = kwargs.pop('results_per_page', None)
        container_client = self._blob_service_client.get_container_client("$blobchangefeed")
        return ItemPaged(
            container_client,
            results_per_page=results_per_page,
            page_iterator_class=ChangeFeedPaged,
            **kwargs)
