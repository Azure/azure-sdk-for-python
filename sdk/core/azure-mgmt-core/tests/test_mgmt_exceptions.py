# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
import functools
import json

from azure.core.pipeline.transport._base import _HttpResponseBase

from azure.core.exceptions import HttpResponseError
from azure.mgmt.core.exceptions import ARMErrorFormat, TypedErrorInfo


ARMError = functools.partial(HttpResponseError, error_format=ARMErrorFormat)


def _build_response(json_body):
    class MockResponse(_HttpResponseBase):
        def __init__(self):
            super(MockResponse, self).__init__(
                request=None,
                internal_response=None,
            )
            self.status_code = 400
            self.reason = "Bad Request"
            self.content_type = "application/json"
            self._body = json_body

        def body(self):
            return self._body

    return MockResponse()


def test_arm_exception():

    message = {
        "error": {
            "code": "BadArgument",
            "message": "The provided database 'foo' has an invalid username.",
            "target": "query",
            "details": [
                {
                    "code": "301",
                    "target": "$search",
                    "message": "$search query option not supported",
                }
            ],
            "innererror": {"customKey": "customValue"},
            "additionalInfo": [{"type": "SomeErrorType", "info": {"customKey": "customValue"}}],
        }
    }
    cloud_exp = ARMError(response=_build_response(json.dumps(message).encode("utf-8")))
    assert cloud_exp.error.target == "query"
    assert cloud_exp.error.details[0].target == "$search"
    assert cloud_exp.error.innererror["customKey"] == "customValue"
    assert cloud_exp.error.additional_info[0].type == "SomeErrorType"
    assert cloud_exp.error.additional_info[0].info["customKey"] == "customValue"
    assert "customValue" in str(cloud_exp)

    message = {
        "error": {
            "code": "BadArgument",
            "message": "The provided database 'foo' has an invalid username.",
            "target": "query",
            "details": [
                {
                    "code": "301",
                    "target": "$search",
                    "message": "$search query option not supported",
                    "additionalInfo": [
                        {
                            "type": "PolicyViolation",
                            "info": {
                                "policyDefinitionDisplayName": "Allowed locations",
                                "policyAssignmentParameters": {"listOfAllowedLocations": {"value": ["westus"]}},
                            },
                        }
                    ],
                }
            ],
            "additionalInfo": [{"type": "SomeErrorType", "info": {"customKey": "customValue"}}],
        }
    }
    cloud_exp = ARMError(response=_build_response(json.dumps(message).encode("utf-8")))
    assert cloud_exp.error.target == "query"
    assert cloud_exp.error.details[0].target == "$search"
    assert cloud_exp.error.additional_info[0].type == "SomeErrorType"
    assert cloud_exp.error.additional_info[0].info["customKey"] == "customValue"
    assert cloud_exp.error.details[0].additional_info[0].type == "PolicyViolation"
    assert cloud_exp.error.details[0].additional_info[0].info["policyDefinitionDisplayName"] == "Allowed locations"
    assert (
        cloud_exp.error.details[0]
        .additional_info[0]
        .info["policyAssignmentParameters"]["listOfAllowedLocations"]["value"][0]
        == "westus"
    )
    assert "customValue" in str(cloud_exp)

    error = ARMError(response=_build_response(b"{{"))
    assert "Bad Request" in error.message

    error = ARMError(
        response=_build_response(
            b'{"error":{"code":"Conflict","message":"The maximum number of Free ServerFarms allowed in a Subscription is 10.","target":null,"details":[{"message":"The maximum number of Free ServerFarms allowed in a Subscription is 10."},{"code":"Conflict"},{"errorentity":{"code":"Conflict","message":"The maximum number of Free ServerFarms allowed in a Subscription is 10.","extendedCode":"59301","messageTemplate":"The maximum number of {0} ServerFarms allowed in a Subscription is {1}.","parameters":["Free","10"],"innerErrors":null}}],"innererror":null}}'
        )
    )
    assert error.error.code == "Conflict"

    message = json.dumps(
        {
            "error": {
                "code": "BadArgument",
                "message": "The provided database 'foo' has an invalid username.",
                "target": "query",
                "details": [
                    {
                        "code": "301",
                        "target": "$search",
                        "message": "$search query option not supported",
                    }
                ],
            }
        }
    ).encode("utf-8")
    error = ARMError(response=_build_response(message))
    assert error.error.code == "BadArgument"

    # See https://github.com/Azure/msrestazure-for-python/issues/54
    response_text = b'"{\\"error\\": {\\"code\\": \\"ResourceGroupNotFound\\", \\"message\\": \\"Resource group \'res_grp\' could not be found.\\"}}"'
    error = ARMError(response=_build_response(response_text))
    # Do not raise is plenty enough, that's a major server issue....
