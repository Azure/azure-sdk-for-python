<<<<<<< HEAD
# The MIT License (MIT)
# Copyright (c) 2017 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
=======
#The MIT License (MIT)
#Copyright (c) 2017 Microsoft Corporation

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
>>>>>>> master

"""Internal class for connection reset retry policy implementation in the Azure Cosmos database service.
"""
from . import http_constants

<<<<<<< HEAD

=======
>>>>>>> master
class DefaultRetryPolicy(object):

    error_codes = http_constants._ErrorCodes
    CONNECTION_ERROR_CODES = [
<<<<<<< HEAD
        error_codes.WindowsInterruptedFunctionCall,
        error_codes.WindowsFileHandleNotValid,
        error_codes.WindowsPermissionDenied,
        error_codes.WindowsBadAddress,
        error_codes.WindowsInvalidArgumnet,
        error_codes.WindowsResourceTemporarilyUnavailable,
        error_codes.WindowsOperationNowInProgress,
        error_codes.WindowsAddressAlreadyInUse,
        error_codes.WindowsConnectionResetByPeer,
        error_codes.WindowsCannotSendAfterSocketShutdown,
        error_codes.WindowsConnectionTimedOut,
        error_codes.WindowsConnectionRefused,
        error_codes.WindowsNameTooLong,
        error_codes.WindowsHostIsDown,
        error_codes.WindowsNoRouteTohost,
        error_codes.LinuxConnectionReset,
    ]
=======
            error_codes.WindowsInterruptedFunctionCall,
            error_codes.WindowsFileHandleNotValid,
            error_codes.WindowsPermissionDenied,
            error_codes.WindowsBadAddress,
            error_codes.WindowsInvalidArgumnet,
            error_codes.WindowsResourceTemporarilyUnavailable,
            error_codes.WindowsOperationNowInProgress,
            error_codes.WindowsAddressAlreadyInUse,
            error_codes.WindowsConnectionResetByPeer,
            error_codes.WindowsCannotSendAfterSocketShutdown,
            error_codes.WindowsConnectionTimedOut,
            error_codes.WindowsConnectionRefused,
            error_codes.WindowsNameTooLong,
            error_codes.WindowsHostIsDown,
            error_codes.WindowsNoRouteTohost,
            error_codes.LinuxConnectionReset
        ]
>>>>>>> master

    def __init__(self, *args):
        self._max_retry_attempt_count = 10
        self.current_retry_attempt_count = 0
        self.retry_after_in_milliseconds = 1000
        self.args = args

    def needsRetry(self, error_code):
        if error_code in DefaultRetryPolicy.CONNECTION_ERROR_CODES:
<<<<<<< HEAD
            if len(self.args) > 0:
                if (self.args[4]["method"] == "GET") or (http_constants.HttpHeaders.IsQuery in self.args[4]["headers"]):
=======
            if (len(self.args) > 0):
                if (self.args[4]['method'] == 'GET') or (http_constants.HttpHeaders.IsQuery in self.args[4]['headers']):
>>>>>>> master
                    return True
                return False
            return True

    def ShouldRetry(self, exception):
        """Returns true if should retry based on the passed-in exception.

        :param (errors.HTTPFailure instance) exception:

        :rtype:
            boolean

        """
<<<<<<< HEAD
        if (self.current_retry_attempt_count < self._max_retry_attempt_count) and self.needsRetry(
            exception.status_code
        ):
=======
        if (self.current_retry_attempt_count < self._max_retry_attempt_count) and self.needsRetry(exception.status_code):
>>>>>>> master
            self.current_retry_attempt_count += 1
            return True
        return False
