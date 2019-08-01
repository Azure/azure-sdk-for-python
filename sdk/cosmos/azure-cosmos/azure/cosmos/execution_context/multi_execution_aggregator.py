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

"""Internal class for multi execution context aggregator implementation in the Azure Cosmos database service.
"""

import heapq
from azure.cosmos.execution_context.base_execution_context import _QueryExecutionContextBase
from azure.cosmos.execution_context import document_producer
from azure.cosmos.routing import routing_range

class _MultiExecutionContextAggregator(_QueryExecutionContextBase):
    """This class is capable of queries which requires rewriting based on 
    backend's returned query execution info.
    
    This class maintains the execution context for each partition key range
    and aggregates the corresponding results from each execution context.
    
    When handling an orderby query, _MultiExecutionContextAggregator instantiates one instance of 
    DocumentProducer per target partition key range and aggregates the result of each.
    
    TODO improvement: this class needs to be parallelized
    """

    class PriorityQueue:
        """Provides a Priority Queue abstraction data structure"""
        def __init__(self):
            self._heap = []
    
        def pop(self):
            return heapq.heappop(self._heap)
    
        def push(self, item):
            heapq.heappush(self._heap, item)   
                
        def peek(self):
            return self._heap[0]
    
        def size(self):
            return len(self._heap)

    def __init__(self, client, resource_link, query, options, partitioned_query_ex_info):

        '''
        Constructor
        '''
        super(_MultiExecutionContextAggregator, self).__init__(client, options)

        # use the routing provider in the client
        self._routing_provider = client._routing_map_provider
        self._client = client
        self._resource_link = resource_link
        self._query = query
        self._partitioned_query_ex_info = partitioned_query_ex_info
        self._sort_orders = partitioned_query_ex_info.get_order_by()
        
        if self._sort_orders:
            self._document_producer_comparator = document_producer._OrderByDocumentProducerComparator(self._sort_orders)
        else:
            self._document_producer_comparator = document_producer._PartitionKeyRangeDocumentProduerComparator()

        # will be a list of (parition_min, partition_max) tuples
        targetPartitionRanges = self._get_target_parition_key_range()

        targetPartitionQueryExecutionContextList = []
        for partitionTargetRange in targetPartitionRanges:
            # create and add the child execution context for the target range
            targetPartitionQueryExecutionContextList.append(self._createTargetPartitionQueryExecutionContext(partitionTargetRange))

        self._orderByPQ = _MultiExecutionContextAggregator.PriorityQueue()

        for targetQueryExContext in targetPartitionQueryExecutionContextList:
            
            try:
                """TODO: we can also use more_itertools.peekable to be more python friendly"""
                targetQueryExContext.peek()
                # if there are matching results in the target ex range add it to the priority queue

                self._orderByPQ.push(targetQueryExContext)

            except StopIteration:
                continue        
    
    def next(self):
        """returns the next result
        
        :return:
            The next result.
        :rtype: dict
        :raises StopIteration: If no more result is left.
            
        """
        if self._orderByPQ.size() > 0:
            
            targetRangeExContext = self._orderByPQ.pop()
            res = next(targetRangeExContext)
            
            try:
                """TODO: we can also use more_itertools.peekable to be more python friendly"""
                targetRangeExContext.peek()
                self._orderByPQ.push(targetRangeExContext)

            except StopIteration:
                pass
                
            return res
        raise StopIteration

    def fetch_next_block(self):
        
        raise NotImplementedError("You should use pipeline's fetch_next_block.")
        
    def _createTargetPartitionQueryExecutionContext(self, partition_key_target_range):
        
        rewritten_query = self._partitioned_query_ex_info.get_rewritten_query()
        if rewritten_query:
            rewritten_query
            if isinstance(self._query, dict):
                # this is a parameterized query, collect all the parameters
                query = dict(self._query)
                query["query"] = rewritten_query
            else:
                query = rewritten_query
        else:
            query = self._query            

        return document_producer._DocumentProducer(partition_key_target_range, self._client, self._resource_link, query, self._document_producer_comparator, self._options)
    
    def _get_target_parition_key_range(self):

        query_ranges = self._partitioned_query_ex_info.get_query_ranges()
        return self._routing_provider.get_overlapping_ranges(self._resource_link, [routing_range._Range.ParseFromDict(range_as_dict) for range_as_dict in query_ranges])
