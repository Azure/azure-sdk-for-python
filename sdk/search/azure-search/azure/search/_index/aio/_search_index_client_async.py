# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import cast, List, TYPE_CHECKING

import six

from azure.core.async_paging import AsyncItemPaged, AsyncPageIterator
from azure.core.pipeline.policies import HeadersPolicy
from azure.core.tracing.decorator_async import distributed_trace_async
from .._generated.aio import SearchIndexClient as _SearchIndexClient
from .._generated.models import (
    IndexBatch,
    IndexingResult,
    SearchRequest,
)
from .._index_documents_batch import IndexDocumentsBatch
from .._queries import AutocompleteQuery, SearchQuery, SuggestQuery
from .._search_index_client import (
    DEFAULT_SEARCH_DNS_SUFFIX,
    convert_search_result,
    pack_continuation_token,
    unpack_continuation_token,
)

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Union
    from .._credential import SearchApiKeyCredential


class _SearchDocumentsPagedAsync(AsyncPageIterator):
    def __init__(self, client, initial_query, kwargs, continuation_token=None):
        super(_SearchDocumentsPagedAsync, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token,
        )
        self._client = client
        self._initial_query = initial_query
        self._kwargs = kwargs

    async def _get_next_cb(self, continuation_token):
        if continuation_token is None:
            return await self._client.documents.search_post(
                search_request=self._initial_query.request, **self._kwargs
            )

        _next_link, next_page_request = unpack_continuation_token(continuation_token)

        return await self._client.documents.search_post(
            search_request=next_page_request
        )

    async def _extract_data_cb(self, response):  # pylint:disable=no-self-use
        continuation_token = pack_continuation_token(response)

        results = [convert_search_result(r) for r in response.results]

        return continuation_token, results


class SearchIndexClient(object):
    """A client to interact with an existing Azure search index.


    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START create_search_client_with_key_async]
            :end-before: [END create_search_client_with_key_async]
            :language: python
            :dedent: 4
            :caption: Creating the SearchIndexClient with an API key.
    """

    def __init__(self, search_service_name, index_name, credential, **kwargs):
        # type: (str, str, SearchApiKeyCredential, **Any) -> None

        headers_policy = HeadersPolicy(
            {
                "api-key": credential.api_key,
                "Accept": "application/json;odata.metadata=none",
            }
        )

        search_dns_suffix = kwargs.pop("search_dns_suffix", DEFAULT_SEARCH_DNS_SUFFIX)

        self._search_service_name = search_service_name  # type: str
        self._index_name = index_name  # type: str
        self._client = _SearchIndexClient(
            endpoint="https://" + search_service_name + "." + search_dns_suffix,
            index_name=index_name,
            headers_policy=headers_policy,
        )  # type: _SearchIndexClient

    def __repr__(self):
        # type: () -> str
        return "<SearchIndexClient [service={}, index={}]>".format(
            repr(self._search_service_name), repr(self._index_name)
        )[:1024]

    async def close(self):
        # type: () -> None
        """ Close the SearchIndexClient session

        """
        return await self._client.close()

    @distributed_trace_async
    async def get_document_count(self, **kwargs):
        # type: (**Any) -> int
        """Return the number of documents in the Azure search index.

        """
        return int(await self._client.documents.count(**kwargs))

    @distributed_trace_async
    async def get_document(self, key, selected_fields=None, **kwargs):
        # type: (str, List[str], **Any) -> dict
        """Retrieve a document from the Azure search index by its key.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_get_document_async.py
                :start-after: [START get_document_async]
                :end-before: [END get_document_async]
                :language: python
                :dedent: 4
                :caption: Get a specific document from the search index.
        """
        result = await self._client.documents.get(
            key=key, selected_fields=selected_fields, **kwargs
        )
        return cast(dict, result)

    @distributed_trace_async
    async def search(self, query, **kwargs):
        # type: (Union[str, SearchQuery], **Any) -> AsyncItemPaged[dict]
        """Search the Azure search index for documents.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_simple_query_async.py
                :start-after: [START simple_query_async]
                :end-before: [END simple_query_async]
                :language: python
                :dedent: 4
                :caption: Search on a simple text term.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_filter_query_async.py
                :start-after: [START filter_query_async]
                :end-before: [END filter_query_async]
                :language: python
                :dedent: 4
                :caption: Filter and sort search results.
        """
        if isinstance(query, six.string_types):
            query = SearchQuery(search_text=query)
        elif not isinstance(query, SearchQuery):
            raise TypeError(
                "Expected a string or SearchQuery for 'query', but got {}".format(
                    repr(query)
                )
            )

        return AsyncItemPaged(
            self._client, query, kwargs, page_iterator_class=_SearchDocumentsPagedAsync
        )

    @distributed_trace_async
    async def suggest(self, query, **kwargs):
        # type: (Union[str, SuggestQuery], **Any) -> List[dict]
        """Get search suggestion results from the Azure search index.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_suggestions_async.py
                :start-after: [START suggest_query_async]
                :end-before: [END suggest_query_async]
                :language: python
                :dedent: 4
                :caption: Get search suggestions.
        """
        if not isinstance(query, SuggestQuery):
            raise TypeError(
                "Expected a SuggestQuery for 'query', but got {}".format(repr(query))
            )

        response = await self._client.documents.suggest_post(
            suggest_request=query.request, **kwargs
        )
        results = [r.as_dict() for r in response.results]
        return results

    @distributed_trace_async
    async def autocomplete(self, query, **kwargs):
        # type: (Union[str, AutocompleteQuery], **Any) -> List[dict]
        """Get search auto-completion results from the Azure search index.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_autocomplete_async.py
                :start-after: [START autocomplete_query_async]
                :end-before: [END autocomplete_query_async]
                :language: python
                :dedent: 4
                :caption: Get a auto-completions.
        """
        if not isinstance(query, AutocompleteQuery):
            raise TypeError(
                "Expected a AutocompleteQuery for 'query', but got {}".format(
                    repr(query)
                )
            )

        response = await self._client.documents.autocomplete_post(
            autocomplete_request=query.request, **kwargs
        )
        results = [r.as_dict() for r in response.results]
        return results

    async def upload_documents(self, documents, **kwargs):
        # type: (List[dict], **Any) -> List[IndexingResult]
        """Upload new documents to the Azure search index.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_crud_operations_async.py
                :start-after: [START upload_document_async]
                :end-before: [END upload_document_async]
                :language: python
                :dedent: 4
                :caption: Upload new documents to an index
        """
        batch = IndexDocumentsBatch()
        batch.add_upload_documents(documents)
        results = await self.index_documents(batch, **kwargs)
        return cast(List[IndexingResult], results)

    async def delete_documents(self, documents, **kwargs):
        # type: (List[dict], **Any) -> List[IndexingResult]
        """Delete documents from the Azure search index

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_crud_operations_async.py
                :start-after: [START delete_document_async]
                :end-before: [END delete_document_async]
                :language: python
                :dedent: 4
                :caption: Delete existing documents to an index
        """
        batch = IndexDocumentsBatch()
        batch.add_delete_documents(documents)
        results = await self.index_documents(batch, **kwargs)
        return cast(List[IndexingResult], results)

    async def merge_documents(self, documents, **kwargs):
        # type: (List[dict], **Any) -> List[IndexingResult]
        """Merge documents in to existing documents in the Azure search index.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_crud_operations_async.py
                :start-after: [START merge_document_async]
                :end-before: [END merge_document_async]
                :language: python
                :dedent: 4
                :caption: Merge fields into existing documents to an index
        """
        batch = IndexDocumentsBatch()
        batch.add_merge_documents(documents)
        results = await self.index_documents(batch, **kwargs)
        return cast(List[IndexingResult], results)

    async def merge_or_upload_documents(self, documents, **kwargs):
        # type: (List[dict], **Any) -> List[IndexingResult]
        """Merge documents in to existing documents in the Azure search index,
        or upload them if they do not yet exist.

        """
        batch = IndexDocumentsBatch()
        batch.add_merge_or_upload_documents(documents)
        results = await self.index_documents(batch, **kwargs)
        return cast(List[IndexingResult], results)

    @distributed_trace_async
    async def index_documents(self, batch, **kwargs):
        # type: (IndexBatch, **Any) -> List[IndexingResult]
        """Specify a document operations to perform as a batch.

        """
        index_documents = IndexBatch(actions=batch.actions)
        batch_response = await self._client.documents.index(batch=index_documents, **kwargs)
        return cast(List[IndexingResult], batch_response.results)

    async def __aenter__(self):
        # type: () -> SearchIndexClient
        await self._client.__aenter__()  # pylint: disable=no-member
        return self

    async def __aexit__(self, *args):
        # type: (*Any) -> None
        await self._client.__aexit__(*args)  # pylint: disable=no-member
