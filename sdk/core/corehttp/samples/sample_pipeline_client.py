# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_pipeline_client.py

DESCRIPTION:
    This sample demonstrates how to create and use a PipelineClient.

USAGE:
    python sample_pipeline_client.py
"""

from typing import Iterable, Union


def sample_pipeline_client():
    # [START build_pipeline_client]
    from corehttp.runtime import PipelineClient
    from corehttp.rest import HttpRequest, HttpResponse
    from corehttp.runtime.policies import (
        HTTPPolicy,
        SansIOHTTPPolicy,
        HeadersPolicy,
        UserAgentPolicy,
        RetryPolicy,
    )

    policies: Iterable[Union[HTTPPolicy, SansIOHTTPPolicy]] = [
        HeadersPolicy(),
        UserAgentPolicy("myuseragent"),
        RetryPolicy(),
    ]

    client: PipelineClient[HttpRequest, HttpResponse] = PipelineClient("https://bing.com", policies=policies)
    request = HttpRequest("GET", "https://bing.com")
    response = client.send_request(request)
    # [END build_pipeline_client]

    pipeline_response = client.pipeline.run(request)
    print(response)


if __name__ == "__main__":
    sample_pipeline_client()
