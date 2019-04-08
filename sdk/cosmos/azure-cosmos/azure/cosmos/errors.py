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

"""PyCosmos Exceptions in the Azure Cosmos database service.
"""
import azure.cosmos.http_constants as http_constants

class CosmosError(Exception):
    """Base class for all Azure Cosmos errors.
    """


class HTTPFailure(CosmosError):
    """Raised when a HTTP request to the Azure Cosmos has failed.
    """
    def __init__(self, status_code, message='', headers=None):
        """
        :param int status_code:
        :param str message:

        """
        if headers is None:
            headers = {}

        self.status_code = status_code
        self.headers = headers
        self.sub_status = None
        self._http_error_message = message
        if http_constants.HttpHeaders.SubStatus in self.headers:
            self.sub_status = int(self.headers[http_constants.HttpHeaders.SubStatus])
            CosmosError.__init__(self,
                                 'Status code: %d Sub-status: %d\n%s' % (self.status_code, self.sub_status, message))
        else:
            CosmosError.__init__(self,
                                 'Status code: %d\n%s' % (self.status_code, message))

class JSONParseFailure(CosmosError):
    """Raised when fails to parse JSON message.
    """


class UnexpectedDataType(CosmosError):
    """Raised when unexpected data type is provided as parameter.
    """