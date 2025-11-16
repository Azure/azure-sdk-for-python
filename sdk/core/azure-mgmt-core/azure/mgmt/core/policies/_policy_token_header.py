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
from typing import TypeVar, Any, Union, TYPE_CHECKING, Dict
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.transport import (
    HttpResponse as LegacyHttpResponse,
    HttpRequest as LegacyHttpRequest,
)
from azure.core.rest import HttpResponse, HttpRequest, AsyncHttpResponse
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.exceptions import HttpResponseError

HTTPResponseType = TypeVar("HTTPResponseType", HttpResponse, LegacyHttpResponse)
HTTPRequestType = TypeVar("HTTPRequestType", HttpRequest, LegacyHttpRequest)

if TYPE_CHECKING:
    from .._pipeline_client import ARMPipelineClient


def _create_acquire_policy_request(request: PipelineRequest[HTTPRequestType]) -> HttpRequest:
    """Create a request to acquire a policy token.

    This method creates an HTTP request to the Azure Policy service to acquire
    a policy token for external policy evaluation. The token will be used in
    subsequent requests to enable policy evaluation.

    :param request: The pipeline request for which to acquire a policy token
    :type request: ~azure.core.pipeline.PipelineRequest
    :return: The HTTP request to acquire policy token
    :rtype: ~azure.core.rest.HttpRequest
    :raises ~azure.core.exceptions.HttpResponseError: If subscription ID cannot be extracted from request URL
    """
    # try to get subscriptionId from request.http_request.url
    subscription_id = (
        request.http_request.url.split("subscriptions/")[1].split("/")[0]
        if "subscriptions/" in request.http_request.url
        else None
    )
    if not subscription_id:
        raise HttpResponseError("Failed to get subscriptionId from request url: {}".format(request.http_request.url))

    content = getattr(request.http_request, "content", None)
    if content and isinstance(content, str):
        try:
            content = json.loads(content)
        except Exception:  # pylint: disable=broad-except
            pass

    body: Dict[str, Any] = {"operation": {"uri": request.http_request.url, "httpMethod": request.http_request.method}}
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


def _update_request_with_policy_token(
    request: PipelineRequest[HTTPRequestType],
    acquire_policy_request: HttpRequest,
    acquire_policy_response: Union[HttpResponse, AsyncHttpResponse],
) -> None:
    """Update the original request with the acquired policy token.

    This method processes the response from the policy token acquisition request
    and adds the policy token to the original request headers if successful.

    :param request: The original pipeline request to update
    :type request: ~azure.core.pipeline.PipelineRequest
    :param acquire_policy_request: The request used to acquire the policy token
    :type acquire_policy_request: ~azure.core.rest.HttpRequest
    :param acquire_policy_response: The response from the policy token acquisition
    :type acquire_policy_response: Union[~azure.core.rest.HttpResponse, ~azure.core.rest.AsyncHttpResponse]
    :raises ~azure.core.exceptions.HttpResponseError: If policy token acquisition fails or returns non-200 status
    """
    if acquire_policy_response.status_code != 200:
        raise HttpResponseError(
            "status code is {} instead of expected 200 when trying call {} to get policy token: {}".format(
                acquire_policy_response.status_code, acquire_policy_request.url, acquire_policy_response.text()
            )
        )

    result = acquire_policy_response.json()
    if result.get("result") == "Succeeded" and result.get("token"):
        request.http_request.headers["x-ms-policy-external-evaluations"] = result["token"]
    else:
        raise HttpResponseError("Failed to acquire policy token: {}".format(acquire_policy_response.text()))


class PolicyTokenHeaderPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):
    """HTTP pipeline policy for adding policy token headers to Azure Resource Manager requests.

    This policy handles the acquisition and application of Azure Policy tokens for external
    policy evaluation. It integrates with the Azure Policy service to obtain tokens that
    enable policy evaluation during resource operations.

    :param client: The ARM pipeline client used for making policy token requests
    :type client: ~azure.mgmt.core.ARMPipelineClient
    :param kwargs: Additional keyword arguments passed to the base policy
    :type kwargs: Any
    """

    def __init__(self, client: "ARMPipelineClient", **kwargs: Any) -> None:  # pylint: disable=unused-argument
        """Initialize the policy token header policy.

        :param client: The ARM pipeline client used for making policy token requests
        :type client: ~azure.mgmt.core.ARMPipelineClient
        :param kwargs: Additional keyword arguments passed to the base policy
        :type kwargs: Any
        """
        self._client = client

    def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        """Process the request to add policy token headers if needed.

        This method is called for each outgoing request. It checks if a policy token
        is needed and if so, acquires one and adds it to the request headers.

        :param request: The pipeline request to process
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        acquire_policy_token = request.context.options.pop("acquire_policy_token", False)
        if not acquire_policy_token or request.http_request.method.upper() == "GET":
            return
        try:
            acquire_policy_request = _create_acquire_policy_request(request)
            acquire_policy_request.url = self._client.format_url(acquire_policy_request.url)
            acquire_policy_response = self._client.send_request(acquire_policy_request, stream=False)
            _update_request_with_policy_token(request, acquire_policy_request, acquire_policy_response)
        except Exception as e:
            request.context.options["acquire_policy_token"] = True
            raise e
