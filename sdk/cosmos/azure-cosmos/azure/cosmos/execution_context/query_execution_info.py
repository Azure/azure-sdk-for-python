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

"""Internal class for partitioned query execution info implementation in the Azure Cosmos database service.
"""

import six

class _PartitionedQueryExecutionInfo(object):
    '''
    Represents a wrapper helper for partitioned query execution info dictionary
    returned by the backend.
    '''
    
    QueryInfoPath = 'queryInfo'
    TopPath = [QueryInfoPath, 'top']
    OrderByPath = [QueryInfoPath, 'orderBy']
    AggregatesPath = [QueryInfoPath, 'aggregates']
    QueryRangesPath = 'queryRanges'
    RewrittenQueryPath = [QueryInfoPath, 'rewrittenQuery']

    def __init__(self, query_execution_info):
        '''
        Constructor
        :param dict query_execution_info:
        '''
        self._query_execution_info = query_execution_info

    def get_top(self):
        """Returns the top count (if any) or None
        """
        return self._extract(_PartitionedQueryExecutionInfo.TopPath)
    
    def get_order_by(self):
        """Returns order by items (if any) or None
        """
        return self._extract(_PartitionedQueryExecutionInfo.OrderByPath)

    def get_aggregates(self):
        """Returns aggregators (if any) or None
        """
        return self._extract(_PartitionedQueryExecutionInfo.AggregatesPath)

    def get_query_ranges(self):
        """Returns query partition ranges (if any) or None
        """
        return self._extract(_PartitionedQueryExecutionInfo.QueryRangesPath)

    def get_rewritten_query(self):
        """Returns rewritten query or None (if any)
        """
        rewrittenQuery = self._extract(_PartitionedQueryExecutionInfo.RewrittenQueryPath)
        if rewrittenQuery is not None:
            # Hardcode formattable filter to true for now 
            rewrittenQuery = rewrittenQuery.replace('{documentdb-formattableorderbyquery-filter}', 'true')
        return rewrittenQuery

    def _extract(self, path):
        
        item = self._query_execution_info
        if isinstance(path, six.string_types):
            return item.get(path)
        
        for p in path:
            item = item.get(p)
            if item is None:
                return None
        return item    