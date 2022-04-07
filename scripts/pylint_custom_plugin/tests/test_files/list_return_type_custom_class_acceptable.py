import azure
from typing import Iterator

class SearchQuery():
    """Represent a rich search query again an Azure Search index."""

    def order_by(self, *fields):
        pass

class SearchItemPaged():
    def __init__(self, *args, **kwargs):
        super(SearchItemPaged, self).__init__(*args, **kwargs)
        self._first_page_iterator_instance = None

    def by_page():
       pass

class SearchClient(): #@
    def list_search(self, search_text, **kwargs): # pylint:disable=too-many-locals
        # type: (str, **Any) -> SearchItemPaged[dict]
        """Search the Azure search index for documents.

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
        )
        if isinstance(select, list):
            query.select(select)

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        kwargs["api_version"] = self._api_version
        return SearchItemPaged(
            self._client, query, kwargs, page_iterator_class=None
        )
    
    def list_this(self):
        return azure.core.paging.ItemPaged()
    
    def list_something(self):
        return [1,2,3,4,5]
