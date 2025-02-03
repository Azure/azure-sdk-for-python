# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Any, Dict, MutableMapping, Optional, TypedDict, cast

from typing_extensions import Self, Unpack

from azure.ai.evaluation._user_agent import USER_AGENT
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
from azure.core.rest import AsyncHttpResponse, HttpRequest, HttpResponse
from azure.core.rest._rest_py3 import ContentType, FilesType, ParamsType


class RequestKwargs(TypedDict, total=False):
    """Keyword arguments for request-style http request functions

    .. note::

        Ideally, we'd be able to express that these are the known subset of kwargs, but it's possible to provide
        others. But that currently isn't possible; there's no way currently to express a TypedDict that expects
        a known set of keys and an unknown set of keys.

        PEP 728 - TypedDict with Typed Extra Items (https://peps.python.org/pep-0728/) would rectify this but it's
        still in Draft status.
    """

    params: ParamsType
    headers: MutableMapping[str, str]
    json: Any
    content: ContentType
    data: Dict[str, Any]
    files: FilesType


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
        user_agent_policy: Optional[UserAgentPolicy] = None,
        headers_policy: Optional[HeadersPolicy] = None,
        proxy_policy: Optional[ProxyPolicy] = None,
        logging_policy: Optional[NetworkTraceLoggingPolicy] = None,
        http_logging_policy: Optional[HttpLoggingPolicy] = None,
        retry_policy: Optional[RetryPolicy] = None,
        custom_hook_policy: Optional[CustomHookPolicy] = None,
        redirect_policy: Optional[RedirectPolicy] = None,
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
        config.headers_policy = (
            headers_policy or cast(Optional[HeadersPolicy], config.headers_policy) or HeadersPolicy(**kwargs)
        )
        config.proxy_policy = proxy_policy or cast(Optional[ProxyPolicy], config.proxy_policy) or ProxyPolicy(**kwargs)
        config.redirect_policy = (
            redirect_policy or cast(Optional[RedirectPolicy], config.redirect_policy) or RedirectPolicy(**kwargs)
        )
        config.retry_policy = retry_policy or cast(Optional[RetryPolicy], config.retry_policy) or RetryPolicy(**kwargs)
        config.custom_hook_policy = (
            custom_hook_policy
            or cast(Optional[CustomHookPolicy], config.custom_hook_policy)
            or CustomHookPolicy(**kwargs)
        )
        config.logging_policy = (
            logging_policy
            or cast(Optional[NetworkTraceLoggingPolicy], config.logging_policy)
            or NetworkTraceLoggingPolicy(**kwargs)
        )
        config.http_logging_policy = (
            http_logging_policy
            or cast(Optional[HttpLoggingPolicy], config.http_logging_policy)
            or HttpLoggingPolicy(**kwargs)
        )
        config.user_agent_policy = (
            user_agent_policy or cast(Optional[UserAgentPolicy], config.user_agent_policy) or UserAgentPolicy(**kwargs)
        )
        config.polling_interval = kwargs.get("polling_interval", 30)

        super().__init__(
            # RequestsTransport normally should not be imported outside of azure.core, since transports
            # are meant to be user configurable.
            # RequestsTransport is only used in this file as the default transport when not user specified.
            transport=transport or RequestsTransport(**kwargs),
            policies=[
                config.headers_policy,
                config.user_agent_policy,
                config.proxy_policy,
                config.redirect_policy,
                config.retry_policy,
                config.custom_hook_policy,
                config.logging_policy,
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

    def delete(self: "HttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> HttpResponse:
        """Send a DELETE request.

        :param str url: The request url
        :returns: The request response
        :rtype: HttpResponse
        """

        return self.request(self.delete.__name__.upper(), url, **kwargs)

    def put(self: "HttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> HttpResponse:
        """Send a PUT request.

        :param str url: The request url
        :returns: The request response
        :rtype: HttpResponse
        """

        return self.request(self.put.__name__.upper(), url, **kwargs)

    def get(self: "HttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> HttpResponse:
        """Send a GET request.

        :param str url: The request url
        :returns: The request response
        :rtype: HttpResponse
        """

        return self.request(self.get.__name__.upper(), url, **kwargs)

    def post(self: "HttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> HttpResponse:
        """Send a POST request.

        :param str url: The request url
        :returns: The request response
        :rtype: HttpResponse
        """

        return self.request(self.post.__name__.upper(), url, **kwargs)

    def head(self: "HttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> HttpResponse:
        """Send a HEAD request.

        :param str url: The request url
        :returns: The request response
        :rtype: HttpResponse
        """

        return self.request(self.head.__name__.upper(), url, **kwargs)

    def options(self: "HttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> HttpResponse:
        """Send a OPTIONS request.

        :param str url: The request url
        :returns: The request response
        :rtype: HttpResponse
        """

        return self.request(self.options.__name__.upper(), url, **kwargs)

    def patch(self: "HttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> HttpResponse:
        """Send a PATCH request.

        :param str url: The request url
        :returns: The request response
        :rtype: HttpResponse
        """

        return self.request(self.patch.__name__.upper(), url, **kwargs)

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
        user_agent_policy: Optional[UserAgentPolicy] = None,
        headers_policy: Optional[HeadersPolicy] = None,
        proxy_policy: Optional[ProxyPolicy] = None,
        logging_policy: Optional[NetworkTraceLoggingPolicy] = None,
        http_logging_policy: Optional[HttpLoggingPolicy] = None,
        retry_policy: Optional[AsyncRetryPolicy] = None,
        custom_hook_policy: Optional[CustomHookPolicy] = None,
        redirect_policy: Optional[AsyncRedirectPolicy] = None,
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
        :param AsyncRetryPolicy retry_policy:
        :param CustomHookPolicy custom_hook_policy:
        :param AsyncRedirectPolicy redirect_policy:
        """
        config = config or Configuration()
        config.headers_policy = (
            headers_policy or cast(Optional[HeadersPolicy], config.headers_policy) or HeadersPolicy(**kwargs)
        )
        config.proxy_policy = proxy_policy or cast(Optional[ProxyPolicy], config.proxy_policy) or ProxyPolicy(**kwargs)
        config.redirect_policy = (
            redirect_policy
            or cast(Optional[AsyncRedirectPolicy], config.redirect_policy)
            or AsyncRedirectPolicy(**kwargs)
        )
        config.retry_policy = (
            retry_policy or cast(Optional[AsyncRetryPolicy], config.retry_policy) or AsyncRetryPolicy(**kwargs)
        )
        config.custom_hook_policy = (
            custom_hook_policy
            or cast(Optional[CustomHookPolicy], config.custom_hook_policy)
            or CustomHookPolicy(**kwargs)
        )
        config.logging_policy = (
            logging_policy
            or cast(Optional[NetworkTraceLoggingPolicy], config.logging_policy)
            or NetworkTraceLoggingPolicy(**kwargs)
        )
        config.http_logging_policy = (
            http_logging_policy
            or cast(Optional[HttpLoggingPolicy], config.http_logging_policy)
            or HttpLoggingPolicy(**kwargs)
        )
        config.user_agent_policy = (
            user_agent_policy or cast(Optional[UserAgentPolicy], config.user_agent_policy) or UserAgentPolicy(**kwargs)
        )
        config.polling_interval = kwargs.get("polling_interval", 30)

        super().__init__(
            # AsyncioRequestsTransport normally should not be imported outside of azure.core, since transports
            # are meant to be user configurable.
            # AsyncioRequestsTransport is only used in this file as the default transport when not user specified.
            transport=transport or AsyncioRequestsTransport(**kwargs),
            policies=[
                config.headers_policy,
                config.user_agent_policy,
                config.proxy_policy,
                config.redirect_policy,
                config.retry_policy,
                config.custom_hook_policy,
                config.logging_policy,
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

    async def delete(self: "AsyncHttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> AsyncHttpResponse:
        """Send a DELETE request.

        :param str url: The request url
        :returns: The request response
        :rtype: AsyncHttpResponse
        """
        return await self.request(self.delete.__name__.upper(), url, **kwargs)

    async def put(self: "AsyncHttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> AsyncHttpResponse:
        """Send a PUT request.

        :param str url: The request url
        :returns: The request response
        :rtype: AsyncHttpResponse
        """

        return await self.request(self.put.__name__.upper(), url, **kwargs)

    async def get(self: "AsyncHttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> AsyncHttpResponse:
        """Send a GET request.

        :param str url: The request url
        :returns: The request response
        :rtype: AsyncHttpResponse
        """

        return await self.request(self.get.__name__.upper(), url, **kwargs)

    async def post(self: "AsyncHttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> AsyncHttpResponse:
        """Send a POST request.

        :param str url: The request url
        :returns: The request response
        :rtype: AsyncHttpResponse
        """

        return await self.request(self.post.__name__.upper(), url, **kwargs)

    async def head(self: "AsyncHttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> AsyncHttpResponse:
        """Send a HEAD request.

        :param str url: The request url
        :returns: The request response
        :rtype: AsyncHttpResponse
        """

        return await self.request(self.head.__name__.upper(), url, **kwargs)

    async def options(self: "AsyncHttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> AsyncHttpResponse:
        """Send a OPTIONS request.

        :param str url: The request url
        :returns: The request response
        :rtype: AsyncHttpResponse
        """

        return await self.request(self.options.__name__.upper(), url, **kwargs)

    async def patch(self: "AsyncHttpPipeline", url: str, **kwargs: Unpack[RequestKwargs]) -> AsyncHttpResponse:
        """Send a PATCH request.

        :param str url: The request url
        :returns: The request response
        :rtype: AsyncHttpResponse
        """

        return await self.request(self.patch.__name__.upper(), url, **kwargs)

    async def __aenter__(self) -> Self:
        return cast(Self, await super().__aenter__())


def get_http_client(**kwargs: Any) -> HttpPipeline:
    """Get an HttpPipeline configured with common policies.

    :returns: An HttpPipeline with a set of applied policies:
    :rtype: HttpPipeline
    """
    kwargs.setdefault("user_agent_policy", UserAgentPolicy(base_user_agent=USER_AGENT))
    return HttpPipeline(**kwargs)


def get_async_http_client(**kwargs: Any) -> AsyncHttpPipeline:
    """Get an AsyncHttpPipeline configured with common policies.

    :returns: An AsyncHttpPipeline with a set of applied policies:
    :rtype: AsyncHttpPipeline
    """
    kwargs.setdefault("user_agent_policy", UserAgentPolicy(base_user_agent=USER_AGENT))
    return AsyncHttpPipeline(**kwargs)
