# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Any, Dict, MutableMapping, Optional, TypedDict, cast

from typing_extensions import Self, Unpack

from azure.core.configuration import Configuration
from azure.core.pipeline import AsyncPipeline, Pipeline
from azure.core.pipeline.policies import (
    AsyncRedirectPolicy,
    AsyncRetryPolicy,
    CustomHookPolicy,
    HeadersPolicy,
    HttpLoggingPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    RedirectPolicy,
    RetryPolicy,
    UserAgentPolicy,
)
from azure.core.pipeline.transport import (  # pylint: disable=non-abstract-transport-import,no-name-in-module
    AsyncHttpTransport,
    AsyncioRequestsTransport,
    HttpTransport,
    RequestsTransport,
)
from azure.core.pipeline.policies import (
    AsyncRetryPolicy,
    RetryPolicy,
    BearerTokenCredentialPolicy,
    AsyncBearerTokenCredentialPolicy
)
from azure.core.rest import AsyncHttpResponse, HttpRequest, HttpResponse
from azure.core.rest._rest_py3 import ContentType, FilesType, ParamsType

class HttpPipeline(Pipeline):
    """A *very* thin wrapper over azure.core.pipeline.Pipeline that facilitates sending miscellaneous http requests by
    adding:

    * A requests-style api for sending http requests
    * Facilities for populating policies for the client, include defaults,
     and re-using policies from an existing client.
    """

    def __init__(
        self,
        *,
        transport: Optional[HttpTransport] = None,
        config: Optional[Configuration] = None,
        auth_policy: Optional[BearerTokenCredentialPolicy] = None,
        retry_policy: Optional[RetryPolicy] = None,
        **kwargs,
    ):
        """

        :param HttpTransport transport: Http Transport used for requests, defaults to RequestsTransport
        :param Configuration config:
        :param UserAgentPolicy user_agent_policy:
        :param HeadersPolicy headers_policy:
        :param ProxyPolicy proxy_policy:
        :param NetworkTraceLoggingPolicy logging_policy:
        :param HttpLoggingPolicy http_logging_policy:
        :param RetryPolicy retry_policy:
        :param CustomHookPolicy custom_hook_policy:
        :param RedirectPolicy redirect_policy:
        """
        config = config or Configuration()
        
        config.retry_policy = retry_policy or cast(Optional[RetryPolicy], config.retry_policy) or RetryPolicy(**kwargs)
        config.authentication_policy = auth_policy or cast(Optional[BearerTokenCredentialPolicy], config.authentication_policy) or BearerTokenCredentialPolicy(**kwargs)
        super().__init__(
            # RequestsTransport normally should not be imported outside of azure.core, since transports
            # are meant to be user configurable.
            # RequestsTransport is only used in this file as the default transport when not user specified.
            transport=transport or RequestsTransport(**kwargs),
            policies=[
                config.retry_policy,
                config.authentication_policy,
            ],
        )

        self._config = config

    def with_policies(self, **kwargs) -> Self:
        """A named constructor which facilitates creating a new pipeline using an existing one as a base.

           Accepts the same parameters as __init__

        :return: new Pipeline object with combined config of current object
            and specified overrides
        :rtype: Self
        """
        cls = self.__class__
        return cls(config=self._config, transport=kwargs.pop("transport", self._transport), **kwargs)

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[ParamsType] = None,
        headers: Optional[MutableMapping[str, str]] = None,
        json: Any = None,
        content: Optional[ContentType] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[FilesType] = None,
        **kwargs,
    ) -> HttpResponse:
        request = HttpRequest(
            method,
            url,
            params=params,
            headers=headers,
            json=json,
            content=content,
            data=data,
            files=files,
        )

        return self.run(request, **kwargs).http_response

    def __enter__(self) -> Self:
        return cast(Self, super().__enter__())


class AsyncHttpPipeline(AsyncPipeline):
    """A *very* thin wrapper over azure.core.pipeline.AsyncPipeline that facilitates sending miscellaneous
    http requests by adding:

    * A requests-style api for sending http requests
    * Facilities for populating policies for the client, include defaults,
     and re-using policies from an existing client.
    """

    def __init__(
        self,
        *,
        transport: Optional[AsyncHttpTransport] = None,
        config: Optional[Configuration] = None,
        retry_policy: Optional[AsyncRetryPolicy] = None,
        auth_policy: Optional[AsyncBearerTokenCredentialPolicy] = None,
        **kwargs,
    ):
        """

        :param HttpTransport transport: Http Transport used for requests, defaults to RequestsTransport
        :param Configuration config:
        :param AsyncRetryPolicy retry_policy:
        """
        config = config or Configuration()
        
        config.retry_policy = (
            retry_policy or cast(Optional[AsyncRetryPolicy], config.retry_policy) or AsyncRetryPolicy(**kwargs)
        )
        config.authentication_policy = auth_policy or cast(Optional[AsyncBearerTokenCredentialPolicy], config.authentication_policy) or AsyncBearerTokenCredentialPolicy(**kwargs)
        super().__init__(
            # AsyncioRequestsTransport normally should not be imported outside of azure.core, since transports
            # are meant to be user configurable.
            # AsyncioRequestsTransport is only used in this file as the default transport when not user specified.
            transport=transport or AsyncioRequestsTransport(**kwargs),
            policies=[
                config.retry_policy,
                config.authentication_policy,
            ],
        )

        self._config = config

    def with_policies(self, **kwargs) -> Self:
        """A named constructor which facilitates creating a new pipeline using an existing one as a base.

           Accepts the same parameters as __init__

        :return: new Pipeline object with combined config of current object
            and specified overrides
        :rtype: Self
        """
        cls = self.__class__
        return cls(config=self._config, transport=kwargs.pop("transport", self._transport), **kwargs)

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[ParamsType] = None,
        headers: Optional[MutableMapping[str, str]] = None,
        json: Any = None,
        content: Optional[ContentType] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[FilesType] = None,
        **kwargs,
    ) -> AsyncHttpResponse:
        request = HttpRequest(
            method,
            url,
            params=params,
            headers=headers,
            json=json,
            content=content,
            data=data,
            files=files,
        )

        return (await self.run(request, **kwargs)).http_response

    async def __aenter__(self) -> Self:
        return cast(Self, await super().__aenter__())


def get_http_client(**kwargs: Any) -> HttpPipeline:
    """Get an HttpPipeline configured with common policies.

    :returns: An HttpPipeline with a set of applied policies:
    :rtype: HttpPipeline
    """
    return HttpPipeline(**kwargs)


def get_async_http_client(**kwargs: Any) -> AsyncHttpPipeline:
    """Get an AsyncHttpPipeline configured with common policies.

    :returns: An AsyncHttpPipeline with a set of applied policies:
    :rtype: AsyncHttpPipeline
    """
    return AsyncHttpPipeline(**kwargs)