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
from typing import TypeVar, Any, Optional, Union
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.transport import (
    HttpResponse as LegacyHttpResponse,
    HttpRequest as LegacyHttpRequest,
)
from azure.core.rest import HttpResponse, HttpRequest, AsyncHttpResponse
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.exceptions import HttpResponseError
from .._pipeline_client import ARMPipelineClient

HTTPResponseType = TypeVar("HTTPResponseType", HttpResponse, LegacyHttpResponse)
HTTPRequestType = TypeVar("HTTPRequestType", HttpRequest, LegacyHttpRequest)


class _PolicyTokenHeaderPolicyBase:
    def __init__(self, **kwargs: Any) -> None:
        self._acquire_policy_token: bool = kwargs.pop("acquire_policy_token", False)

    def _create_acquire_policy_request(self, request: PipelineRequest[HTTPRequestType]) -> Optional[HttpRequest]:
        acquire_policy_token = request.context.options.pop("acquire_policy_token", None)
        if acquire_policy_token is None:
            if not self._acquire_policy_token:
                return None
        elif acquire_policy_token is False:
            return None

        # try to get subscriptionId from request.http_request.url
        subscription_id = (
            request.http_request.url.split("subscriptions/")[1].split("/")[0]
            if "subscriptions/" in request.http_request.url
            else None
        )
        if not subscription_id:
            raise HttpResponseError(
                "Failed to get subscriptionId from request url: {}".format(request.http_request.url)
            )

        content = getattr(request.http_request, "content", None)
        if content and isinstance(content, str):
            try:
                content = json.loads(content)
            except Exception:  # pylint: disable=broad-except
                pass

        body = {"operation": {"uri": request.http_request.url, "method": request.http_request.method}}
        if content:
            body["operation"]["content"] = content
        change_reference = request.context.options.pop("change_reference", None)
        if change_reference:
            body["changeReference"] = change_reference

        acquire_policy_url = "/subscriptions/{subscriptionId}/providers/Microsoft.Authorization/acquirePolicyToken"
        return HttpRequest(
            method="POST",
            url=acquire_policy_url.format(subscriptionId=subscription_id),
            params={"api-version": "2025-03-01"},
            headers={"Accept": "application/json", "Content-Type": "application/json", "x-ms-force-sync": "true"},
            content=json.dumps(body),
        )

    @staticmethod
    def _update_request_with_policy_token(
        request: PipelineRequest[HTTPRequestType],
        acquire_policy_request: HttpRequest,
        acquire_policy_response: Union[HttpResponse, AsyncHttpResponse],
    ) -> None:
        if acquire_policy_response.status_code != 200:
            raise HttpResponseError(
                "status code is not 200 when trying call {} to get policy token".format(acquire_policy_request.url)
            )

        result = acquire_policy_response.json()
        if result.get("result") == "Succeeded" and result.get("token"):
            request.http_request.headers["x-ms-policy-external-evaluations"] = result["token"]
        else:
            raise HttpResponseError("Failed to acquire policy token: {}".format(acquire_policy_response.text()))


class PolicyTokenHeaderPolicy(_PolicyTokenHeaderPolicyBase, SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):

    def __init__(self, client: ARMPipelineClient, **kwargs: Any):
        super().__init__(**kwargs)
        self._client = client

    def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        acquire_policy_request = self._create_acquire_policy_request(request)
        if acquire_policy_request:
            acquire_policy_response = self._client.send_request(acquire_policy_request, stream=False)
            self._update_request_with_policy_token(request, acquire_policy_request, acquire_policy_response)
