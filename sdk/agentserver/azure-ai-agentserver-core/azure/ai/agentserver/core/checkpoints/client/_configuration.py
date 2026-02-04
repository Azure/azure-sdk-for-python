# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Configuration for Azure AI Checkpoint Client."""

from azure.core.configuration import Configuration
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline import policies

from ...application._metadata import get_current_app


class FoundryCheckpointClientConfiguration(Configuration):
    """Configuration for Azure AI Checkpoint Client.

    Manages authentication, endpoint configuration, and policy settings for the
    Azure AI Checkpoint Client. This class is used internally by the client and should
    not typically be instantiated directly.

    :param credential: Azure TokenCredential for authentication.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    """

    def __init__(self, credential: "AsyncTokenCredential") -> None:
        super().__init__()

        self.retry_policy = policies.AsyncRetryPolicy()
        self.logging_policy = policies.NetworkTraceLoggingPolicy()
        self.request_id_policy = policies.RequestIdPolicy()
        self.http_logging_policy = policies.HttpLoggingPolicy()
        self.user_agent_policy = policies.UserAgentPolicy(
            base_user_agent=get_current_app().as_user_agent("FoundryCheckpointClient")
        )
        self.authentication_policy = policies.AsyncBearerTokenCredentialPolicy(
            credential, "https://ai.azure.com/.default"
        )
        self.redirect_policy = policies.AsyncRedirectPolicy()
