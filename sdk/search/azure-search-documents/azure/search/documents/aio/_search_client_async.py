# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import cast, List, Union, Any, Optional, Dict

from azure.core.rest import HttpRequest, AsyncHttpResponse
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from ._paging import AsyncSearchItemPaged, AsyncSearchPageIterator
from .._utils import get_authentication_policy, get_answer_query
from .._generated.aio import SearchIndexClient
from .._generated.models import (
    AutocompleteMode,
    AutocompleteRequest,
    IndexAction,
    IndexBatch,
    IndexingResult,
    QueryAnswerType,
    QueryCaptionType,
    QueryType,
    SearchMode,
    ScoringStatistics,
    VectorFilterMode,
    VectorQuery,
    SemanticErrorMode,
    SuggestRequest,
)
from .._search_documents_error import RequestEntityTooLargeError
from .._index_documents_batch import IndexDocumentsBatch
from .._queries import AutocompleteQuery, SearchQuery, SuggestQuery
from .._api_versions import DEFAULT_VERSION
from .._headers_mixin import HeadersMixin
from .._version import SDK_MONIKER


class SearchClient(HeadersMixin):
    """A client to interact with an existing Azure search index.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param index_name: The name of the index to connect to
    :type index_name: str
    :param credential: A credential to authorize search client requests
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials_async.AsyncTokenCredential
    :keyword str api_version: The Search API version to use for requests.
    :keyword str audience: sets the Audience to use for authentication with Azure Active Directory (AAD). The
        audience is not considered when using a shared key. If audience is not provided, the public cloud audience
        will be assumed.

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START create_search_client_with_key_async]
            :end-before: [END create_search_client_with_key_async]
            :language: python
            :dedent: 4
            :caption: Creating the SearchClient with an API key.
    """

    _ODATA_ACCEPT: str = "application/json;odata.metadata=none"
    _client: SearchIndexClient

    def __init__(
        self, endpoint: str, index_name: str, credential: Union[AzureKeyCredential, AsyncTokenCredential], **kwargs: Any
    ) -> None:
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._index_documents_batch = IndexDocumentsBatch()
        self._endpoint: str = endpoint
        self._index_name: str = index_name
        self._credential = credential
        audience = kwargs.pop("audience", None)
        if isinstance(credential, AzureKeyCredential):
            self._aad = False
            self._client = SearchIndexClient(
                endpoint=endpoint,
                index_name=index_name,
                sdk_moniker=SDK_MONIKER,
                api_version=self._api_version,
                **kwargs
            )
        else:
            self._aad = True
            authentication_policy = get_authentication_policy(credential, audience=audience, is_async=True)
            self._client = SearchIndexClient(
                endpoint=endpoint,
                index_name=index_name,
                authentication_policy=authentication_policy,
                sdk_moniker=SDK_MONIKER,
                api_version=self._api_version,
                **kwargs
            )

    def __repr__(self) -> str:
        return "<SearchClient [endpoint={}, index={}]>".format(repr(self._endpoint), repr(self._index_name))[:1024]

    async def close(self) -> None:
        """Close the session.
        :return: None
        :rtype: None
        """
        return await self._client.close()

    @distributed_trace_async
    async def get_document_count(self, **kwargs: Any) -> int:
        """Return the number of documents in the Azure search index.

        :return: The count of documents in the index
        :rtype: int
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        return int(await self._client.documents.count(**kwargs))

    @distributed_trace_async
    async def get_document(self, key: str, selected_fields: Optional[List[str]] = None, **kwargs: Any) -> Dict:
        """Retrieve a document from the Azure search index by its key.

        :param key: The primary key value for the document to retrieve
        :type key: str
        :param selected_fields: an allow-list of fields to include in the results
        :type selected_fields: list[str]
        :return: The document that matches the specified key
        :rtype:  dict

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_get_document_async.py
                :start-after: [START get_document_async]
                :end-before: [END get_document_async]
                :language: python
                :dedent: 4
                :caption: Get a specific document from the search index.
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.documents.get(key=key, selected_fields=selected_fields, **kwargs)
        return cast(dict, result)

    @distributed_trace_async
    async def search(
        self,
        search_text: Optional[str] = None,
        *,
        include_total_count: Optional[bool] = None,
        facets: Optional[List[str]] = None,
        filter: Optional[str] = None,
        highlight_fields: Optional[str] = None,
        highlight_post_tag: Optional[str] = None,
        highlight_pre_tag: Optional[str] = None,
        minimum_coverage: Optional[float] = None,
        order_by: Optional[List[str]] = None,
        query_type: Optional[Union[str, QueryType]] = None,
        scoring_parameters: Optional[List[str]] = None,
        scoring_profile: Optional[str] = None,
        semantic_query: Optional[str] = None,
        search_fields: Optional[List[str]] = None,
        search_mode: Optional[Union[str, SearchMode]] = None,
        query_answer: Optional[Union[str, QueryAnswerType]] = None,
        query_answer_count: Optional[int] = None,
        query_answer_threshold: Optional[float] = None,
        query_caption: Optional[Union[str, QueryCaptionType]] = None,
        query_caption_highlight_enabled: Optional[bool] = None,
        semantic_configuration_name: Optional[str] = None,
        select: Optional[List[str]] = None,
        skip: Optional[int] = None,
        top: Optional[int] = None,
        scoring_statistics: Optional[Union[str, ScoringStatistics]] = None,
        session_id: Optional[str] = None,
        vector_queries: Optional[List[VectorQuery]] = None,
        vector_filter_mode: Optional[Union[str, VectorFilterMode]] = None,
        semantic_error_mode: Optional[Union[str, SemanticErrorMode]] = None,
        semantic_max_wait_in_milliseconds: Optional[int] = None,
        **kwargs
    ) -> AsyncSearchItemPaged[Dict]:
        # pylint:disable=too-many-locals, disable=redefined-builtin
        """Search the Azure search index for documents.

        :param str search_text: A full-text search query expression; Use "*" or omit this parameter to
            match all documents.
        :keyword bool include_total_count: A value that specifies whether to fetch the total count of
            results. Default is false. Setting this value to true may have a performance impact. Note that
            the count returned is an approximation.
        :keyword list[str] facets: The list of facet expressions to apply to the search query. Each facet
            expression contains a field name, optionally followed by a comma-separated list of name:value
            pairs.
        :keyword str filter: The OData $filter expression to apply to the search query.
        :keyword str highlight_fields: The comma-separated list of field names to use for hit highlights.
            Only searchable fields can be used for hit highlighting.
        :keyword str highlight_post_tag: A string tag that is appended to hit highlights. Must be set with
            highlightPreTag. Default is </em>.
        :keyword str highlight_pre_tag: A string tag that is prepended to hit highlights. Must be set with
            highlightPostTag. Default is <em>.
        :keyword float minimum_coverage: A number between 0 and 100 indicating the percentage of the index that
            must be covered by a search query in order for the query to be reported as a success. This
            parameter can be useful for ensuring search availability even for services with only one
            replica. The default is 100.
        :keyword list[str] order_by: The list of OData $orderby expressions by which to sort the results. Each
            expression can be either a field name or a call to either the geo.distance() or the
            search.score() functions. Each expression can be followed by asc to indicate ascending, and
            desc to indicate descending. The default is ascending order. Ties will be broken by the match
            scores of documents. If no OrderBy is specified, the default sort order is descending by
            document match score. There can be at most 32 $orderby clauses.
        :keyword query_type: A value that specifies the syntax of the search query. The default is
            'simple'. Use 'full' if your query uses the Lucene query syntax. Possible values include:
            'simple', 'full', "semantic".
        :paramtype query_type: str or ~azure.search.documents.models.QueryType
        :keyword list[str] scoring_parameters: The list of parameter values to be used in scoring functions (for
            example, referencePointParameter) using the format name-values. For example, if the scoring
            profile defines a function with a parameter called 'mylocation' the parameter string would be
            "mylocation--122.2,44.8" (without the quotes).
        :keyword str scoring_profile: The name of a scoring profile to evaluate match scores for matching
            documents in order to sort the results.
        :keyword str semantic_query: Allows setting a separate search query that will be solely used for
            semantic reranking, semantic captions and semantic answers. Is useful for scenarios where there
            is a need to use different queries between the base retrieval and ranking phase, and the L2
            semantic phase.
        :keyword list[str] search_fields: The list of field names to which to scope the full-text search. When
            using fielded search (fieldName:searchExpression) in a full Lucene query, the field names of
            each fielded search expression take precedence over any field names listed in this parameter.
        :keyword search_mode: A value that specifies whether any or all of the search terms must be
            matched in order to count the document as a match. Possible values include: 'any', 'all'.
        :paramtype search_mode: str or ~azure.search.documents.models.SearchMode
        :keyword query_answer: This parameter is only valid if the query type is 'semantic'. If set,
            the query returns answers extracted from key passages in the highest ranked documents.
            Possible values include: "none", "extractive".
        :paramtype query_answer: str or ~azure.search.documents.models.QueryAnswerType
        :keyword int query_answer_count: This parameter is only valid if the query type is 'semantic' and
            query answer is 'extractive'.
            Configures the number of answers returned. Default count is 1.
        :keyword float query_answer_threshold: This parameter is only valid if the query type is 'semantic' and
            query answer is 'extractive'. Configures the number of confidence threshold. Default count is 0.7.
        :keyword query_caption: This parameter is only valid if the query type is 'semantic'. If set, the
            query returns captions extracted from key passages in the highest ranked documents.
            Defaults to 'None'. Possible values include: "none", "extractive".
        :paramtype query_caption: str or ~azure.search.documents.models.QueryCaptionType
        :keyword bool query_caption_highlight_enabled: This parameter is only valid if the query type is 'semantic' when
            query caption is set to 'extractive'. Determines whether highlighting is enabled.
            Defaults to 'true'.
        :keyword semantic_configuration_name: The name of the semantic configuration that will be used when
            processing documents for queries of type semantic.
        :paramtype semantic_configuration_name: str
        :keyword list[str] select: The list of fields to retrieve. If unspecified, all fields marked as retrievable
            in the schema are included.
        :keyword int skip: The number of search results to skip. This value cannot be greater than 100,000.
            If you need to scan documents in sequence, but cannot use $skip due to this limitation,
            consider using $orderby on a totally-ordered key and $filter with a range query instead.
        :keyword int top: The number of search results to retrieve. This can be used in conjunction with
            $skip to implement client-side paging of search results. If results are truncated due to
            server-side paging, the response will include a continuation token that can be used to issue
            another Search request for the next page of results.
        :keyword scoring_statistics: A value that specifies whether we want to calculate scoring
            statistics (such as document frequency) globally for more consistent scoring, or locally, for
            lower latency. The default is 'local'. Use 'global' to aggregate scoring statistics globally
            before scoring. Using global scoring statistics can increase latency of search queries.
            Possible values include: "local", "global".
        :paramtype scoring_statistics: str or ~azure.search.documents.models.ScoringStatistics
        :keyword str session_id: A value to be used to create a sticky session, which can help getting more
            consistent results. As long as the same sessionId is used, a best-effort attempt will be made
            to target the same replica set. Be wary that reusing the same sessionID values repeatedly can
            interfere with the load balancing of the requests across replicas and adversely affect the
            performance of the search service. The value used as sessionId cannot start with a '_'
            character.
        :keyword semantic_error_mode: Allows the user to choose whether a semantic call should fail
            completely (default / current behavior), or to return partial results. Known values are:
            "partial" and "fail".
        :paramtype semantic_error_mode: str or ~azure.search.documents.models.SemanticErrorMode
        :keyword int semantic_max_wait_in_milliseconds: Allows the user to set an upper bound on the amount of
            time it takes for semantic enrichment to finish processing before the request fails.
        :keyword vector_queries: The query parameters for vector and hybrid search queries.
        :paramtype vector_queries: list[VectorQuery]
        :keyword vector_filter_mode: Determines whether or not filters are applied before or after the
             vector search is performed. Default is 'preFilter'. Known values are: "postFilter" and "preFilter".
        :paramtype vector_filter_mode: str or VectorFilterMode
        :return: A list of documents (dicts) matching the specified search criteria.
        :return: List of search results.
        :rtype:  AsyncSearchItemPaged[dict]

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

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_facet_query_async.py
                :start-after: [START facet_query_async]
                :end-before: [END facet_query_async]
                :language: python
                :dedent: 4
                :caption: Get search result facets.
        """
        include_total_result_count = include_total_count
        filter_arg = filter
        search_fields_str = ",".join(search_fields) if search_fields else None
        answers = get_answer_query(query_answer, query_answer_count, query_answer_threshold)
        captions = (
            query_caption
            if not query_caption_highlight_enabled
            else "{}|highlight-{}".format(query_caption, query_caption_highlight_enabled)
        )
        semantic_configuration = semantic_configuration_name

        query = SearchQuery(
            search_text=search_text,
            include_total_result_count=include_total_result_count,
            facets=facets,
            filter=filter_arg,
            highlight_fields=highlight_fields,
            highlight_post_tag=highlight_post_tag,
            highlight_pre_tag=highlight_pre_tag,
            minimum_coverage=minimum_coverage,
            order_by=order_by if isinstance(order_by, str) else None,
            query_type=query_type,
            scoring_parameters=scoring_parameters,
            scoring_profile=scoring_profile,
            semantic_query=semantic_query,
            search_fields=search_fields_str,
            search_mode=search_mode,
            answers=answers,
            captions=captions,
            semantic_configuration=semantic_configuration,
            select=select if isinstance(select, str) else None,
            skip=skip,
            top=top,
            session_id=session_id,
            scoring_statistics=scoring_statistics,
            vector_queries=vector_queries,
            vector_filter_mode=vector_filter_mode,
            semantic_error_handling=semantic_error_mode,
            semantic_max_wait_in_milliseconds=semantic_max_wait_in_milliseconds,
        )
        if isinstance(select, list):
            query.select(select)
        if isinstance(order_by, list):
            query.order_by(order_by)
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        kwargs["api_version"] = self._api_version
        return AsyncSearchItemPaged(self._client, query, kwargs, page_iterator_class=AsyncSearchPageIterator)

    @distributed_trace_async
    async def suggest(
        self,
        search_text: str,
        suggester_name: str,
        *,
        filter: Optional[str] = None,
        use_fuzzy_matching: Optional[bool] = None,
        highlight_post_tag: Optional[str] = None,
        highlight_pre_tag: Optional[str] = None,
        minimum_coverage: Optional[float] = None,
        order_by: Optional[List[str]] = None,
        search_fields: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        top: Optional[int] = None,
        **kwargs
    ) -> List[Dict]:
        """Get search suggestion results from the Azure search index.

        :param str search_text: Required. The search text to use to suggest documents. Must be at least 1
            character, and no more than 100 characters.
        :param str suggester_name: Required. The name of the suggester as specified in the suggesters
            collection that's part of the index definition.
        :keyword str filter: An OData expression that filters the documents considered for suggestions.
        :keyword bool use_fuzzy_matching: A value indicating whether to use fuzzy matching for the suggestions
            query. Default is false. When set to true, the query will find terms even if there's a
            substituted or missing character in the search text. While this provides a better experience in
            some scenarios, it comes at a performance cost as fuzzy suggestions queries are slower and
            consume more resources.
        :keyword str highlight_post_tag: A string tag that is appended to hit highlights. Must be set with
            highlightPreTag. If omitted, hit highlighting of suggestions is disabled.
        :keyword str highlight_pre_tag: A string tag that is prepended to hit highlights. Must be set with
            highlightPostTag. If omitted, hit highlighting of suggestions is disabled.
        :keyword float minimum_coverage: A number between 0 and 100 indicating the percentage of the index that
            must be covered by a suggestions query in order for the query to be reported as a success. This
            parameter can be useful for ensuring search availability even for services with only one
            replica. The default is 80.
        :keyword list[str] order_by: The list of OData $orderby expressions by which to sort the results. Each
            expression can be either a field name or a call to either the geo.distance() or the
            search.score() functions. Each expression can be followed by asc to indicate ascending, or desc
            to indicate descending. The default is ascending order. Ties will be broken by the match scores
            of documents. If no $orderby is specified, the default sort order is descending by document
            match score. There can be at most 32 $orderby clauses.
        :keyword list[str] search_fields: The list of field names to search for the specified search text. Target
            fields must be included in the specified suggester.
        :keyword list[str] select: The list of fields to retrieve. If unspecified, only the key field will be
            included in the results.
        :keyword int top: The number of suggestions to retrieve. The value must be a number between 1 and
            100. The default is 5.
        :return: List of suggestion results.
        :rtype:  list[dict]

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_suggestions_async.py
                :start-after: [START suggest_query_async]
                :end-before: [END suggest_query_async]
                :language: python
                :dedent: 4
                :caption: Get search suggestions.
        """
        filter_arg = filter
        search_fields_str = ",".join(search_fields) if search_fields else None
        query = SuggestQuery(
            search_text=search_text,
            suggester_name=suggester_name,
            filter=filter_arg,
            use_fuzzy_matching=use_fuzzy_matching,
            highlight_post_tag=highlight_post_tag,
            highlight_pre_tag=highlight_pre_tag,
            minimum_coverage=minimum_coverage,
            order_by=order_by if isinstance(order_by, str) else None,
            search_fields=search_fields_str,
            select=select if isinstance(select, str) else None,
            top=top,
        )
        if isinstance(select, list):
            query.select(select)
        if isinstance(order_by, list):
            query.order_by(order_by)
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        request = cast(SuggestRequest, query.request)
        response = await self._client.documents.suggest_post(suggest_request=request, **kwargs)
        assert response.results is not None  # Hint for mypy
        results = [r.as_dict() for r in response.results]
        return results

    @distributed_trace_async
    async def autocomplete(
        self,
        search_text: str,
        suggester_name: str,
        *,
        mode: Optional[Union[str, AutocompleteMode]] = None,
        filter: Optional[str] = None,
        use_fuzzy_matching: Optional[bool] = None,
        highlight_post_tag: Optional[str] = None,
        highlight_pre_tag: Optional[str] = None,
        minimum_coverage: Optional[float] = None,
        search_fields: Optional[List[str]] = None,
        top: Optional[int] = None,
        **kwargs
    ) -> List[Dict]:
        """Get search auto-completion results from the Azure search index.

        :param str search_text: The search text on which to base autocomplete results.
        :param str suggester_name: The name of the suggester as specified in the suggesters
            collection that's part of the index definition.
        :keyword mode: Specifies the mode for Autocomplete. The default is 'oneTerm'. Use
            'twoTerms' to get shingles and 'oneTermWithContext' to use the current context while producing
            auto-completed terms. Possible values include: 'oneTerm', 'twoTerms', 'oneTermWithContext'.
        :paramtype mode: str or ~azure.search.documents.models.AutocompleteMode
        :keyword str filter: An OData expression that filters the documents used to produce completed terms
            for the Autocomplete result.
        :keyword bool use_fuzzy_matching: A value indicating whether to use fuzzy matching for the
            autocomplete query. Default is false. When set to true, the query will find terms even if
            there's a substituted or missing character in the search text. While this provides a better
            experience in some scenarios, it comes at a performance cost as fuzzy autocomplete queries are
            slower and consume more resources.
        :keyword str highlight_post_tag: A string tag that is appended to hit highlights. Must be set with
            highlightPreTag. If omitted, hit highlighting is disabled.
        :keyword str highlight_pre_tag: A string tag that is prepended to hit highlights. Must be set with
            highlightPostTag. If omitted, hit highlighting is disabled.
        :keyword float minimum_coverage: A number between 0 and 100 indicating the percentage of the index that
            must be covered by an autocomplete query in order for the query to be reported as a success.
            This parameter can be useful for ensuring search availability even for services with only one
            replica. The default is 80.
        :keyword list[str] search_fields: The list of field names to consider when querying for auto-completed
            terms. Target fields must be included in the specified suggester.
        :keyword int top: The number of auto-completed terms to retrieve. This must be a value between 1 and
            100. The default is 5.
        :return: List of auto-completion results.
        :rtype:  list[Dict]

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_autocomplete_async.py
                :start-after: [START autocomplete_query_async]
                :end-before: [END autocomplete_query_async]
                :language: python
                :dedent: 4
                :caption: Get a auto-completions.
        """
        autocomplete_mode = mode
        filter_arg = filter
        search_fields_str = ",".join(search_fields) if search_fields else None
        query = AutocompleteQuery(
            search_text=search_text,
            suggester_name=suggester_name,
            autocomplete_mode=autocomplete_mode,
            filter=filter_arg,
            use_fuzzy_matching=use_fuzzy_matching,
            highlight_post_tag=highlight_post_tag,
            highlight_pre_tag=highlight_pre_tag,
            minimum_coverage=minimum_coverage,
            search_fields=search_fields_str,
            top=top,
        )

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        request = cast(AutocompleteRequest, query.request)
        response = await self._client.documents.autocomplete_post(autocomplete_request=request, **kwargs)
        assert response.results is not None  # Hint for mypy
        results = [r.as_dict() for r in response.results]
        return results

    # pylint:disable=client-method-missing-tracing-decorator-async
    async def upload_documents(self, documents: List[Dict], **kwargs: Any) -> List[IndexingResult]:
        """Upload documents to the Azure search index.

        An upload action is similar to an "upsert" where the document will be
        inserted if it is new and updated/replaced if it exists. All fields are
        replaced in the update case.

        :param documents: A list of documents to upload.
        :type documents: list[dict]
        :return: List of IndexingResult
        :rtype:  list[IndexingResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_crud_operations_async.py
                :start-after: [START upload_document_async]
                :end-before: [END upload_document_async]
                :language: python
                :dedent: 4
                :caption: Upload new documents to an index
        """
        batch = IndexDocumentsBatch()
        batch.add_upload_actions(documents)

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        results = await self.index_documents(batch, **kwargs)
        return cast(List[IndexingResult], results)

    # pylint:disable=client-method-missing-tracing-decorator-async, delete-operation-wrong-return-type
    async def delete_documents(self, documents: List[Dict], **kwargs: Any) -> List[IndexingResult]:
        """Delete documents from the Azure search index

        Delete removes the specified document from the index. Any field you
        specify in a delete operation, other than the key field, will be
        ignored. If you want to remove an individual field from a document, use
        `merge_documents` instead and set the field explicitly to None.

        Delete operations are idempotent. That is, even if a document key does
        not exist in the index, attempting a delete operation with that key will
        result in a 200 status code.

        :param documents: A list of documents to delete.
        :type documents: list[dict]
        :return: List of IndexingResult
        :rtype:  list[IndexingResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_crud_operations_async.py
                :start-after: [START delete_document_async]
                :end-before: [END delete_document_async]
                :language: python
                :dedent: 4
                :caption: Delete existing documents to an index
        """
        batch = IndexDocumentsBatch()
        batch.add_delete_actions(documents)

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        results = await self.index_documents(batch, **kwargs)
        return cast(List[IndexingResult], results)

    # pylint:disable=client-method-missing-tracing-decorator-async
    async def merge_documents(self, documents: List[Dict], **kwargs: Any) -> List[IndexingResult]:
        """Merge documents in to existing documents in the Azure search index.

        Merge updates an existing document with the specified fields. If the
        document doesn't exist, the merge will fail. Any field you specify in a
        merge will replace the existing field in the document. This also applies
        to collections of primitive and complex types.

        :param documents: A list of documents to merge.
        :type documents: list[dict]
        :return: List of IndexingResult
        :rtype:  list[IndexingResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_crud_operations_async.py
                :start-after: [START merge_document_async]
                :end-before: [END merge_document_async]
                :language: python
                :dedent: 4
                :caption: Merge fields into existing documents to an index
        """
        batch = IndexDocumentsBatch()
        batch.add_merge_actions(documents)

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        results = await self.index_documents(batch, **kwargs)
        return cast(List[IndexingResult], results)

    # pylint:disable=client-method-missing-tracing-decorator-async
    async def merge_or_upload_documents(self, documents: List[Dict], **kwargs: Any) -> List[IndexingResult]:
        """Merge documents in to existing documents in the Azure search index,
        or upload them if they do not yet exist.

        This action behaves like `merge_documents` if a document with the given
        key already exists in the index. If the document does not exist, it
        behaves like `upload_documents` with a new document.

        :param documents: A list of documents to merge or upload.
        :type documents: list[dict]
        :return: List of IndexingResult
        :rtype:  list[IndexingResult]
        """
        batch = IndexDocumentsBatch()
        batch.add_merge_or_upload_actions(documents)

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        results = await self.index_documents(batch, **kwargs)
        return cast(List[IndexingResult], results)

    @distributed_trace_async
    async def index_documents(self, batch: IndexDocumentsBatch, **kwargs: Any) -> List[IndexingResult]:
        """Specify a document operations to perform as a batch.

        :param batch: A batch of document operations to perform.
        :type batch: IndexDocumentsBatch
        :return: List of IndexingResult
        :rtype:  list[IndexingResult]

        :raises ~azure.search.documents.RequestEntityTooLargeError
        """
        return await self._index_documents_actions(actions=batch.actions, **kwargs)

    async def _index_documents_actions(self, actions: List[IndexAction], **kwargs: Any) -> List[IndexingResult]:
        error_map = {413: RequestEntityTooLargeError}

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        batch = IndexBatch(actions=actions)
        try:
            batch_response = await self._client.documents.index(batch=batch, error_map=error_map, **kwargs)
            return cast(List[IndexingResult], batch_response.results)
        except RequestEntityTooLargeError:
            if len(actions) == 1:
                raise
            pos = round(len(actions) / 2)
            batch_response_first_half = await self._index_documents_actions(
                actions=actions[:pos], error_map=error_map, **kwargs
            )
            if batch_response_first_half:
                result_first_half = batch_response_first_half
            else:
                result_first_half = []
            batch_response_second_half = await self._index_documents_actions(
                actions=actions[pos:], error_map=error_map, **kwargs
            )
            if batch_response_second_half:
                result_second_half = batch_response_second_half
            else:
                result_second_half = []
            result_first_half.extend(result_second_half)
            return result_first_half

    async def __aenter__(self) -> "SearchClient":
        await self._client.__aenter__()  # pylint: disable=no-member
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)

    @distributed_trace_async
    async def send_request(self, request: HttpRequest, *, stream: bool = False, **kwargs) -> AsyncHttpResponse:
        """Runs a network request using the client's existing pipeline.

        :param request: The network request you want to make.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.AsyncHttpResponse
        """
        request.headers = self._merge_client_headers(request.headers)
        return await self._client._send_request(request, stream=stream, **kwargs)  # pylint:disable=protected-access
