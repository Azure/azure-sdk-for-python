# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes

from ._utils import process_storage_error
from .models import StorageErrorException

class QueueIterator(object):
    """An Iterable message stream.

    This iterator acts as an iterable message stream.
    """
    
    def __init__(self, **kwargs):
        self.queue = iter([])

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            try:
                yield self.queue.next()
            except StopIteration:
                raise
            except StorageErrorException as error:
                process_storage_error(error)
