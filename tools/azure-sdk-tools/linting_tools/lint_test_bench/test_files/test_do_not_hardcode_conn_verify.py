# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access
# This code violates do-not-harcode-connection-verify

from azure.core import PipelineClient
from azure.core.pipeline.transport import HttpRequest

def test_do_not_hardcode_conn_verify(**kwargs):
    client: PipelineClient = PipelineClient(base_url="endpoint", policies={}, **kwargs)
    client._pipeline._transport.connection_verify = False
    response = client._pipeline.run(
        HttpRequest("GET", "https://example.com"),
        **kwargs
    )
    return response
