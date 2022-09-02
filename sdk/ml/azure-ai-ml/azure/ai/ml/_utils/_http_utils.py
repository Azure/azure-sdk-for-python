# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=no-self-use

from functools import wraps
from typing import Any, Callable

from typing_extensions import Concatenate, ParamSpec, Self

from azure.core.configuration import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    CustomHookPolicy,
    HeadersPolicy,
    HttpLoggingPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    RedirectPolicy,
    RetryPolicy,
    UserAgentPolicy,
)
from azure.core.pipeline.transport import HttpTransport, RequestsTransport
from azure.core.rest import HttpRequest, HttpResponse


def _request_function(f: Callable[["HttpPipeline"], None]):
    """A decorator that provides the implementation for the request-style
       convenience functions of the HttpPipeline class

    :param Callable[[], None] f: A function whose name will be used as the http
                                 request method
    """

    # This is a hack to provide richer typing for the decorated function
    # The outer _ function allows us to pattern match on the parameter types
    # of HttpRequest and forward those types to the decorated function
    P = ParamSpec("P")

    def _(_: Callable[Concatenate[str, P], Any] = HttpRequest):
        @wraps(f)
        def decorated(self: "HttpPipeline", *args: P.args, **kwargs: P.kwargs) -> HttpResponse:
            """A function that sends an HTTP request and returns the response

            Accepts the same parameters as azure.core.rest.HttpRequest, except for the method.
            All other kwargs are forwarded to azure.core.Pipeline.run

            :param bool stream: Whether to stream the response, defaults to False
            :return HttpResponse:
            """
            request = HttpRequest(
                f.__name__.upper(),
                *args,
                params=kwargs.pop("params", None),
                headers=kwargs.pop("headers", None),
                json=kwargs.pop("json", None),
                content=kwargs.pop("content", None),
                data=kwargs.pop("data", None),
                files=kwargs.pop("files", None),
            )

            return self.run(request, **kwargs).http_response

        return decorated

    return _()


class HttpPipeline(Pipeline):
    """A *very* thin wrapper over azure.core.pipeline.Pipeline that facilitates
    sending miscellaneous http requests by adding:

    * A requests-style api for sending http requests
    * Facilities for populating policies for the client, include defaults,
     and re-using policies from an existing client.
    """

    def __init__(
        self,
        *,
        transport: HttpTransport = None,
        config: Configuration = None,
        user_agent_policy: UserAgentPolicy = None,
        headers_policy: HeadersPolicy = None,
        proxy_policy: ProxyPolicy = None,
        logging_policy: NetworkTraceLoggingPolicy = None,
        http_logging_policy: HttpLoggingPolicy = None,
        retry_policy: RetryPolicy = None,
        custom_hook_policy: CustomHookPolicy = None,
        redirect_policy: RedirectPolicy = None,
        **kwargs
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
        config.headers_policy = headers_policy or config.headers_policy or HeadersPolicy(**kwargs)
        config.proxy_policy = proxy_policy or config.proxy_policy or ProxyPolicy(**kwargs)
        config.redirect_policy = redirect_policy or config.redirect_policy or RedirectPolicy(**kwargs)
        config.retry_policy = retry_policy or config.retry_policy or RetryPolicy(**kwargs)
        config.custom_hook_policy = custom_hook_policy or config.custom_hook_policy or CustomHookPolicy(**kwargs)
        config.logging_policy = logging_policy or config.logging_policy or NetworkTraceLoggingPolicy(**kwargs)
        config.http_logging_policy = http_logging_policy or config.http_logging_policy or HttpLoggingPolicy(**kwargs)
        config.user_agent_policy = user_agent_policy or config.user_agent_policy or UserAgentPolicy(**kwargs)
        config.polling_interval = kwargs.get("polling_interval", 30)

        super().__init__(
            transport=transport or RequestsTransport(**kwargs),
            policies=[
                config.headers_policy,
                config.user_agent_policy,
                config.proxy_policy,
                config.redirect_policy,
                config.retry_policy,
                config.authentication_policy,
                config.custom_hook_policy,
                config.logging_policy,
            ],
        )

        self._config = config

    def with_policies(self, **kwargs) -> Self:
        """A named constructor which facilitates creating a new pipeline
           using an existing one as a base.


           Accepts the same parameters as __init__

        Returns:
            Self: new Pipeline object with combined config of current object
                  and specified overrides
        """
        cls = self.__class__
        return cls(config=self._config, transport=kwargs.pop("transport", self._transport), **kwargs)

    @_request_function
    def delete(self) -> None:
        """Sends a DELETE request."""
        ...

    @_request_function
    def get(self) -> None:
        """Sends a GET request."""
        ...

    @_request_function
    def head(self) -> None:
        """Sends a HEAD request."""
        ...

    @_request_function
    def options(self) -> None:
        """Sends a OPTIONS request."""
        ...

    @_request_function
    def patch(self) -> None:
        """Sends a PATCH request."""
        ...

    @_request_function
    def post(self) -> None:
        """Sends a POST request."""
        ...

    @_request_function
    def put(self) -> None:
        """Sends a PUT request."""
        ...
