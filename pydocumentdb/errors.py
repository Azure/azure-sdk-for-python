# Copyright (c) Microsoft Corporation.  All rights reserved.

"""PyDocumentDB Exceptions.
"""
import pydocumentdb.http_constants as http_constants

class DocumentDBError(Exception):
    """Base class for all DocumentDB errors.
    """


class HTTPFailure(DocumentDBError):
    """Raised when a HTTP request to the DocumentDB has failed.
    """
    def __init__(self, status_code, message='', headers=None):
        """
        :Parameters:
            status_code: int
            message: str

        """
        if headers is None:
            headers = {}

        self.status_code = status_code
        self.headers = headers
        self.sub_status = None
        if http_constants.HttpHeaders.SubStatus in self.headers:
            self.sub_status = int(self.headers[http_constants.HttpHeaders.SubStatus])
            DocumentDBError.__init__(self,
                                 'Status code: %d Sub-status: %d\n%s' % (self.status_code, self.sub_status, message))
        else:
            DocumentDBError.__init__(self,
                                 'Status code: %d\n%s' % (self.status_code, message))


class JSONParseFailure(DocumentDBError):
    """Raised when fails to parse JSON message.
    """


class UnexpectedDataType(DocumentDBError):
    """Raised when unexpected data type is provided as parameter.
    """