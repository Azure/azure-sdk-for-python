# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes

from ._utils import process_storage_error
from .models import StorageErrorException
from collections import deque

class QueueIterator(object):
    """An Iterable message stream.

    This iterator acts as an iterable message stream.
    """
    
    def __init__(self, timeout=None, **kwargs):
        self._queue = deque()
        self.timeout = timeout

    def __iter__(self):
        return self

    def __next__(self, timeout=None):
        while True:
            try:
                return self.next(timeout)
            except StopIteration:
                raise
            except StorageErrorException as error:
                process_storage_error(error)
    
    def next(self, timeout=None):
        '''
        Get the next element from the queue.  If no more elements
        are expected, then raise StopIteration; otherwise if no elements 
        are available element, wait timeout seconds, before raising Empty.  
        '''
        try:
            return self.get(timeout=timeout)
        except StopIteration:
            raise

    def get(self, timeout=None):
        """
        Remove and return an item from the queue.
        """
        if timeout is not None and timeout < 0:
            raise ValueError("'timeout' must be a non-negative number")
        return self._queue.popleft()
    
    def put(self, item):
        """
        Add an item to the queue
        """
        self._queue.append(item)
