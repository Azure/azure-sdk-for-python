import collections.abc


class QueryResultIterator(collections.abc.Iterator):
    """ Iterator over query results from Azure Cosmos SQL DB

    The type of each item returned by the iterator depends on the specific
    query used to generate the result set. It may be a scalar value for aggregate
    functions, or it may be a dictionary for projections.
    """

    def __init__(self, inner, metadata=None):
        self.response_metadata = metadata
        self._inner = inner

    def __next__(self):
        return self._inner.__next__()

    def __iter__(self):
        return self
