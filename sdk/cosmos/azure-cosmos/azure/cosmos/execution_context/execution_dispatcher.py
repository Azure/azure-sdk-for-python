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

import json
from six.moves import xrange
from azure.cosmos.errors import HTTPFailure
from azure.cosmos.execution_context.base_execution_context import _QueryExecutionContextBase
from azure.cosmos.execution_context.base_execution_context import _DefaultQueryExecutionContext
from azure.cosmos.execution_context.query_execution_info import _PartitionedQueryExecutionInfo
from azure.cosmos.execution_context import endpoint_component
from azure.cosmos.execution_context import multi_execution_aggregator
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes

class _ProxyQueryExecutionContext(_QueryExecutionContextBase):
    '''
    This class represents a proxy execution context wrapper:
        - By default uses _DefaultQueryExecutionContext
        - if backend responds a 400 error code with a Query Execution Info
            it switches to _MultiExecutionContextAggregator
    '''
 
    def __init__(self, client, resource_link, query, options, fetch_function):
        '''
        Constructor
        '''
        super(_ProxyQueryExecutionContext, self).__init__(client, options)
        
        self._execution_context = _DefaultQueryExecutionContext(client, options, fetch_function)
        self._resource_link = resource_link
        self._query = query
        self._fetch_function = fetch_function
        
    def next(self):
        """Returns the next query result.
        
        :return:
            The next query result.
        :rtype: dict
        :raises StopIteration: If no more result is left.
            
        """
        try:
            return next(self._execution_context)
        except HTTPFailure as e:        
            if self._is_partitioned_execution_info(e):
                query_execution_info = self._get_partitioned_execution_info(e)
                self._execution_context = self._create_pipelined_execution_context(query_execution_info)
            else:
                raise e
        
        return next(self._execution_context)

    def fetch_next_block(self):
        """Returns a block of results. 
        
        This method only exists for backward compatibility reasons. (Because QueryIterable
        has exposed fetch_next_block api).
        
        :return:
            List of results.
        :rtype: list
        """
        try:
            return self._execution_context.fetch_next_block()
        except HTTPFailure as e:
            if self._is_partitioned_execution_info(e):
                query_execution_info = self._get_partitioned_execution_info(e)
                self._execution_context = self._create_pipelined_execution_context(query_execution_info)
            else:
                raise e
             
        return self._execution_context.fetch_next_block()        
        
    def _is_partitioned_execution_info(self, e):    
        return e.status_code == StatusCodes.BAD_REQUEST and e.sub_status == SubStatusCodes.CROSS_PARTITION_QUERY_NOT_SERVABLE
    
    def _get_partitioned_execution_info(self, e):
        error_msg = json.loads(e._http_error_message)
        return _PartitionedQueryExecutionInfo(json.loads(error_msg['additionalErrorInfo']))
        
    def _create_pipelined_execution_context(self, query_execution_info):
        
        assert self._resource_link, "code bug, resource_link has is required."
        execution_context_aggregator = multi_execution_aggregator._MultiExecutionContextAggregator(self._client, self._resource_link, self._query, self._options, query_execution_info)    
        return _PipelineExecutionContext(self._client, self._options, execution_context_aggregator, query_execution_info)


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
        
        top = query_execution_info.get_top()
        if not (top is None):
            self._endpoint = endpoint_component._QueryExecutionTopEndpointComponent(self._endpoint, top)

        aggregates = query_execution_info.get_aggregates()
        if aggregates:
            self._endpoint = endpoint_component._QueryExecutionAggregateEndpointComponent(self._endpoint, aggregates)
   
        
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
