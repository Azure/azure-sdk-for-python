# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class ChainableException(Exception):
    """This exception stores a reference to a previous exception which has caused
    the current one"""

    def __init__(self, message=None, cause=None):
        # By using .__cause__, this will allow typical stack trace behavior in Python 3,
        # while still being able to operate in Python 2.
        self.__cause__ = cause
        super(ChainableException, self).__init__(message)

    def __str__(self):
        if self.__cause__:
            return "{} caused by {}".format(
                super(ChainableException, self).__repr__(), self.__cause__.__repr__()
            )
        else:
            return super(ChainableException, self).__repr__()
