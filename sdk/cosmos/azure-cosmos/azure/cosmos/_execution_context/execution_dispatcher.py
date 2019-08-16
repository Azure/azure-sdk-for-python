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

"""Internal class for proxy query execution context implementation in the Azure Cosmos database service.
"""

from six.moves import xrange
from azure.cosmos._execution_context.base_execution_context import _QueryExecutionContextBase
from azure.cosmos._execution_context import endpoint_component


class _PipelineExecutionContext(_QueryExecutionContextBase):
        
    DEFAULT_PAGE_SIZE = 1000    
        
    def __init__(self, client, options, execution_context, query_execution_info):
        '''
        Constructor
        '''
        super(_PipelineExecutionContext, self).__init__(client, options)
        
        if options.get('maxItemCount'):
            self._page_size = options['maxItemCount']
        else:
            self._page_size = _PipelineExecutionContext.DEFAULT_PAGE_SIZE
        
        self._execution_context = execution_context
        
        self._endpoint = endpoint_component._QueryExecutionEndpointComponent(execution_context)
        
        order_by = query_execution_info.get_order_by()
        if (order_by):
            self._endpoint = endpoint_component._QueryExecutionOrderByEndpointComponent(self._endpoint)

        aggregates = query_execution_info.get_aggregates()
        if aggregates:
            self._endpoint = endpoint_component._QueryExecutionAggregateEndpointComponent(self._endpoint, aggregates)

        offset = query_execution_info.get_offset()
        if not (offset is None):
            self._endpoint = endpoint_component._QueryExecutionOffsetEndpointComponent(self._endpoint, offset)

        top = query_execution_info.get_top()
        if not (top is None):
            self._endpoint = endpoint_component._QueryExecutionTopEndpointComponent(self._endpoint, top)

        limit = query_execution_info.get_limit()
        if not (limit is None):
            self._endpoint = endpoint_component._QueryExecutionTopEndpointComponent(self._endpoint, limit)

        distinct_type = query_execution_info.get_distinct_type()
        if distinct_type != 'None':
            if distinct_type == "Ordered":
                self._endpoint = endpoint_component._QueryExecutionDistinctOrderedEndpointComponent(self._endpoint)
            else:
                self._endpoint = endpoint_component._QueryExecutionDistinctUnorderedEndpointComponent(self._endpoint)

    def next(self):
        """Returns the next query result.
        
        :return:
            The next query result.
        :rtype: dict
        :raises StopIteration: If no more result is left.
            
        """
        return next(self._endpoint)

    def fetch_next_block(self):
        """Returns a block of results. 
        
        This method only exists for backward compatibility reasons. (Because QueryIterable
        has exposed fetch_next_block api).
        
        This method internally invokes next() as many times required to collect the 
        requested fetch size.
        
        :return:
            List of results.
        :rtype: list
        """
        
        results = []
        for _ in xrange(self._page_size):
            try:
                results.append(next(self))
            except StopIteration:
                # no more results
                break
        return results            
