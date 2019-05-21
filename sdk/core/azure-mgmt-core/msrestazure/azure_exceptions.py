# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

import json

from requests import RequestException

from msrest.exceptions import ClientException
from msrest.serialization import Deserializer
from msrest.exceptions import DeserializationError

class CloudErrorRoot(object):
    """Just match the "error" key at the root of a OdataV4 JSON.
    """
    _validation = {}
    _attribute_map = {
        'error': {'key': 'error', 'type': 'CloudErrorData'},
    }
    def __init__(self, error):
        self.error = error

class CloudErrorData(object):
    """Cloud Error Data object, deserialized from error data returned
    during a failed REST API call.
    """

    _validation = {}
    _attribute_map = {
        'error': {'key': 'code', 'type': 'str'},
        'message': {'key': 'message', 'type': 'str'},
        'target': {'key': 'target', 'type': 'str'},
        'details': {'key': 'details', 'type': '[CloudErrorData]'},
        'innererror': {'key': 'innererror', 'type': 'object'},
        'additionalInfo': {'key': 'additionalInfo', 'type': '[TypedErrorInfo]'},
        'data': {'key': 'values', 'type': '{str}'}
        }

    def __init__(self, *args, **kwargs):
        self.error = kwargs.get('error')
        self.message = kwargs.get('message')
        self.request_id = None
        self.error_time = None
        self.target = kwargs.get('target')
        self.details = kwargs.get('details')
        self.innererror = kwargs.get('innererror')
        self.additionalInfo = kwargs.get('additionalInfo')
        self.data = kwargs.get('data')
        super(CloudErrorData, self).__init__(*args)

    def __str__(self):
        """Cloud error message."""
        error_str = "Azure Error: {}".format(self.error)
        error_str += "\nMessage: {}".format(self._message)
        if self.target:
            error_str += "\nTarget: {}".format(self.target)
        if self.request_id:
            error_str += "\nRequest ID: {}".format(self.request_id)
        if self.error_time:
            error_str += "\nError Time: {}".format(self.error_time)
        if self.data:
            error_str += "\nAdditional Data:"
            for key, value in self.data.items():
                error_str += "\n\t{} : {}".format(key, value)
        if self.details:
            error_str += "\nException Details:"
            for error_obj in self.details:
                error_str += "\n\tError Code: {}".format(error_obj.error)
                error_str += "\n\tMessage: {}".format(error_obj.message)
                if error_obj.target:
                    error_str += "\n\tTarget: {}".format(error_obj.target)
                if error_obj.innererror:
                    error_str += "\nInner error: {}".format(json.dumps(error_obj.innererror, indent=4))
                if error_obj.additionalInfo:
                    error_str += "\n\tAdditional Information:"
                    for error_info in error_obj.additionalInfo:
                        error_str += "\n\t\t{}".format(str(error_info).replace("\n", "\n\t\t"))
        if self.innererror:
            error_str += "\nInner error: {}".format(json.dumps(self.innererror, indent=4))
        if self.additionalInfo:
            error_str += "\nAdditional Information:"
            for error_info in self.additionalInfo:
                error_str += "\n\t{}".format(str(error_info).replace("\n", "\n\t"))
        error_bytes = error_str.encode()
        return error_bytes.decode('ascii')

    @classmethod
    def _get_subtype_map(cls):
        return {}

    @property
    def message(self):
        """Cloud error message."""
        return self._message

    @message.setter
    def message(self, value):
        """Attempt to deconstruct error message to retrieve further
        error data.
        """
        try:
            import ast
            value = ast.literal_eval(value)
        except (SyntaxError, TypeError, ValueError):
            pass
        try:
            value = value.get('value', value)
            msg_data = value.split('\n')
            self._message = msg_data[0]
        except AttributeError:
            self._message = value
            return
        try:
            self.request_id = msg_data[1].partition(':')[2]
            time_str = msg_data[2].partition(':')
            self.error_time = Deserializer.deserialize_iso(
                "".join(time_str[2:]))
        except (IndexError, DeserializationError):
            pass


class CloudError(ClientException):
    """ClientError, exception raised for failed Azure REST call.
    Will attempt to deserialize response into meaningful error
    data.

    :param requests.Response response: Response object.
    :param str error: Optional error message.
    """

    def __init__(self, response, error=None, *args, **kwargs):
        self.deserializer = Deserializer({
            'CloudErrorRoot': CloudErrorRoot,
            'CloudErrorData': CloudErrorData,
            'TypedErroInfo': TypedErrorInfo
        })
        self.error = None
        self.message = None
        self.response = response
        self.status_code = self.response.status_code
        self.request_id = None

        if error:
            self.message = error
            self.error = response
        else:
            self._build_error_data(response)

            if not self.error or not self.message:
                self._build_error_message(response)

        super(CloudError, self).__init__(
            self.message, self.error, *args, **kwargs)

    def __str__(self):
        """Cloud error message"""
        if self.error:
            return str(self.error)
        return str(self.message)

    def _build_error_data(self, response):
        try:
            self.error = self.deserializer('CloudErrorRoot', response).error
        except DeserializationError:
            self.error = None
        except AttributeError:
            # So far seen on Autorest test server only.
            self.error = None
        else:
            if self.error:
                if not self.error.error or not self.error.message:
                    self.error = None
                else:
                    self.message = self.error.message

    def _get_state(self, content):
        state = content.get("status")
        if not state:
            resource_content = content.get('properties', content)
            state = resource_content.get("provisioningState")
        return "Resource state {}".format(state) if state else "none"

    def _build_error_message(self, response):
        # Assume ClientResponse has "body", and otherwise it's a requests.Response
        content = response.text() if hasattr(response, "body") else response.text
        try:
            data = json.loads(content)
        except ValueError:
            message = "none"
        else:
            try:
                message = data.get("message", self._get_state(data))
            except AttributeError: # data is not a dict, but is a requests.Response parsable as JSON
                message = str(content)
        try:
            response.raise_for_status()
        except RequestException as err:
            if not self.error:
                self.error = err
            if not self.message:
                if message == "none":
                    message = str(err)
                msg = "Operation failed with status: {!r}. Details: {}"
                self.message = msg.format(response.reason, message)
        else:
            if not self.error:
                self.error = response
            if not self.message:
                msg = "Operation failed with status: {!r}. Details: {}"
                self.message = msg.format(
                    response.status_code, message)

class TypedErrorInfo(object):
    """Typed Error Info object, deserialized from error data returned
    during a failed REST API call. Contains additional error information
    """

    _validation = {}
    _attribute_map = {
        'type': {'key': 'type', 'type': 'str'},
        'info': {'key': 'info', 'type': 'object'}
        }

    def __init__(self, type, info):
        self.type = type
        self.info = info

    def __str__(self):
        """Cloud error message."""
        error_str = "Type: {}".format(self.type)
        error_str += "\nInfo: {}".format(json.dumps(self.info, indent=4))
        error_bytes = error_str.encode()
        return error_bytes.decode('ascii')