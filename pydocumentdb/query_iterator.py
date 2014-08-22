# Copyright (c) Microsoft Corporation.  All rights reserved.

"""Iterator for query results.
"""

import pydocumentdb.errors as errors
import pydocumentdb.http_constants as http_constants


class QueryIterator:
    """Represents an iterator for query results.
    """

    class __States:
        """The states of the iterator.
        """
        Start = 0
        InProgress = 1
        Ended = 2

    def __init__(self, options, fetch_function):
        """
        :Parameters:
            - `options`: dict
            - `fetch_function`: function
           
        Example of `fetch_function`:

        >>> def result_fn(result):
        >>>     return result['Databases']

        """
        self.__options = options
        self.__fetch_function = fetch_function
        self.__current = 0
        self.__resources = []
        self.__continuation = None
        self.__state = self.__States.Start

    def __iter__(self):
        """Makes this class iterable.
        """
        return self

    def next(self):
        """Makes this class iterable.
        """
        item = self.__FetchOneItem()
        if not item:
            raise StopIteration
        else:
            self.__MoveToNext()
            return item

    def Reset(self):
        """Resets the iterator to its initial state.
        """
        self.__current = 0
        self.__resources = []
        self.__continuation = None
        self.__state = self.__States.Start

    def ToArray(self):
        """Tranverses through the iterator and gets all the iterable elements.

        :Returns:
            list

        """
        array = []
        # Python implicitly calls self.next with "for ... in ..."
        for element in self:
            array.append(element)
        return array

    def NextBatchToArray(self):
        """Fetches the next batch of iterable elements.

        :Returns:
            list

        """
        if (self.__state == self.__States.Start or
            (self.__continuation and self.__state == self.__States.InProgress)):
            if not self.__FetchMore():
                return None
            self.__current += len(self.__resources)
            return self.__resources
        else:
            self.__state = self.__States.Ended
            return None

    def __FetchOneItem(self):
        """Fetches one item.

        :Returns:
            dict or None

        """
        if self.__current < len(self.__resources):
            return self.__resources[self.__current]

        if (self.__state == self.__States.Start or
            (self.__continuation and self.__state == self.__States.InProgress)):
            if not self.__FetchMore():
                return None
            while len(self.__resources) == 0:
                if not self.__continuation:
                    self.__state = self.__States.Ended
                    return None
                else:
                    if not self.__FetchMore():
                        return None
            return self.__resources[self.__current]
        else:
            self.__state = self.__States.Ended
            return None

    def __MoveToNext(self):
        """Moves to the next iterable element.
        """
        self.__current += 1

    def __FetchMore(self):
        """Fetches more iterable elements.

        :Returns:
            boolean, True on success, False on failure.

        """
        self.__options['continuation'] = self.__continuation
        (self.__resources, response_headers) = self.__fetch_function(
            self.__options)
        self.__continuation = (response_headers[
                                   http_constants.HttpHeaders.Continuation]
                               if (http_constants.HttpHeaders.Continuation in
                                   response_headers)
                               else None)
        self.__state = self.__States.InProgress
        self.__current = 0
        return True

    def __enter__(self):
        """To support `with` operator.

        :Returns:
            query_iterator.QueryIterator

        """
        return self

    def __exit__(self, e_type, e_value, e_trace):
        """To support `with` operator.

        :Parameters:
            - `e_type`: the type of exception
            - `e_value`: the exception instance raised.
            - `e_trance`: a traceback instance.

        """
        pass