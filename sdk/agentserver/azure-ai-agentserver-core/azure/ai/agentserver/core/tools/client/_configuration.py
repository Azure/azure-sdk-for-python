# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.core.configuration import Configuration
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline import policies

from ...application._package_metadata import get_current_app


class FoundryToolClientConfiguration(Configuration):  # pylint: disable=too-many-instance-attributes
    """Configuration for Azure AI Tool Client.

    Manages authentication, endpoint configuration, and policy settings for the
    Azure AI Tool Client. This class is used internally by the client and should
    not typically be instantiated directly.

    :param credential:
        Azure TokenCredential for authentication.
    :type credential: ~azure.core.credentials.TokenCredential
    """

    def __init__(self, credential: "AsyncTokenCredential"):
        super().__init__()

        self.retry_policy = policies.AsyncRetryPolicy()
        self.logging_policy = policies.NetworkTraceLoggingPolicy()
        self.request_id_policy = policies.RequestIdPolicy()
        self.http_logging_policy = policies.HttpLoggingPolicy()
        self.user_agent_policy = policies.UserAgentPolicy(
            base_user_agent=get_current_app().as_user_agent("FoundryToolClient"))
        self.authentication_policy = policies.AsyncBearerTokenCredentialPolicy(
            credential, "https://ai.azure.com/.default"
        )
        self.redirect_policy = policies.AsyncRedirectPolicy()
