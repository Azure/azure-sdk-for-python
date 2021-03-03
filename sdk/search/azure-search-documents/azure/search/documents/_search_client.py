# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import cast, List, TYPE_CHECKING
import six

from azure.core.tracing.decorator import distributed_trace
from ._api_versions import DEFAULT_VERSION
from ._generated import SearchClient as SearchIndexClient
from ._generated.models import IndexingResult
from ._search_documents_error import RequestEntityTooLargeError
from ._index_documents_batch import IndexDocumentsBatch
from ._paging import SearchItemPaged, SearchPageIterator
from ._queries import AutocompleteQuery, SearchQuery, SuggestQuery
from ._headers_mixin import HeadersMixin
from ._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Union
    from azure.core.credentials import AzureKeyCredential


def odata(statement, **kwargs):
    """Escape an OData query string.

    The statement to prepare should include fields to substitute given inside
    braces, e.g. `{somevar}` and then pass the corresponing value as a keyword
    argument, e.g. `somevar=10`.

    :param statement: An OData query string to prepare
    :type statement: str
    :rtype: str

    .. admonition:: Example:

        >>> odata("name eq {name} and age eq {age}", name="O'Neil", age=37)
        "name eq 'O''Neil' and age eq 37"


    """
    kw = dict(kwargs)
    for key in kw:
        value = kw[key]
        if isinstance(value, six.string_types):
            value = value.replace("'", "''")
            if "'{{{}}}'".format(key) not in statement:
                kw[key] = "'{}'".format(value)
    return statement.format(**kw)


class SearchClient(HeadersMixin):
    """A client to interact with an existing Azure search index.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param index_name: The name of the index to connect to
    :type index_name: str
    :param credential: A credential to authorize search client requests
    :type credential: ~azure.core.credentials.AzureKeyCredential
    :keyword str api_version: The Search API version to use for requests.

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_search_client_with_key]
            :end-before: [END create_search_client_with_key]
            :language: python
            :dedent: 4
            :caption: Creating the SearchClient with an API key.
    """

    _ODATA_ACCEPT = "application/json;odata.metadata=none"  # type: str

    def __init__(self, endpoint, index_name, credential, **kwargs):
        # type: (str, str, AzureKeyCredential, **Any) -> None

        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._endpoint = endpoint  # type: str
        self._index_name = index_name  # type: str
        self._credential = credential  # type: AzureKeyCredential
        self._client = SearchIndexClient(
            endpoint=endpoint,
            index_name=index_name,
            sdk_moniker=SDK_MONIKER,
            api_version=self._api_version, **kwargs
        )  # type: SearchIndexClient

    def __repr__(self):
        # type: () -> str
        return "<SearchClient [endpoint={}, index={}]>".format(
            repr(self._endpoint), repr(self._index_name)
        )[:1024]

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.documents.SearchClient` session.

        """
        return self._client.close()

    @distributed_trace
    def get_document_count(self, **kwargs):
        # type: (**Any) -> int
        """Return the number of documents in the Azure search index.

        :rtype: int
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        return int(self._client.documents.count(**kwargs))

    @distributed_trace
    def get_document(self, key, selected_fields=None, **kwargs):
        # type: (str, List[str], **Any) -> dict
        """Retrieve a document from the Azure search index by its key.

        :param key: The primary key value for the document to retrieve
        :type key: str
        :param selected_fields: a whitelist of fields to include in the results
        :type selected_fields: List[str]
        :rtype:  dict

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_get_document.py
                :start-after: [START get_document]
                :end-before: [END get_document]
                :language: python
                :dedent: 4
                :caption: Get a specific document from the search index.
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.documents.get(
            key=key, selected_fields=selected_fields, **kwargs
        )
        return cast(dict, result)

    @distributed_trace
    def search(self, search_text, **kwargs):
        # type: (str, **Any) -> SearchItemPaged[dict]
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
        :keyword list[str] highlight_fields: The list of field names to use for hit highlights. Only searchable
         fields can be used for hit highlighting.
        :keyword str highlight_post_tag: A string tag that is appended to hit highlights. Must be set with
         highlightPreTag. Default is &lt;/em&gt;.
        :keyword str highlight_pre_tag: A string tag that is prepended to hit highlights. Must be set with
         highlightPostTag. Default is &lt;em&gt;.
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
         'simple', 'full'.
        :paramtype query_type: str or ~search_index_client.models.QueryType
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
        :paramtype search_mode: str or ~search_index_client.models.SearchMode
        :keyword list[str] select: The list of fields to retrieve. If unspecified, all fields marked as retrievable
         in the schema are included.
        :keyword int skip: The number of search results to skip. This value cannot be greater than 100,000.
         If you need to scan documents in sequence, but cannot use $skip due to this limitation,
         consider using $orderby on a totally-ordered key and $filter with a range query instead.
        :keyword int top: The number of search results to retrieve. This can be used in conjunction with
         $skip to implement client-side paging of search results. If results are truncated due to
         server-side paging, the response will include a continuation token that can be used to issue
         another Search request for the next page of results.
        :rtype:  SearchItemPaged[dict]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_simple_query.py
                :start-after: [START simple_query]
                :end-before: [END simple_query]
                :language: python
                :dedent: 4
                :caption: Search on a simple text term.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_filter_query.py
                :start-after: [START filter_query]
                :end-before: [END filter_query]
                :language: python
                :dedent: 4
                :caption: Filter and sort search results.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_facet_query.py
                :start-after: [START facet_query]
                :end-before: [END facet_query]
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
        search_mode = kwargs.pop("search_mode", None)
        select = kwargs.pop("select", None)
        skip = kwargs.pop("skip", None)
        top = kwargs.pop("top", None)
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
            search_fields=search_fields,
            search_mode=search_mode,
            select=select if isinstance(select, six.string_types) else None,
            skip=skip,
            top=top
        )
        if isinstance(select, list):
            query.select(select)

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        kwargs["api_version"] = self._api_version
        return SearchItemPaged(
            self._client, query, kwargs, page_iterator_class=SearchPageIterator
        )

    @distributed_trace
    def suggest(self, search_text, suggester_name, **kwargs):
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

            .. literalinclude:: ../samples/sample_suggestions.py
                :start-after: [START suggest_query]
                :end-before: [END suggest_query]
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
            search_fields=search_fields,
            select=select if isinstance(select, six.string_types) else None,
            top=top
        )
        if isinstance(select, list):
            query.select(select)
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        response = self._client.documents.suggest_post(
            suggest_request=query.request, **kwargs
        )
        results = [r.as_dict() for r in response.results]
        return results

    @distributed_trace
    def autocomplete(self, search_text, suggester_name, **kwargs):
        # type: (str, str, **Any) -> List[dict]
        """Get search auto-completion results from the Azure search index.

        :param str search_text: The search text on which to base autocomplete results.
        :param str suggester_name: The name of the suggester as specified in the suggesters
        collection that's part of the index definition.
        :keyword mode: Specifies the mode for Autocomplete. The default is 'oneTerm'. Use
         'twoTerms' to get shingles and 'oneTermWithContext' to use the current context while producing
         auto-completed terms. Possible values include: 'oneTerm', 'twoTerms', 'oneTermWithContext'.
        :paramtype mode: str or ~search_index_client.models.AutocompleteMode
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

            .. literalinclude:: ../samples/sample_autocomplete.py
                :start-after: [START autocomplete_query]
                :end-before: [END autocomplete_query]
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
            search_fields=search_fields,
            top=top
        )

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        response = self._client.documents.autocomplete_post(
            autocomplete_request=query.request, **kwargs
        )
        results = [r.as_dict() for r in response.results]
        return results

    def upload_documents(self, documents, **kwargs):
        # type: (List[dict], **Any) -> List[IndexingResult]
        """Upload documents to the Azure search index.

        An upload action is similar to an "upsert" where the document will be
        inserted if it is new and updated/replaced if it exists. All fields are
        replaced in the update case.

        :param documents: A list of documents to upload.
        :type documents: List[dict]
        :rtype:  List[IndexingResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_crud_operations.py
                :start-after: [START upload_document]
                :end-before: [END upload_document]
                :language: python
                :dedent: 4
                :caption: Upload new documents to an index
        """
        batch = IndexDocumentsBatch()
        batch.add_upload_actions(documents)

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        results = self.index_documents(batch, **kwargs)
        return cast(List[IndexingResult], results)

    def delete_documents(self, documents, **kwargs):
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

            .. literalinclude:: ../samples/sample_crud_operations.py
                :start-after: [START delete_document]
                :end-before: [END delete_document]
                :language: python
                :dedent: 4
                :caption: Delete existing documents to an index
        """
        batch = IndexDocumentsBatch()
        batch.add_delete_actions(documents)

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        results = self.index_documents(batch, **kwargs)
        return cast(List[IndexingResult], results)

    def merge_documents(self, documents, **kwargs):
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

            .. literalinclude:: ../samples/sample_crud_operations.py
                :start-after: [START merge_document]
                :end-before: [END merge_document]
                :language: python
                :dedent: 4
                :caption: Merge fields into existing documents to an index
        """
        batch = IndexDocumentsBatch()
        batch.add_merge_actions(documents)

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        results = self.index_documents(batch, **kwargs)
        return cast(List[IndexingResult], results)

    def merge_or_upload_documents(self, documents, **kwargs):
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
        results = self.index_documents(batch, **kwargs)
        return cast(List[IndexingResult], results)

    @distributed_trace
    def index_documents(self, batch, **kwargs):
        # type: (IndexDocumentsBatch, **Any) -> List[IndexingResult]
        """Specify a document operations to perform as a batch.

        :param batch: A batch of document operations to perform.
        :type batch: IndexDocumentsBatch
        :rtype:  List[IndexingResult]
        :raises :class:`~azure.search.documents.RequestEntityTooLargeError`
        """
        return self._index_documents_actions(actions=batch.actions, **kwargs)

    def _index_documents_actions(self, actions, **kwargs):
        # type: (List[IndexAction], **Any) -> List[IndexingResult]
        error_map = {413: RequestEntityTooLargeError}

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        try:
            batch_response = self._client.documents.index(actions=actions, error_map=error_map, **kwargs)
            return cast(List[IndexingResult], batch_response.results)
        except RequestEntityTooLargeError:
            if len(actions) == 1:
                raise
            pos = round(len(actions) / 2)
            batch_response_first_half = self._index_documents_actions(
                actions=actions[:pos],
                error_map=error_map,
                **kwargs
            )
            if batch_response_first_half:
                result_first_half = cast(List[IndexingResult], batch_response_first_half.results)
            else:
                result_first_half = []
            batch_response_second_half = self._index_documents_actions(
                actions=actions[pos:],
                error_map=error_map,
                **kwargs
            )
            if batch_response_second_half:
                result_second_half = cast(List[IndexingResult], batch_response_second_half.results)
            else:
                result_second_half = []
            return result_first_half.extend(result_second_half)

    def __enter__(self):
        # type: () -> SearchClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
