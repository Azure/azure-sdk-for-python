# coding=utf-8

from typing import Any, TYPE_CHECKING

from corehttp.runtime import policies

from ._version import VERSION

if TYPE_CHECKING:
    from corehttp.credentials import TokenCredential


class SchemaRegistryClientConfiguration:
    """Configuration for SchemaRegistryClient.

    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param fully_qualified_namespace: The Schema Registry service endpoint, for example
     'my-namespace.servicebus.windows.net'. Required.
    :type fully_qualified_namespace: str
    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~corehttp.credentials.TokenCredential
    :keyword api_version: The API version to use for this operation. Default value is "2023-07-01".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, fully_qualified_namespace: str, credential: "TokenCredential", **kwargs: Any) -> None:
        api_version: str = kwargs.pop("api_version", "2023-07-01")

        if fully_qualified_namespace is None:
            raise ValueError("Parameter 'fully_qualified_namespace' must not be None.")
        if credential is None:
            raise ValueError("Parameter 'credential' must not be None.")

        self.fully_qualified_namespace = fully_qualified_namespace
        self.credential = credential
        self.api_version = api_version
        self.credential_scopes = kwargs.pop("credential_scopes", ["https://eventhubs.azure.net/.default"])
        kwargs.setdefault("sdk_moniker", "schemaregistry/{}".format(VERSION))
        self.polling_interval = kwargs.get("polling_interval", 30)
        self._configure(**kwargs)

    def _configure(self, **kwargs: Any) -> None:
        self.user_agent_policy = kwargs.get("user_agent_policy") or policies.UserAgentPolicy(**kwargs)
        self.headers_policy = kwargs.get("headers_policy") or policies.HeadersPolicy(**kwargs)
        self.proxy_policy = kwargs.get("proxy_policy") or policies.ProxyPolicy(**kwargs)
        self.logging_policy = kwargs.get("logging_policy") or policies.NetworkTraceLoggingPolicy(**kwargs)
        self.retry_policy = kwargs.get("retry_policy") or policies.RetryPolicy(**kwargs)
        self.authentication_policy = kwargs.get("authentication_policy")
        if self.credential and not self.authentication_policy:
            self.authentication_policy = policies.BearerTokenCredentialPolicy(
                self.credential,
                *self.credential_scopes,
                auth_flows=[
                    {
                        "authorizationUrl": "https://login.microsoftonline.com/common/oauth2/authorize",
                        "scopes": [{"value": "https://eventhubs.azure.net/.default"}],
                        "type": "implicit",
                    }
                ],
                **kwargs
            )
