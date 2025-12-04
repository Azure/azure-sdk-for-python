# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Dict, List, Optional, Union, cast

from azure.core.async_paging import AsyncItemPaged, AsyncPageIterator, ReturnType
from azure.core.tracing.decorator_async import distributed_trace_async

from ._operations import _SearchClientOperationsMixin as _SearchClientOperationsMixinGenerated
from ..._operations._patch import (
    _build_search_request,
    _convert_search_result,
    _pack_continuation_token,
    _unpack_continuation_token,
)
from ...models._patch import RequestEntityTooLargeError
from ... import models as _models


def _ensure_response(f):
    """Decorator to ensure response is fetched before accessing metadata.
    :param f: The function to wrap.
    :type f: Callable
    :return: The wrapped function.
    :rtype: Callable
    """

    async def wrapper(self, *args, **kw):
        # pylint:disable=protected-access
        if self._current_page is None:
            self._response = await self._get_next(self.continuation_token)
            self.continuation_token, self._current_page = await self._extract_data(self._response)
        return await f(self, *args, **kw)

    return wrapper


class AsyncSearchPageIterator(AsyncPageIterator):
    """An async iterator over search result pages."""

    def __init__(self, client, initial_request: _models.SearchRequest, kwargs, continuation_token=None) -> None:
        super(AsyncSearchPageIterator, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token,
        )
        self._client = client
        self._initial_request = initial_request
        self._kwargs = kwargs
        self._facets: Optional[Dict[str, List[Dict[str, Any]]]] = None
        self._api_version = kwargs.get("api_version", "2025-11-01-preview")

    async def _get_next_cb(self, continuation_token):
        if continuation_token is None:
            return await self._client._search_post(  # pylint:disable=protected-access
                body=self._initial_request, **self._kwargs
            )

        _next_link, next_page_request = _unpack_continuation_token(continuation_token)
        return await self._client._search_post(  # pylint:disable=protected-access
            body=next_page_request, **self._kwargs
        )

    async def _extract_data_cb(self, response: _models.SearchDocumentsResult):
        continuation_token = _pack_continuation_token(response, api_version=self._api_version)
        results = [_convert_search_result(r) for r in response.results]
        return continuation_token, results

    @_ensure_response
    async def get_facets(self) -> Optional[Dict[str, Any]]:
        self.continuation_token = None
        response = cast(_models.SearchDocumentsResult, self._response)
        if response.facets is not None and self._facets is None:
            self._facets = {
                k: [x.as_dict() if hasattr(x, "as_dict") else dict(x) for x in v] for k, v in response.facets.items()
            }
        return self._facets

    @_ensure_response
    async def get_coverage(self) -> Optional[float]:
        self.continuation_token = None
        response = cast(_models.SearchDocumentsResult, self._response)
        return response.coverage

    @_ensure_response
    async def get_count(self) -> Optional[int]:
        self.continuation_token = None
        response = cast(_models.SearchDocumentsResult, self._response)
        return response.count

    @_ensure_response
    async def get_answers(self) -> Optional[List[_models.QueryAnswerResult]]:
        self.continuation_token = None
        response = cast(_models.SearchDocumentsResult, self._response)
        return response.answers

    @_ensure_response
    async def get_debug_info(self) -> Optional[_models.DebugInfo]:
        self.continuation_token = None
        response = cast(_models.SearchDocumentsResult, self._response)
        return response.debug_info


class AsyncSearchItemPaged(AsyncItemPaged[ReturnType]):
    """An async pageable list of search results with metadata accessors."""

    def __init__(self, page_iterator_factory_func) -> None:
        super(AsyncSearchItemPaged, self).__init__()
        # Store the factory function that creates AsyncSearchPageIterator instances
        self._page_iterator_factory = page_iterator_factory_func
        self._first_page_iterator_instance: Optional[AsyncSearchPageIterator] = None
        self._page_iterator = None
        self._page = None

    def by_page(self, continuation_token=None):
        """Get an async iterator of pages of results.

        :param continuation_token: Token to retrieve the next page of results
        :type continuation_token: str or None
        :return: An async iterator of pages
        :rtype: AsyncSearchPageIterator
        """
        return self._page_iterator_factory(continuation_token)

    async def __anext__(self) -> ReturnType:
        if self._page_iterator is None:
            self._page_iterator = self.by_page()
            self._first_page_iterator_instance = cast(AsyncSearchPageIterator, self._page_iterator)
        if self._page is None:
            self._page = await self._page_iterator.__anext__()
        try:
            return await self._page.__anext__()
        except StopAsyncIteration:
            self._page = None
            return await self.__anext__()

    async def _first_iterator_instance(self) -> AsyncSearchPageIterator:
        if self._first_page_iterator_instance is None:
            self._first_page_iterator_instance = cast(AsyncSearchPageIterator, self.by_page())
        return self._first_page_iterator_instance

    async def get_facets(self) -> Optional[Dict]:
        """Return any facet results if faceting was requested.

        :return: facet results
        :rtype: dict or None
        """
        return await (await self._first_iterator_instance()).get_facets()

    async def get_coverage(self) -> Optional[float]:
        """Return the coverage percentage, if `minimum_coverage` was
        specified for the query.

        :return: coverage percentage
        :rtype: float or None
        """
        return await (await self._first_iterator_instance()).get_coverage()

    async def get_count(self) -> Optional[int]:
        """Return the count of results if `include_total_count` was
        set for the query.

        :return: count of results
        :rtype: int or None
        """
        return await (await self._first_iterator_instance()).get_count()

    async def get_answers(self) -> Optional[List[_models.QueryAnswerResult]]:
        """Return semantic answers. Only included if the semantic ranker is used
        and answers are requested in the search query via the query_answer parameter.

        :return: answers
        :rtype: list[~azure.search.documents.models.QueryAnswerResult] or None
        """
        return await (await self._first_iterator_instance()).get_answers()

    async def get_debug_info(self) -> Optional[_models.DebugInfo]:
        """Return the debug information for the query.

        :return: the debug information for the query
        :rtype: ~azure.search.documents.models.DebugInfo or None
        """
        return await (await self._first_iterator_instance()).get_debug_info()


class _SearchClientOperationsMixin(_SearchClientOperationsMixinGenerated):
    """Async SearchClient operations mixin customizations."""

    @distributed_trace_async
    async def index_documents(self, batch: _models.IndexDocumentsBatch, **kwargs: Any) -> List[_models.IndexingResult]:
        """Specify a document operations to perform as a batch.

        :param batch: A batch of document operations to perform.
        :type batch: IndexDocumentsBatch
        :return: List of IndexingResult
        :rtype:  list[IndexingResult]

        :raises ~azure.search.documents.RequestEntityTooLargeError: The request is too large.
        """
        return await self._index_documents_actions(batch=batch, **kwargs)

    async def _index_documents_actions(
        self, batch: _models.IndexDocumentsBatch, **kwargs: Any
    ) -> List[_models.IndexingResult]:
        error_map = {413: RequestEntityTooLargeError}

        try:
            batch_response = await self._index(batch=batch, error_map=error_map, **kwargs)
            typed_result = [cast(_models.IndexingResult, x) for x in batch_response.results]
            return typed_result
        except RequestEntityTooLargeError:
            if len(batch.actions) == 1:
                raise
            pos = round(len(batch.actions) / 2)
            batch_response_first_half = await self._index_documents_actions(
                batch=_models.IndexDocumentsBatch(actions=batch.actions[:pos]), **kwargs
            )
            if batch_response_first_half:
                result_first_half = batch_response_first_half
            else:
                result_first_half = []
            batch_response_second_half = await self._index_documents_actions(actions=batch.actions[pos:], **kwargs)
            if batch_response_second_half:
                result_second_half = batch_response_second_half
            else:
                result_second_half = []
            result_first_half.extend(result_second_half)
            return result_first_half

    async def upload_documents(self, documents: List[Dict], **kwargs: Any) -> List[_models.IndexingResult]:
        """Upload documents to the Azure search index.

        An upload action is similar to an "upsert" where the document will be
        inserted if it is new and updated/replaced if it exists. All fields are
        replaced in the update case.

        :param documents: A list of documents to upload.
        :type documents: list[dict]
        :return: List of IndexingResult
        :rtype: list[~azure.search.documents.models.IndexingResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_crud_operations_async.py
                :start-after: [START upload_document]
                :end-before: [END upload_document]
                :language: python
                :dedent: 4
                :caption: Upload new documents to an index
        """
        batch = _models.IndexDocumentsBatch()
        batch.add_upload_actions(documents)

        result = await self.index_documents(batch, **kwargs)
        return result

    async def delete_documents(self, documents: List[Dict], **kwargs: Any) -> List[_models.IndexingResult]:
        """Delete documents from the Azure search index.

        Delete removes the specified documents from the index. Any field you
        specify in a delete operation, other than the key field, will be ignored.
        If you want to remove a field from a document, use merge instead and
        set the field explicitly to None.

        :param documents: A list of documents to delete.
        :type documents: list[dict]
        :return: List of IndexingResult
        :rtype: list[~azure.search.documents.models.IndexingResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_crud_operations_async.py
                :start-after: [START delete_document]
                :end-before: [END delete_document]
                :language: python
                :dedent: 4
                :caption: Delete documents from an index
        """
        batch = _models.IndexDocumentsBatch()
        batch.add_delete_actions(documents)

        result = await self.index_documents(batch, **kwargs)
        return result

    async def merge_documents(self, documents: List[Dict], **kwargs: Any) -> List[_models.IndexingResult]:
        """Merge documents in the Azure search index.

        Merge updates an existing document with the specified fields. If the
        document doesn't exist, the merge will fail. Any field you specify in
        a merge will replace the existing field in the document. This also
        applies to collections of primitive and complex types.

        :param documents: A list of documents to merge.
        :type documents: list[dict]
        :return: List of IndexingResult
        :rtype: list[~azure.search.documents.models.IndexingResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_crud_operations_async.py
                :start-after: [START merge_document]
                :end-before: [END merge_document]
                :language: python
                :dedent: 4
                :caption: Merge documents in an index
        """
        batch = _models.IndexDocumentsBatch()
        batch.add_merge_actions(documents)

        result = await self.index_documents(batch, **kwargs)
        return result

    async def merge_or_upload_documents(self, documents: List[Dict], **kwargs: Any) -> List[_models.IndexingResult]:
        """Merge or upload documents to the Azure search index.

        Merge or upload behaves like merge if a document with the given key
        already exists in the index. If the document does not exist, it behaves
        like upload with a new document.

        :param documents: A list of documents to merge or upload.
        :type documents: list[dict]
        :return: List of IndexingResult
        :rtype: list[~azure.search.documents.models.IndexingResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_crud_operations_async.py
                :start-after: [START merge_or_upload_document]
                :end-before: [END merge_or_upload_document]
                :language: python
                :dedent: 4
                :caption: Merge or upload documents to an index
        """
        batch = _models.IndexDocumentsBatch()
        batch.add_merge_or_upload_actions(documents)

        result = await self.index_documents(batch, **kwargs)
        return result

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
        order_by: Optional[Union[List[str], str]] = None,
        query_type: Optional[Union[str, _models.QueryType]] = None,
        scoring_parameters: Optional[List[str]] = None,
        scoring_profile: Optional[str] = None,
        semantic_query: Optional[str] = None,
        search_fields: Optional[Union[List[str], str]] = None,
        search_mode: Optional[Union[str, _models.SearchMode]] = None,
        query_language: Optional[Union[str, _models.QueryLanguage]] = None,
        query_speller: Optional[Union[str, _models.QuerySpellerType]] = None,
        query_answer: Optional[Union[str, _models.QueryAnswerType]] = None,
        query_answer_count: Optional[int] = None,
        query_answer_threshold: Optional[float] = None,
        query_caption: Optional[Union[str, _models.QueryCaptionType]] = None,
        query_caption_highlight_enabled: Optional[bool] = None,
        semantic_fields: Optional[Union[List[str], str]] = None,
        semantic_configuration_name: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        skip: Optional[int] = None,
        top: Optional[int] = None,
        scoring_statistics: Optional[Union[str, _models.ScoringStatistics]] = None,
        session_id: Optional[str] = None,
        vector_queries: Optional[List[_models.VectorQuery]] = None,
        vector_filter_mode: Optional[Union[str, _models.VectorFilterMode]] = None,
        semantic_error_mode: Optional[Union[str, _models.SemanticErrorMode]] = None,
        semantic_max_wait_in_milliseconds: Optional[int] = None,
        query_rewrites: Optional[Union[str, _models.QueryRewritesType]] = None,
        query_rewrites_count: Optional[int] = None,
        debug: Optional[Union[str, _models.QueryDebugMode]] = None,
        hybrid_search: Optional[_models.HybridSearch] = None,
        **kwargs: Any,
    ) -> AsyncSearchItemPaged[Dict]:
        # pylint:disable=too-many-locals
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
        :keyword order_by: The list of OData $orderby expressions by which to sort the results. Each
            expression can be either a field name or a call to either the geo.distance() or the
            search.score() functions. Each expression can be followed by asc to indicate ascending, and
            desc to indicate descending. The default is ascending order. Ties will be broken by the match
            scores of documents. If no OrderBy is specified, the default sort order is descending by
            document match score. There can be at most 32 $orderby clauses.
        :paramtype order_by: list[str] or str
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
        :keyword search_fields: The list of field names to which to scope the full-text search. When
            using fielded search (fieldName:searchExpression) in a full Lucene query, the field names of
            each fielded search expression take precedence over any field names listed in this parameter.
        :paramtype search_fields: list[str] or str
        :keyword search_mode: A value that specifies whether any or all of the search terms must be
            matched in order to count the document as a match. Possible values include: 'any', 'all'.
        :paramtype search_mode: str or ~azure.search.documents.models.SearchMode
        :keyword query_language: The language of the search query. Possible values include: "none", "en-us",
            "en-gb", "en-in", "en-ca", "en-au", "fr-fr", "fr-ca", "de-de", "es-es", "es-mx", "zh-cn",
            "zh-tw", "pt-br", "pt-pt", "it-it", "ja-jp", "ko-kr", "ru-ru", "cs-cz", "nl-be", "nl-nl",
            "hu-hu", "pl-pl", "sv-se", "tr-tr", "hi-in", "ar-sa", "ar-eg", "ar-ma", "ar-kw", "ar-jo",
            "da-dk", "no-no", "bg-bg", "hr-hr", "hr-ba", "ms-my", "ms-bn", "sl-sl", "ta-in", "vi-vn",
            "el-gr", "ro-ro", "is-is", "id-id", "th-th", "lt-lt", "uk-ua", "lv-lv", "et-ee", "ca-es",
            "fi-fi", "sr-ba", "sr-me", "sr-rs", "sk-sk", "nb-no", "hy-am", "bn-in", "eu-es", "gl-es",
            "gu-in", "he-il", "ga-ie", "kn-in", "ml-in", "mr-in", "fa-ae", "pa-in", "te-in", "ur-pk".
        :paramtype query_language: str or ~azure.search.documents.models.QueryLanguage
        :keyword query_speller: A value that specified the type of the speller to use to spell-correct
            individual search query terms. Possible values include: "none", "lexicon".
        :paramtype query_speller: str or ~azure.search.documents.models.QuerySpellerType
        :keyword query_answer: This parameter is only valid if the query type is 'semantic'. If set,
            the query returns answers extracted from key passages in the highest ranked documents.
            Possible values include: "none", "extractive".
        :paramtype query_answer: str or ~azure.search.documents.models.QueryAnswerType
        :keyword int query_answer_count: This parameter is only valid if the query type is 'semantic' and
            query answer is 'extractive'. Configures the number of answers returned. Default count is 1.
        :keyword float query_answer_threshold: This parameter is only valid if the query type is 'semantic' and
            query answer is 'extractive'. Configures the number of confidence threshold. Default count is 0.7.
        :keyword query_caption: This parameter is only valid if the query type is 'semantic'. If set, the
            query returns captions extracted from key passages in the highest ranked documents.
            Defaults to 'None'. Possible values include: "none", "extractive".
        :paramtype query_caption: str or ~azure.search.documents.models.QueryCaptionType
        :keyword bool query_caption_highlight_enabled: This parameter is only valid if the query type is 'semantic' when
            query caption is set to 'extractive'. Determines whether highlighting is enabled.
            Defaults to 'true'.
        :keyword semantic_fields: The list of field names used for semantic search.
        :paramtype semantic_fields: list[str] or str
        :keyword semantic_configuration_name: The name of the semantic configuration that will be used when
            processing documents for queries of type semantic.
        :paramtype semantic_configuration_name: str
        :keyword select: The list of fields to retrieve. If unspecified, all fields marked as retrievable
            in the schema are included.
        :paramtype select: list[str] or str
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
        :keyword query_rewrites: When QueryRewrites is set to ``generative``\\ , the query terms are sent
            to a generate model which will produce 10 (default) rewrites to help increase the recall of the
            request. The requested count can be configured by appending the pipe character ``|`` followed
            by the ``count-<number of rewrites>`` option, such as ``generative|count-3``. Defaults to
            ``None``. This parameter is only valid if the query type is ``semantic``. Known values are:
            "none" and "generative".
        :paramtype query_rewrites: str or ~azure.search.documents.models.QueryRewritesType
        :keyword int query_rewrites_count: This parameter is only valid if the query rewrites type is 'generative'.
            Configures the number of rewrites returned. Default count is 10.
        :keyword debug: Enables a debugging tool that can be used to further explore your Semantic search
            results. Known values are: "disabled", "speller", "semantic", and "all".
        :paramtype debug: str or ~azure.search.documents.models.QueryDebugMode
        :keyword vector_queries: The query parameters for vector and hybrid search queries.
        :paramtype vector_queries: list[~azure.search.documents.models.VectorQuery]
        :keyword vector_filter_mode: Determines whether or not filters are applied before or after the
            vector search is performed. Default is 'preFilter'. Known values are: "postFilter" and "preFilter".
        :paramtype vector_filter_mode: str or ~azure.search.documents.models.VectorFilterMode
        :keyword hybrid_search: The query parameters to configure hybrid search behaviors.
        :paramtype hybrid_search: ~azure.search.documents.models.HybridSearch
        :keyword enable_elevated_read: A value that enables elevated read that bypass document level
            permission checks for the query operation. Default value is None.
        :paramtype enable_elevated_read: bool
        :return: A list of documents (dicts) matching the specified search criteria.
        :return: List of search results.
        :rtype: AsyncSearchItemPaged[dict]

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
        # Build the search request using shared helper
        search_request = _build_search_request(
            search_text=search_text,
            include_total_count=include_total_count,
            facets=facets,
            filter=filter,
            highlight_fields=highlight_fields,
            highlight_post_tag=highlight_post_tag,
            highlight_pre_tag=highlight_pre_tag,
            minimum_coverage=minimum_coverage,
            order_by=order_by,
            query_type=query_type,
            scoring_parameters=scoring_parameters,
            scoring_profile=scoring_profile,
            semantic_query=semantic_query,
            search_fields=search_fields,
            search_mode=search_mode,
            query_language=query_language,
            query_speller=query_speller,
            query_answer=query_answer,
            query_answer_count=query_answer_count,
            query_answer_threshold=query_answer_threshold,
            query_caption=query_caption,
            query_caption_highlight_enabled=query_caption_highlight_enabled,
            semantic_fields=semantic_fields,
            semantic_configuration_name=semantic_configuration_name,
            select=select,
            skip=skip,
            top=top,
            scoring_statistics=scoring_statistics,
            session_id=session_id,
            vector_queries=vector_queries,
            vector_filter_mode=vector_filter_mode,
            semantic_error_mode=semantic_error_mode,
            semantic_max_wait_in_milliseconds=semantic_max_wait_in_milliseconds,
            query_rewrites=query_rewrites,
            query_rewrites_count=query_rewrites_count,
            debug=debug,
            hybrid_search=hybrid_search,
        )

        # Create kwargs for the search_post call
        search_kwargs = dict(kwargs)

        # Create a factory function that returns an async page iterator
        def page_iterator_factory(continuation_token=None):
            return AsyncSearchPageIterator(
                client=self, initial_request=search_request, kwargs=search_kwargs, continuation_token=continuation_token
            )

        # Return AsyncSearchItemPaged with the factory function
        return AsyncSearchItemPaged(page_iterator_factory)

    @distributed_trace_async
    async def autocomplete(
        self,
        search_text: str,
        suggester_name: str,
        *,
        autocomplete_mode: Optional[Union[str, _models.AutocompleteMode]] = None,
        filter: Optional[str] = None,
        use_fuzzy_matching: Optional[bool] = None,
        highlight_post_tag: Optional[str] = None,
        highlight_pre_tag: Optional[str] = None,
        minimum_coverage: Optional[float] = None,
        search_fields: Optional[str] = None,
        top: Optional[int] = None,
        **kwargs: Any,
    ) -> List[_models.AutocompleteItem]:
        """Autocomplete incomplete search terms based on input text and matching terms in the index.

        :param str search_text: The search text on which to base autocomplete results.
        :param str suggester_name: The name of the suggester as specified in the suggesters
            collection that's part of the index definition.
        :keyword autocomplete_mode: Specifies the mode for Autocomplete. The default is 'oneTerm'.
            Use 'twoTerms' to get shingles and 'oneTermWithContext' to use the current context while
            producing auto-completed terms. Known values are: "oneTerm", "twoTerms", and
            "oneTermWithContext".
        :paramtype autocomplete_mode: str or ~azure.search.documents.models.AutocompleteMode
        :keyword str filter: An OData expression that filters the documents used to produce completed
            terms for the Autocomplete result.
        :keyword bool use_fuzzy_matching: A value indicating whether to use fuzzy matching for the
            autocomplete query. Default is false. When set to true, the query will find terms even if
            there's a substituted or missing character in the search text. While this provides a better
            experience in some scenarios, it comes at a performance cost as fuzzy autocomplete queries are
            slower and consume more resources.
        :keyword str highlight_post_tag: A string tag that is appended to hit highlights. Must be set with
            highlightPreTag. If omitted, hit highlighting is disabled.
        :keyword str highlight_pre_tag: A string tag that is prepended to hit highlights. Must be set with
            highlightPostTag. If omitted, hit highlighting is disabled.
        :keyword float minimum_coverage: A number between 0 and 100 indicating the percentage of the index
            that must be covered by an autocomplete query in order for the query to be reported as a
            success. This parameter can be useful for ensuring search availability even for services with
            only one replica. The default is 80.
        :keyword str search_fields: The comma-separated list of field names to consider when querying for
            auto-completed terms. Target fields must be included in the specified suggester.
        :keyword int top: The number of auto-completed terms to retrieve. This must be a value between 1
            and 100. The default is 5.
        :return: List of autocomplete results.
        :rtype: list[dict[str, Any]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_autocomplete_async.py
                :start-after: [START autocomplete_query_async]
                :end-before: [END autocomplete_query_async]
                :language: python
                :dedent: 4
                :caption: Get autocomplete suggestions.
        """
        # Call the generated _autocomplete_post method
        response = await self._autocomplete_post(
            search_text=search_text,
            suggester_name=suggester_name,
            autocomplete_mode=autocomplete_mode,
            filter=filter,
            use_fuzzy_matching=use_fuzzy_matching,
            highlight_post_tag=highlight_post_tag,
            highlight_pre_tag=highlight_pre_tag,
            minimum_coverage=minimum_coverage,
            search_fields=search_fields,
            top=top,
            **kwargs,
        )

        assert response.results is not None  # Hint for mypy
        return response.results

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
        order_by: Optional[str] = None,
        search_fields: Optional[str] = None,
        select: Optional[str] = None,
        top: Optional[int] = None,
        **kwargs: Any,
    ) -> List[_models.SuggestResult]:
        """Get search suggestions for documents in the Azure search index.

        :param str search_text: The search text to use to suggest documents. Must be at least 1
            character, and no more than 100 characters.
        :param str suggester_name: The name of the suggester as specified in the suggesters
            collection that's part of the index definition.
        :keyword str filter: An OData expression that filters the documents considered for suggestions.
        :keyword bool use_fuzzy_matching: A value indicating whether to use fuzzy matching for the
            suggestion query. Default is false. When set to true, the query will find suggestions even if
            there's a substituted or missing character in the search text. While this provides a better
            experience in some scenarios, it comes at a performance cost as fuzzy suggestion searches are
            slower and consume more resources.
        :keyword str highlight_post_tag: A string tag that is appended to hit highlights. Must be set with
            highlightPreTag. If omitted, hit highlighting of suggestions is disabled.
        :keyword str highlight_pre_tag: A string tag that is prepended to hit highlights. Must be set with
            highlightPostTag. If omitted, hit highlighting of suggestions is disabled.
        :keyword float minimum_coverage: A number between 0 and 100 indicating the percentage of the index
            that must be covered by a suggestion query in order for the query to be reported as a success.
            This parameter can be useful for ensuring search availability even for services with only one
            replica. The default is 80.
        :keyword str order_by: The comma-separated list of OData $orderby expressions by which to sort the
            results. Each expression can be either a field name or a call to either the geo.distance() or
            the search.score() functions. Each expression can be followed by asc to indicate ascending, or
            desc to indicate descending. The default is ascending order. Ties will be broken by the match
            scores of documents. If no $orderby is specified, the default sort order is descending by
            document match score. There can be at most 32 $orderby clauses.
        :keyword str search_fields: The comma-separated list of field names to search for the specified
            search text. Target fields must be included in the specified suggester.
        :keyword str select: The comma-separated list of fields to retrieve. If unspecified, only the key
            field will be included in the results.
        :keyword int top: The number of suggestions to retrieve. This must be a value between 1 and 100.
            The default is 5.
        :return: List of suggestion results.
        :rtype: list[dict[str, Any]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_suggestions_async.py
                :start-after: [START suggest]
                :end-before: [END suggest]
                :language: python
                :dedent: 4
                :caption: Get search suggestions.
        """
        # Call the generated _suggest_post method
        response = await self._suggest_post(
            search_text=search_text,
            suggester_name=suggester_name,
            filter=filter,
            use_fuzzy_matching=use_fuzzy_matching,
            highlight_post_tag=highlight_post_tag,
            highlight_pre_tag=highlight_pre_tag,
            minimum_coverage=minimum_coverage,
            order_by=order_by,
            search_fields=search_fields,
            select=select,
            top=top,
            **kwargs,
        )

        assert response.results is not None  # Hint for mypy
        return response.results


__all__: list[str] = [
    "_SearchClientOperationsMixin",
    "AsyncSearchItemPaged",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
