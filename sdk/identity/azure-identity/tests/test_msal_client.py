# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.pipeline.policies import RetryPolicy
from azure.identity._internal.msal_client import MsalClient

from helpers import mock, mock_response


def test_retries_posts():
    """The client should configure its pipeline to retry its token requests"""

    pipeline = mock.Mock(
        run=mock.Mock(
            return_value=mock.Mock(
                http_response=mock_response(json_payload={"access_token": "*", "expires_in": 42, "resource": "..."})
            )
        )
    )

    def get_pipeline(*_, **kwargs):
        for policy in kwargs.get("policies") or []:
            if isinstance(policy, RetryPolicy):
                return pipeline
        raise Exception("client should use RetryPolicy")

    with mock.patch(MsalClient.__module__ + ".Pipeline", get_pipeline):
        client = MsalClient()

    client.post("https://localhost")

    _, kwargs = pipeline.run.call_args
    assert "POST" in kwargs["retry_on_methods"]
