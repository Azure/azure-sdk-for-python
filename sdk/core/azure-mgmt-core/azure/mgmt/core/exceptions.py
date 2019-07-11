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
import logging
from typing import TYPE_CHECKING, Dict, Any, Optional


from azure.core.exceptions import HttpResponseError


if TYPE_CHECKING:
    from azure.core.pipeline.transport.base import _HttpResponseBase


_LOGGER = logging.getLogger(__name__)


class ODataV4Format(object):
    """Class to describe OData V4 error format.

    http://docs.oasis-open.org/odata/odata-json-format/v4.0/os/odata-json-format-v4.0-os.html#_Toc372793091

    :param dict json_object: A Python dict representing a ODataV4 JSON
    :ivar str code: Its value is a service-defined error code. This code serves as a sub-status for the HTTP error code specified in the response.
    :ivar str message: Human-readable, language-dependent representation of the error.
    :ivar str target: The target of the particular error (for example, the name of the property in error).
    :ivar list details: Array of JSON objects that MUST contain name/value pairs for code and message, and MAY contain a name/value pair for target, as described above.
    :ivar dict innererror: An object. The contents of this object are service-defined. Usually this object contains information that will help debug the service.
    """

    def __init__(self, json_object):
        # Required fields, but assume they could be missing still to be robust
        self.code = json_object.get("code")  # type: Optional[str]
        self.message = json_object.get("message")  # type: Optional[str]

        # Optional fields
        self.target = json_object.get("target", None)  # type: Optional[str]

        # details is recursive of this very format
        self.details = [
            self.__class__(detail_node)
            for detail_node in json_object.get("details", [])
        ]  # type: List[ODataV4Format]

        self.innererror = json_object.get("innererror", {})  # type: Dict[str, Any]

    def __str__(self):
        error_str = "Code: {}".format(self.code)
        error_str += "\nMessage: {}".format(self.message)
        if self.target:
            error_str += "\nTarget: {}".format(self.target)

        if self.details:
            error_str += "\nException Details:"
            for error_obj in self.details:
                # Indent for visibility
                error_str += "\n".join("\t" + s for s in str(error_obj).splitlines())

        if self.innererror:
            error_str += "\nInner error: {}".format(
                json.dumps(self.innererror, indent=4)
            )
        return error_str


class ODataV4Error(HttpResponseError):
    """An HTTP response error where the JSON is decoded as OData V4 error format.

    http://docs.oasis-open.org/odata/odata-json-format/v4.0/os/odata-json-format-v4.0-os.html#_Toc372793091

    :ivar dict odata_json: The parsed JSON body as attribute for convenience.
    :ivar str code: Its value is a service-defined error code. This code serves as a sub-status for the HTTP error code specified in the response.
    :ivar str message: Human-readable, language-dependent representation of the error.
    :ivar str target: The target of the particular error (for example, the name of the property in error).
    :ivar list details: Array of JSON objects that MUST contain name/value pairs for code and message, and MAY contain a name/value pair for target, as described above.
    :ivar dict innererror: An object. The contents of this object are service-defined. Usually this object contains information that will help debug the service.
    """
    _ERROR_FORMAT = ODataV4Format

    def __init__(self, response, **kwargs):
        # type: (_HttpResponseBase, Dict[str, Any]) -> None

        # Ensure field are declared, whatever can happen afterwards
        self.odata_json = None  # type: Optional[dict[str, Any]]
        try:
            self.odata_json = json.loads(response.body())
            odata_message = self.odata_json.setdefault("error", {}).get("message")
        except Exception:
            # If the body is not JSON valid, just stop now
            odata_message = None

        self.code = None  # type: Optional[str]
        self.message = kwargs.get("message", odata_message)  # type: Optional[str]
        self.target = None  # type: Optional[str]
        self.details = []  # type: Optional[List[Any]]
        self.innererror = {}  # type: Optional[Dict[str, Any]]

        if self.message and "message" not in kwargs:
            kwargs['message'] = self.message

        super(ODataV4Error, self).__init__(
            response=response, **kwargs
        )

        if self.odata_json:
            try:
                error_node = self.odata_json["error"]
                self._error_format = self._ERROR_FORMAT(error_node)
                self.__dict__.update(self._error_format.__dict__)
            except Exception:
                _LOGGER.info("Received error message was not valid OdataV4 format.")
                self._error_format = "JSON was invalid for this format"

    def __str__(self):
        return str(self._error_format)


class TypedErrorInfo:
    """Additional info class defined in ARM specification.

    https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/common-api-details.md#error-response-content
    """

    def __init__(self, type, info):
        self.type = type
        self.info = info

    def __str__(self):
        """Cloud error message."""
        error_str = "Type: {}".format(self.type)
        error_str += "\nInfo: {}".format(json.dumps(self.info, indent=4))
        return error_str


class ARMErrorFormat(ODataV4Format):
    """Describe error format from ARM, used at the base or inside "details" node.

    This format is compatible with ODataV4 format.
    https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/common-api-details.md#error-response-content
    """

    def __init__(self, json_object):
        # Parse the ODatav4 part
        super(ARMErrorFormat, self).__init__(json_object)

        # ARM specific annotations
        self.additional_info = [
            TypedErrorInfo(additional_info["type"], additional_info["info"])
            for additional_info in json_object.get("additionalInfo", [])
        ]

    def __str__(self):
        error_str = super(ARMErrorFormat, self).__str__()

        if self.additional_info:
            error_str += "\nAdditional Information:"
            for error_info in self.additional_info:
                error_str += str(error_info)

        return error_str


class ARMError(ODataV4Error):
    """An HTTP error from an ARM endpoint.

    This subclass ODataV4Error since ARM specifications requires all
    ARM error to be complient with it.

    https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/common-api-details.md#error-response-content
    """
    _ERROR_FORMAT = ARMErrorFormat
