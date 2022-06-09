# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import HttpResponseError
from .._generated.aio._search_client import SearchClient as SearchClientGen
from .._generated.models import BatchRequest, SearchAddressBatchResult
# from ..utils import get_authentication_policy

if TYPE_CHECKING:
    from typing import Any, List
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.polling import LROPoller, AsyncLROPoller


class SearchClient(object):
    """Azure Maps Search REST APIs.

    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential
    :param client_id: Specifies which account is intended for usage in conjunction with the Azure AD security model.  It represents a unique ID for the Azure Maps account and can be retrieved from the Azure Maps management  plane Account API. To use Azure AD security in Azure Maps see the following `articles <https://aka.ms/amauthdetails>`_ for guidance.
    :type client_id: str
    :param str base_url: Service URL
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no Retry-After header is present.
    """
    def __init__(
        self,
        credential, # type: AsyncTokenCredential
        **kwargs # type: Any
    ):
        # type: (...) -> None
        if not credential:
            raise ValueError(
                "You need to provide account shared key to authenticate.")

        self._search_client = SearchClientGen(
            credential,
            **kwargs
        ).search

   
    @distributed_trace_async
    def begin_fuzzy_search_batch(
        self,
        batch_request,  # type: "BatchRequest"
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller["SearchAddressBatchResult"]
        """begin_fuzzy_search_batch

        :param batch_request: The list of address geocoding queries/requests to process. The list can
         contain  a max of 10,000 queries and must contain at least 1 query.
        :type batch_request: ~azure.maps.search._generated.models.BatchRequest
        :return: LROPoller["SearchAddressBatchResult"]
        :returntype: ~azure.core.polling.LROPoller[~azure.maps.search._generated.models.SearchAddressBatchResult]
        """
        poller = self._search_client.begin_fuzzy_search_batch(
            batch_request,
            **kwargs
        )
        result_properties = poller.result().additional_properties
        if 'status' in result_properties and result_properties['status'].lower() == 'failed':
            raise HttpResponseError(message=result_properties['error']['message'])

        return poller


    @distributed_trace_async
    def begin_search_address_batch(
        self,
        batch_request,  # type: "BatchRequest"
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller["SearchAddressBatchResult"]
        """begin_search_address_batch

        :param batch_request: The list of address geocoding queries/requests to process. The list can
         contain  a max of 10,000 queries and must contain at least 1 query.
        :type batch_request: ~azure.maps.search._generated.models.BatchRequest
        :return: LROPoller["SearchAddressBatchResult"]
        :paramtype: ~azure.core.polling.LROPoller[~azure.maps.search._generated.models.SearchAddressBatchResult]
        """
        poller =  self._search_client.begin_search_address_batch(
            batch_request,
            **kwargs
        )

        result_properties = poller.result().additional_properties
        if 'status' in result_properties and result_properties['status'].lower() == 'failed':
            raise HttpResponseError(message=result_properties['error']['message'])

        return poller


    @distributed_trace_async
    def begin_reverse_search_address_batch(
        self,
        batch_request,  # type: "BatchRequest"
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller["ReverseSearchAddressBatchProcessResult"]
        """begin_reverse_search_address_batch

        :param batch_request: The list of address geocoding queries/requests to process. The list can
         contain  a max of 10,000 queries and must contain at least 1 query.
        :type batch_request: ~azure.maps.search._generated.models.BatchRequest
        :return: LROPoller["ReverseSearchAddressBatchProcessResult"]
        :paramtype: ~azure.core.polling.LROPoller[~azure.maps.search._generated.models.ReverseSearchAddressBatchProcessResult]
        """
        poller =  self._search_client.begin_reverse_search_address_batch(
            batch_request,
            **kwargs
        )
        result_properties = poller.result().additional_properties
        if 'status' in result_properties and result_properties['status'].lower() == 'failed':
            raise HttpResponseError(message=result_properties['error']['message'])

        return poller
