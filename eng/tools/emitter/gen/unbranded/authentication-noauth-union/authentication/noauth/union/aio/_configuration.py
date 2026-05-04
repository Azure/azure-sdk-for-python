# coding=utf-8

from typing import Any, Optional, TYPE_CHECKING

from corehttp.runtime import policies

from .._version import VERSION

if TYPE_CHECKING:
    from corehttp.credentials import AsyncTokenCredential


class UnionClientConfiguration:
    """Configuration for UnionClient.

    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param endpoint: Service host. Default value is "http://localhost:3000".
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Default value is
     None.
    :type credential: ~corehttp.credentials.AsyncTokenCredential
    """

    def __init__(
        self,
        endpoint: str = "http://localhost:3000",
        credential: Optional["AsyncTokenCredential"] = None,
        **kwargs: Any
    ) -> None:

        self.endpoint = endpoint
        self.credential = credential
        self.credential_scopes = kwargs.pop("credential_scopes", ["https://security.microsoft.com/.default"])
        kwargs.setdefault("sdk_moniker", "authentication-noauth-union/{}".format(VERSION))
        self.polling_interval = kwargs.get("polling_interval", 30)
        self._configure(**kwargs)

    def _configure(self, **kwargs: Any) -> None:
        self.user_agent_policy = kwargs.get("user_agent_policy") or policies.UserAgentPolicy(**kwargs)
        self.headers_policy = kwargs.get("headers_policy") or policies.HeadersPolicy(**kwargs)
        self.proxy_policy = kwargs.get("proxy_policy") or policies.ProxyPolicy(**kwargs)
        self.logging_policy = kwargs.get("logging_policy") or policies.NetworkTraceLoggingPolicy(**kwargs)
        self.retry_policy = kwargs.get("retry_policy") or policies.AsyncRetryPolicy(**kwargs)
        self.authentication_policy = kwargs.get("authentication_policy")
        if self.credential and not self.authentication_policy:
            self.authentication_policy = policies.AsyncBearerTokenCredentialPolicy(
                self.credential,
                *self.credential_scopes,
                auth_flows=[
                    {
                        "authorizationUrl": "https://login.microsoftonline.com/common/oauth2/authorize",
                        "scopes": [{"value": "https://security.microsoft.com/.default"}],
                        "type": "implicit",
                    }
                ],
                **kwargs
            )
