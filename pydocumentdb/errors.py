# Copyright (c) Microsoft Corporation.  All rights reserved.

"""PyDocumentDB Exceptions.
"""


class DocumentDBError(Exception):
    """Base class for all DocumentDB errors.
    """


class HTTPFailure(DocumentDBError):
    """Raised when a HTTP request to the DocumentDB has failed.
    """
    def __init__(self, status_code, message='', headers={}):
        """
        :Parameters:
            status_code: int
            message: str

        """
        self.status_code = status_code
        self.headers = headers
        DocumentDBError.__init__(self,
                                 'Status code: %d\n%s' % (status_code, message))


class JSONParseFailure(DocumentDBError):
    """Raised when fails to parse JSON message.
    """


class UnexpectedDataType(DocumentDBError):
    """Raised when unexpected data type is provided as parameter.
    """