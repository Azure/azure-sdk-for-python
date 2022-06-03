# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import cast, List, TYPE_CHECKING, Union
import six

from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from ._paging import AsyncSearchItemPaged, AsyncSearchPageIterator
from ._utils_async import get_async_authentication_policy
from .._generated.aio import SearchClient as SearchIndexClient
from .._generated.models import IndexingResult
from .._search_documents_error import RequestEntityTooLargeError
from .._index_documents_batch import IndexDocumentsBatch
from .._queries import AutocompleteQuery, SearchQuery, SuggestQuery
from .._api_versions import DEFAULT_VERSION
from .._headers_mixin import HeadersMixin
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials_async import AsyncTokenCredential


class SearchClient(HeadersMixin):
    """A client to interact with an existing Azure search index.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param index_name: The name of the index to connect to
    :type index_name: str
    :param credential: A credential to authorize search client requests
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials_async.AsyncTokenCredential
    :keyword str api_version: The Search API version to use for requests.

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START create_search_client_with_key_async]
            :end-before: [END create_search_client_with_key_async]
            :language: python
            :dedent: 4
            :caption: Creating the SearchClient with an API key.
    """

    _ODATA_ACCEPT = "application/json;odata.metadata=none"  # type: str

    def __init__(
        self,
        endpoint: str,
        index_name: str,
        credential: Union[AzureKeyCredential, "AsyncTokenCredential"],
        **kwargs
    ) -> None:
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._index_documents_batch = IndexDocumentsBatch()
        self._endpoint = endpoint  # type: str
        self._index_name = index_name  # type: str
        self._credential = credential
        if isinstance(credential, AzureKeyCredential):
            self._aad = False
            self._client = SearchIndexClient(
                endpoint=endpoint,
                index_name=index_name,
                sdk_moniker=SDK_MONIKER,
                api_version=self._api_version,
                **kwargs
            )  # type: SearchIndexClient
        else:
            self._aad = True
            authentication_policy = get_async_authentication_policy(credential)
            self._client = SearchIndexClient(
                endpoint=endpoint,
                index_name=index_name,
                authentication_policy=authentication_policy,
                sdk_moniker=SDK_MONIKER,
                api_version=self._api_version,
                **kwargs
            )  # type: SearchIndexClient

    def __repr__(self):
        # type: () -> str
        return "<SearchClient [endpoint={}, index={}]>".format(
            repr(self._endpoint), repr(self._index_name)
        )[:1024]

    async def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.documents.aio.SearchClient` session."""
        return await self._client.close()

    @distributed_trace_async
    async def get_document_count(self, **kwargs):
        # type: (**Any) -> int
        """Return the number of documents in the Azure search index.

        :rtype: int
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        return int(await self._client.documents.count(**kwargs))

    @distributed_trace_async
    async def get_document(self, key, selected_fields=None, **kwargs):
        # type: (str, List[str], **Any) -> dict
        """Retrieve a document from the Azure search index by its key.

        :param key: The primary key value for the document to retrieve
        :type key: str
        :param selected_fields: a allowlist of fields to include in the results
        :type selected_fields: List[str]
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
        result = await self._client.documents.get(
            key=key, selected_fields=selected_fields, **kwargs
        )
        return cast(dict, result)


    @distributed_trace_async
    async def search(self, search_text, **kwargs): # pylint:disable=too-many-locals
        # type: (str, **Any) -> AsyncSearchItemPaged[dict]
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
        :keyword list[str] search_fields: The list of field names to which to scope the full-text search. When
         using fielded search (fieldName:searchExpression) in a full Lucene query, the field names of
         each fielded search expression take precedence over any field names listed in this parameter.
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
         query answer is 'extractive'.
         Configures the number of answers returned. Default count is 1.
        :keyword query_caption: This parameter is only valid if the query type is 'semantic'. If set, the
         query returns captions extracted from key passages in the highest ranked documents.
         Defaults to 'None'. Possible values include: "none", "extractive".
        :paramtype query_caption: str or ~azure.search.documents.models.QueryCaptionType
        :keyword bool query_caption_highlight: This parameter is only valid if the query type is 'semantic' when
         query caption is set to 'extractive'. Determines whether highlighting is enabled.
         Defaults to 'true'.
        :keyword list[str] semantic_fields: The list of field names used for semantic search.
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
        :keyword session_id: A value to be used to create a sticky session, which can help getting more
        consistent results. As long as the same sessionId is used, a best-effort attempt will be made
        to target the same replica set. Be wary that reusing the same sessionID values repeatedly can
        interfere with the load balancing of the requests across replicas and adversely affect the
        performance of the search service. The value used as sessionId cannot start with a '_'
        character.
        :paramtype session_id: str
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
        include_total_result_count = kwargs.pop("include_total_count", None)
        facets = kwargs.pop("facets", None)
        filter_arg = kwargs.pop("filter", None)
        highlight_fields = kwargs.pop("highlight_fields", None)
        highlight_post_tag = kwargs.pop("highlight_post_tag", None)
        highlight_pre_tag = kwargs.pop("highlight_pre_tag", None)
        minimum_coverage = kwargs.pop("minimum_coverage", None)
        order_by = kwargs.pop("order_by", None)
        query_type = kwargs.pop("query_type", None)
        scoring_parameters = kwargs.pop("scoring_parameters", None)
        scoring_profile = kwargs.pop("scoring_profile", None)
        search_fields = kwargs.pop("search_fields", None)
        search_fields_str = ",".join(search_fields) if search_fields else None
        search_mode = kwargs.pop("search_mode", None)
        query_language = kwargs.pop("query_language", None)
        query_speller = kwargs.pop("query_speller", None)
        select = kwargs.pop("select", None)
        skip = kwargs.pop("skip", None)
        top = kwargs.pop("top", None)
        session_id = kwargs.pop("session_id", None)
        scoring_statistics = kwargs.pop("scoring_statistics", None)

        query_answer = kwargs.pop("query_answer", None)
        query_answer_count = kwargs.pop("query_answer_count", None)
        answers = query_answer if not query_answer_count else '{}|count-{}'.format(
            query_answer, query_answer_count
        )

        query_caption = kwargs.pop("query_caption", None)
        query_caption_highlight = kwargs.pop("query_caption_highlight", None)
        captions = query_caption if not query_caption_highlight else '{}|highlight-{}'.format(
            query_caption, query_caption_highlight
        )

        semantic_fields = kwargs.pop("semantic_fields", None)
        semantic_configuration = kwargs.pop("semantic_configuration_name", None)

        query = SearchQuery(
            search_text=search_text,
            include_total_result_count=include_total_result_count,
            facets=facets,
            filter=filter_arg,
            highlight_fields=highlight_fields,
            highlight_post_tag=highlight_post_tag,
            highlight_pre_tag=highlight_pre_tag,
            minimum_coverage=minimum_coverage,
            order_by=order_by,
            query_type=query_type,
            scoring_parameters=scoring_parameters,
            scoring_profile=scoring_profile,
            search_fields=search_fields_str,
            search_mode=search_mode,
            query_language=query_language,
            speller=query_speller,
            answers=answers,
            captions=captions,
            semantic_fields=",".join(semantic_fields) if semantic_fields else None,
            semantic_configuration=semantic_configuration,
            select=select if isinstance(select, six.string_types) else None,
            skip=skip,
            top=top,
            session_id=session_id,
            scoring_statistics=scoring_statistics
        )
        if isinstance(select, list):
            query.select(select)
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        kwargs["api_version"] = self._api_version
        return AsyncSearchItemPaged(
            self._client, query, kwargs, page_iterator_class=AsyncSearchPageIterator
        )

    @distributed_trace_async
    async def suggest(self, search_text, suggester_name, **kwargs):
        # type: (str, str, **Any) -> List[dict]
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
        :rtype:  List[dict]

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_suggestions_async.py
                :start-after: [START suggest_query_async]
                :end-before: [END suggest_query_async]
                :language: python
                :dedent: 4
                :caption: Get search suggestions.
        """
        filter_arg = kwargs.pop("filter", None)
        use_fuzzy_matching = kwargs.pop("use_fuzzy_matching", None)
        highlight_post_tag = kwargs.pop("highlight_post_tag", None)
        highlight_pre_tag = kwargs.pop("highlight_pre_tag", None)
        minimum_coverage = kwargs.pop("minimum_coverage", None)
        order_by = kwargs.pop("order_by", None)
        search_fields = kwargs.pop("search_fields", None)
        search_fields_str = ",".join(search_fields) if search_fields else None
        select = kwargs.pop("select", None)
        top = kwargs.pop("top", None)
        query = SuggestQuery(
            search_text=search_text,
            suggester_name=suggester_name,
            filter=filter_arg,
            use_fuzzy_matching=use_fuzzy_matching,
            highlight_post_tag=highlight_post_tag,
            highlight_pre_tag=highlight_pre_tag,
            minimum_coverage=minimum_coverage,
            order_by=order_by,
            search_fields=search_fields_str,
            select=select if isinstance(select, six.string_types) else None,
            top=top,
        )
        if isinstance(select, list):
            query.select(select)
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        response = await self._client.documents.suggest_post(
            suggest_request=query.request, **kwargs
        )
        results = [r.as_dict() for r in response.results]
        return results

    @distributed_trace_async
    async def autocomplete(self, search_text, suggester_name, **kwargs):
        # type: (str, str, **Any) -> List[dict]
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
        :rtype:  List[dict]

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_autocomplete_async.py
                :start-after: [START autocomplete_query_async]
                :end-before: [END autocomplete_query_async]
                :language: python
                :dedent: 4
                :caption: Get a auto-completions.
        """
        autocomplete_mode = kwargs.pop("mode", None)
        filter_arg = kwargs.pop("filter", None)
        use_fuzzy_matching = kwargs.pop("use_fuzzy_matching", None)
        highlight_post_tag = kwargs.pop("highlight_post_tag", None)
        highlight_pre_tag = kwargs.pop("highlight_pre_tag", None)
        minimum_coverage = kwargs.pop("minimum_coverage", None)
        search_fields = kwargs.pop("search_fields", None)
        search_fields_str = ",".join(search_fields) if search_fields else None
        top = kwargs.pop("top", None)
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
        response = await self._client.documents.autocomplete_post(
            autocomplete_request=query.request, **kwargs
        )
        results = [r.as_dict() for r in response.results]
        return results

    async def upload_documents(self, documents, **kwargs):
        # type: (List[dict], **Any) -> List[IndexingResult]
        """Upload documents to the Azure search index.

        An upload action is similar to an "upsert" where the document will be
        inserted if it is new and updated/replaced if it exists. All fields are
        replaced in the update case.

        :param documents: A list of documents to upload.
        :type documents: List[dict]
        :rtype:  List[IndexingResult]

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

    async def delete_documents(self, documents, **kwargs):
        # type: (List[dict], **Any) -> List[IndexingResult]
        """Delete documents from the Azure search index

        Delete removes the specified document from the index. Any field you
        specify in a delete operation, other than the key field, will be
        ignored. If you want to remove an individual field from a document, use
        `merge_documents` instead and set the field explicitly to None.

        Delete operations are idempotent. That is, even if a document key does
        not exist in the index, attempting a delete operation with that key will
        result in a 200 status code.

        :param documents: A list of documents to delete.
        :type documents: List[dict]
        :rtype:  List[IndexingResult]

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

    async def merge_documents(self, documents, **kwargs):
        # type: (List[dict], **Any) -> List[IndexingResult]
        """Merge documents in to existing documents in the Azure search index.

        Merge updates an existing document with the specified fields. If the
        document doesn't exist, the merge will fail. Any field you specify in a
        merge will replace the existing field in the document. This also applies
        to collections of primitive and complex types.

        :param documents: A list of documents to merge.
        :type documents: List[dict]
        :rtype:  List[IndexingResult]

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

    async def merge_or_upload_documents(self, documents, **kwargs):
        # type: (List[dict], **Any) -> List[IndexingResult]
        """Merge documents in to existing documents in the Azure search index,
        or upload them if they do not yet exist.

        This action behaves like `merge_documents` if a document with the given
        key already exists in the index. If the document does not exist, it
        behaves like `upload_documents` with a new document.

        :param documents: A list of documents to merge or upload.
        :type documents: List[dict]
        :rtype:  List[IndexingResult]
        """
        batch = IndexDocumentsBatch()
        batch.add_merge_or_upload_actions(documents)

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        results = await self.index_documents(batch, **kwargs)
        return cast(List[IndexingResult], results)

    @distributed_trace_async
    async def index_documents(self, batch, **kwargs):
        # type: (IndexDocumentsBatch, **Any) -> List[IndexingResult]
        """Specify a document operations to perform as a batch.

        :param batch: A batch of document operations to perform.
        :type batch: IndexDocumentsBatch
        :rtype:  List[IndexingResult]
        :raises :class:`~azure.search.documents.RequestEntityTooLargeError`
        """
        return await self._index_documents_actions(actions=batch.actions, **kwargs)

    @distributed_trace_async
    async def _index_documents_actions(self, actions, **kwargs):
        # type: (List[IndexAction], **Any) -> List[IndexingResult]
        error_map = {413: RequestEntityTooLargeError}

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        try:
            batch_response = await self._client.documents.index(
                actions=actions, error_map=error_map, **kwargs
            )
            return cast(List[IndexingResult], batch_response.results)
        except RequestEntityTooLargeError:
            if len(actions) == 1:
                raise
            pos = round(len(actions) / 2)
            batch_response_first_half = await self._index_documents_actions(
                actions=actions[:pos], error_map=error_map, **kwargs
            )
            if batch_response_first_half:
                result_first_half = cast(
                    List[IndexingResult], batch_response_first_half.results
                )
            else:
                result_first_half = []
            batch_response_second_half = await self._index_documents_actions(
                actions=actions[pos:], error_map=error_map, **kwargs
            )
            if batch_response_second_half:
                result_second_half = cast(
                    List[IndexingResult], batch_response_second_half.results
                )
            else:
                result_second_half = []
            return result_first_half.extend(result_second_half)

    async def __aenter__(self):
        # type: () -> SearchClient
        await self._client.__aenter__()  # pylint: disable=no-member
        return self

    async def __aexit__(self, *args):
        # type: (*Any) -> None
        await self._client.__aexit__(*args)  # pylint: disable=no-member
