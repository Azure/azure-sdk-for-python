# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

# import os
import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live_and_not_recording  # , get_proxy_netloc

# from ci_tools.variables import PROXY_URL
import urllib.parse as url_parse

# import httpx
# from urllib.parse import urlparse, urlunparse

# # option one: use custom transport to route through the proxy
# # need to figure out how to plug this into the client used in the tests
# class ProxyTransport(httpx.HTTPTransport):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.proxy_url = os.getenv("PROXY_URL")

#     def handle_request(self, request: httpx.Request) -> httpx.Response:
#         # Save original upstream base for the proxy to use during playback
#         parsed_target_url = urlparse(str(request.url))
#         if "x-recording-upstream-base-uri" not in request.headers:
#             request.headers["x-recording-upstream-base-uri"] = f"{parsed_target_url.scheme}://{parsed_target_url.netloc}"

#         # Set recording headers
#         request.headers["x-recording-id"] = "<RECORDING_ID>"
#         request.headers["x-recording-mode"] = "record"  # or "playback"
#         # rewrite destination to proxy
#         updated_target = parsed_target_url._replace(**get_proxy_netloc()).geturl()
#         request.url = httpx.URL(updated_target)

#         # Delegate to parent (real) transport and capture response
#         response = super().handle_request(request)

#         # Restore response.request.url to the original upstream target so callers see the original URL
#         try:
#             parsed_resp = urlparse(str(response.request.url))
#             upstream_uri = urlparse(response.request.headers.get("x-recording-upstream-base-uri", ""))
#             if upstream_uri.netloc:
#                 original_target = parsed_resp._replace(scheme=upstream_uri.scheme or parsed_resp.scheme, netloc=upstream_uri.netloc).geturl()
#                 response.request.url = httpx.URL(original_target)
#         except Exception:
#             # best-effort restore; do not fail the call if something goes wrong here
#             pass

#         return response


# class AsyncProxyTransport(httpx.AsyncHTTPTransport):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.proxy_url = os.getenv("PROXY_URL")

#     async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
#         # Save original upstream base for the proxy to use during playback
#         parsed_target_url = urlparse(str(request.url))
#         if "x-recording-upstream-base-uri" not in request.headers:
#             request.headers["x-recording-upstream-base-uri"] = f"{parsed_target_url.scheme}://{parsed_target_url.netloc}"

#         # Set recording headers
#         request.headers["x-recording-id"] = "<RECORDING_ID>"
#         request.headers["x-recording-mode"] = "record"  # or "playback"

#         # rewrite to proxy
#         updated_target = parsed_target_url._replace(**get_proxy_netloc()).geturl()
#         request.url = httpx.URL(updated_target)

#         # Delegate to underlying async transport and capture response
#         response = await super().handle_async_request(request)

#         # Restore response.request.url to the original upstream target so callers see the original URL
#         try:
#             parsed_resp = urlparse(str(response.request.url))
#             upstream_uri = urlparse(response.request.headers.get("x-recording-upstream-base-uri", ""))
#             if upstream_uri.netloc:
#                 original_target = parsed_resp._replace(scheme=upstream_uri.scheme or parsed_resp.scheme, netloc=upstream_uri.netloc).geturl()
#                 response.request.url = httpx.URL(original_target)
#         except Exception:
#             pass

#         return response


class TestResponses(TestBase):

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_responses(self, **kwargs):
        """
        Test creating a responses call (no Agents, no Conversation).

        Routes used in this test:

        Action REST API Route                                OpenAI Client Method
        ------+---------------------------------------------+-----------------------------------
        POST   /openai/responses                             client.responses.create()
        """
        model = self.test_agents_params["model_deployment_name"]

        client = self.create_client(operation_group="agents", **kwargs).get_openai_client()

        response1 = client.responses.create(
            model=model,
            input="How many feet in a mile?",
        )
        print(f"Response id: {response1.id}, output text: {response1.output_text}")
        assert "5280" in response1.output_text or "5,280" in response1.output_text

        response2 = client.responses.create(
            model=model, input="And how many meters?", previous_response_id=response1.id
        )
        print(f"Response id: {response2.id}, output text: {response2.output_text}")
        assert "1609" in response2.output_text or "1,609" in response2.output_text
