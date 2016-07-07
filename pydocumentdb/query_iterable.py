# Copyright (c) Microsoft Corporation.  All rights reserved.

"""Iterable query results.
"""

import pydocumentdb.base as base
import pydocumentdb.http_constants as http_constants
import pydocumentdb.retry_utility as retry_utility


class QueryIterable(object):
    """Represents an iterable object of the query results.
    """
    
    def __init__(self, client, options, fetch_function):
        """
        :Parameters:
            - `client`: object, document client instance
            - `options`: dict, the request options for the request.
            - `fetch_function`: function, for executing the feed query

        Example of `fetch_function`:

        >>> def result_fn(result):
        >>>     return result['Databases']

        """
        self._client = client
        self._options = options
        self._fetch_function = fetch_function
        self.retry_options = client.connection_policy.RetryOptions;
        self._results = []
        self._continuation = None
        self._has_started = False
        
        self._current_collection_index = 0
        self._collection_links = []
        self._collection_links_length = 0


    @classmethod
    def PartitioningQueryIterable(cls, client, options, database_link, query, partition_key):
        """
        :Parameters:
            - `client`: DocumentClient, instance of document client
            - `options`: dict, the request options for the request.
            - `database_link`: str, database self link or ID based link
            - `query`: str or dict
            - `partition_key`: str, partition key for the query

        Example of `fetch_function`:

        >>> def result_fn(result):
        >>>     return result['Databases']

        """
        
        # This will call the base constructor(__init__ method above)
        self = cls(client, options, None)

        self._query = query

        partition_resolver = client.GetPartitionResolver(database_link)
        
        if(partition_resolver is None):
            raise ValueError(client.PartitionResolverErrorMessage)
        else:
            self._collection_links = partition_resolver.ResolveForRead(partition_key)

        self._collection_links_length = len(self._collection_links)

        if self._collection_links is None:
            raise ValueError("_collection_links is None.")

        if self._collection_links_length <= 0:
            raise ValueError("_collection_links_length is not greater than 0.")

        # Creating the QueryFeed for the first collection
        path = base.GetPathFromLink(self._collection_links[self._current_collection_index], 'docs')
        collection_id = base.GetResourceIdOrFullNameFromLink(self._collection_links[self._current_collection_index])
        
        self._current_collection_index += 1

        def fetch_fn(options):
            return client.QueryFeed(path,
                                    collection_id,
                                    query,
                                    options)

        self._fetch_function = fetch_fn
        
        return self

    def __iter__(self):
        """Makes this class iterable.
        """
        return self.Iterator(self)

    class Iterator(object):
        def __init__(self, iterable):
            self._iterable = iterable
            self._finished = False
            self._current = 0
            self._iterable._results = []
            self._iterable._continuation = None
            self._iterable._has_started = False

        def __iter__(self):
            # Always returns self
            return self

        def next(self):
            def callback():
                if not self._iterable.fetch_next_block():
                    self._finished = True

            if self._finished:
                # Must keep raising once we have ended
                raise StopIteration

            if (self._current >= len(self._iterable._results) and
                    not self._finished):
                retry_utility._Execute(self._iterable._client, self._iterable._client._global_endpoint_manager, callback)
                self._current = 0

            if self._finished:
                raise StopIteration

            result = self._iterable._results[self._current]
            self._current += 1
            return result

        # Also support Python 3.x iteration
        __next__ = next

    def fetch_next_block(self):
        """Fetches the next block of query results.

        :Returns:
            list of fetched items.

        """
        # Fetch next block of results by executing the query against the current document collection
        fetched_items = self.fetch_items()

        # If there are multiple document collections to query for(in case of partitioning), keep looping through each one of them,
        # creating separate feed queries for each collection and fetching the items
        while not fetched_items:
            if self._collection_links and self._current_collection_index < self._collection_links_length:
                path = base.GetPathFromLink(self._collection_links[self._current_collection_index], 'docs')
                collection_id = base.GetResourceIdOrFullNameFromLink(self._collection_links[self._current_collection_index])
                
                self._continuation = None
                self._has_started = False

                def fetch_fn(options):
                    return self._client.QueryFeed(path,
                                            collection_id,
                                            self._query,
                                            options)

                self._fetch_function = fetch_fn

                fetched_items = self.fetch_items()
                self._current_collection_index += 1
            else:
                break

        return fetched_items
        

    def fetch_items(self):
        """Fetches more items.

        :Returns:
            list of fetched items.

        """
        fetched_items = []
        while self._continuation or not self._has_started:
            if not self._has_started:
                self._has_started = True
            self._options['continuation'] = self._continuation
            (fetched_items, response_headers) = self._fetch_function(self._options)
            self._results = fetched_items
            self._continuation = response_headers.get(
                http_constants.HttpHeaders.Continuation)
            if fetched_items:
                break
        return fetched_items
