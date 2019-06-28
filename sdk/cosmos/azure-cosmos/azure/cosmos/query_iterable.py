#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""Iterable query results in the Azure Cosmos database service.
"""
from azure.cosmos.execution_context import execution_dispatcher
from azure.cosmos.execution_context import base_execution_context

class QueryIterable(object):
    """Represents an iterable object of the query results.
    QueryIterable is a wrapper for query execution context.
    """
    
    def __init__(self, client, query, options, fetch_function, collection_link = None):
        """
        Instantiates a QueryIterable for non-client side partitioning queries.
        _ProxyQueryExecutionContext will be used as the internal query execution context
         
        :param CosmosClient client:
            Instance of document client.
        :param (str or dict) query:
        :param dict options:
            The request options for the request.
        :param method fetch_function:
        :param str collection_link:
            If this is a Document query/feed collection_link is required.
 
        Example of `fetch_function`:
 
        >>> def result_fn(result):
        >>>     return result['Databases']
 
        """
        self._client = client
        self.retry_options = client.connection_policy.RetryOptions
        self._query = query
        self._options = options
        self._fetch_function = fetch_function
        self._collection_link = collection_link
        self._ex_context = None

    @classmethod
    def PartitioningQueryIterable(cls, client, query, options, database_link, partition_key):
        """
        Represents a client side partitioning query iterable.
        
        This constructor instantiates a QueryIterable for
        client side partitioning queries, and sets _MultiCollectionQueryExecutionContext
        as the internal execution context.
        
        :param CosmosClient client:
            Instance of document client
        :param (str or dict) options:
        :param dict options:
            The request options for the request.
        :param str database_link:
            Database self link or ID based link
        :param str partition_key:
            Partition key for the query
        """
        # This will call the base constructor(__init__ method above)
        
        self = cls(client, query, options, None, None)
        self._database_link = database_link
        self._partition_key = partition_key

        return self
    
    def _create_execution_context(self):
        """instantiates the internal query execution context based.
        """
        if hasattr(self, '_database_link'):
            # client side partitioning query
            return base_execution_context._MultiCollectionQueryExecutionContext(self._client, self._options, self._database_link, self._query, self._partition_key)
        else:
            # 
            return execution_dispatcher._ProxyQueryExecutionContext(self._client, self._collection_link, self._query, self._options, self._fetch_function)

    def __iter__(self):
        """Makes this class iterable.
        """
        return self.Iterator(self)

    class Iterator(object):
        def __init__(self, iterable):
            self._iterable = iterable
            self._finished = False
            self._ex_context = iterable._create_execution_context()

        def __iter__(self):
            # Always returns self
            return self

        def __next__(self):
            return next(self._ex_context)

        # Also support Python 3.x iteration
        def next(self):
            return self.__next__()

    def fetch_next_block(self):
        """Returns a block of results with respecting retry policy.
        
        This method only exists for backward compatibility reasons. (Because QueryIterable
        has exposed fetch_next_block api).

        :return:
            List of results.
        :rtype:
            list
        """
                
        if self._ex_context is None:
            # initiates execution context for the first time
            self._ex_context = self._create_execution_context()
        
        return self._ex_context.fetch_next_block()
