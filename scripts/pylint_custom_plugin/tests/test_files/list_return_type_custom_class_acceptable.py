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
        self._client = None
        query = None
        return SearchItemPaged(
            self._client, query, kwargs, page_iterator_class=None
        )
    
    def list_this(self):
        return azure.core.paging.ItemPaged()
    
    def list_something(self):
        return [1,2,3,4,5]
