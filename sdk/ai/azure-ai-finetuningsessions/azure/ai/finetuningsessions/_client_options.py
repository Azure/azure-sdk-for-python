# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Preserved client defaults expressed through generated constructor options.

Both public client subclasses use this helper instead of editing generated
configuration or replacing a caller-supplied policy list or pipeline.

Default retry policies never replay POST, including heartbeats, regardless of
client or per-call retry counts or method allowlists. To opt into transport
retries for POST, supply an explicit ``retry_policy`` (``RetryPolicy`` for sync,
``AsyncRetryPolicy`` for async) and take responsibility for mutation replay
safety. Caller-owned ``policies`` and ``pipeline`` are also unchanged. Redirect
handling and explicit application-level retry decisions remain unchanged.
"""

from typing import Any, Union
from urllib.parse import urlparse, urlsplit

from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline import PipelineRequest, PipelineResponse, policies
from azure.core.pipeline.policies import AzureKeyCredentialPolicy

from ._version import VERSION

#: Hostnames that count as "local dev" for the purpose of allowing plain http://.
_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


class _NoPostRetryPolicy(policies.RetryPolicy):
    """Keep Azure Core retry configuration except for non-idempotent POST."""

    def send(self, request: PipelineRequest[Any]) -> PipelineResponse[Any, Any]:
        """Disable POST retries before Azure Core consumes per-call options.

        :param request: Request passing through the default client pipeline.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The response from the remaining pipeline policies.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        if request.http_request.method.upper() == "POST":
            # Reapply on each redirect: core pops retry_total from options.
            request.context.options["retry_total"] = 0
        return super().send(request)


class _AsyncNoPostRetryPolicy(policies.AsyncRetryPolicy):
    """Keep async Azure Core retries except for non-idempotent POST."""

    async def send(self, request: PipelineRequest[Any]) -> PipelineResponse[Any, Any]:
        """Disable POST retries before Azure Core consumes per-call options.

        :param request: Request passing through the default async client pipeline.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The response from the remaining pipeline policies.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        if request.http_request.method.upper() == "POST":
            request.context.options["retry_total"] = 0
        return await super().send(request)


def _origin(url: str) -> tuple:
    """Compare scheme, normalized hostname and effective port, not just netloc.

    :param str url: Endpoint or request URL to inspect.
    :return: Scheme, hostname, and effective port.
    :rtype: tuple
    """
    # Requests/urllib3 may treat a backslash before '@' as a path separator,
    # whereas urlsplit treats it as userinfo. Never authenticate that ambiguity.
    if "\\" in url:
        raise ValueError("Endpoint and request URLs must not contain backslashes.")
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    port = parts.port
    return scheme, parts.hostname, port if port is not None else {"http": 80, "https": 443}.get(scheme)


class _ApiKeyTransportPolicy(policies.SansIOHTTPPolicy):
    """Reject unsafe key transports before auth, including explicit auth policies."""

    def __init__(self, endpoint: str, *, allow_insecure_http: bool = False) -> None:
        self.origin = _origin(endpoint)
        self._allow_http = allow_insecure_http and _is_local_endpoint(endpoint)
        self._context_key = f"finetuning-key-origin-{id(self)}"

    def on_request(self, request: Any) -> None:
        target_origin = _origin(request.http_request.url)
        if target_origin[0] != "https" and not (self._allow_http and target_origin == self.origin):
            # A configuration may be constructed for compatibility, but sending
            # credentials is fail-closed. Unlike a transient transport error,
            # this ValueError must not itself trigger connection retries.
            raise ValueError(
                "API key authentication requires HTTPS. allow_insecure_http=True only permits "
                "the configured loopback HTTP origin (localhost, 127.0.0.1, [::1])."
            )
        initial_origin, crossed_origin = request.context.get(self._context_key, (target_origin, False))
        crossed_origin = crossed_origin or target_origin != initial_origin
        request.context[self._context_key] = (initial_origin, crossed_origin)
        # Azure Core compares netloc only: include scheme changes, but do not
        # strip auth for an equivalent explicit default port. Once an origin
        # was crossed, keep cleanup enabled for the rest of this redirect chain.
        request.context["insecure_domain_change"] = crossed_origin


class _ScopedAzureKeyCredentialPolicy(AzureKeyCredentialPolicy):
    """Authenticate only the configured origin, even when core cleanup is disabled."""

    def __init__(self, credential: AzureKeyCredential, endpoint: str, *, allow_insecure_http: bool = False) -> None:
        super().__init__(credential, name="api-key")
        self._transport_policy = _ApiKeyTransportPolicy(endpoint, allow_insecure_http=allow_insecure_http)
        self._context_key = f"finetuning-api-key-{id(self)}"

    def on_request(self, request: Any) -> None:
        self._transport_policy.on_request(request)
        headers = request.http_request.headers
        if _origin(request.http_request.url) != self._transport_policy.origin:
            injected = request.context.pop(self._context_key, None)
            if injected is not None and headers.get("api-key") == injected:
                headers.pop("api-key", None)
            return
        super().on_request(request)
        # Retain the value actually sent, not the credential's possibly rotated
        # value, so redirects cannot retain an earlier SDK-injected key.
        request.context[self._context_key] = headers["api-key"]


class _DirectContextPolicy(policies.SansIOHTTPPolicy):
    """Apply existing direct-route context only to this endpoint's session calls.

    A retry policy placement ensures redirects are rechecked. Headers equal to
    SDK defaults include those prepopulated by conveniences. Track those values
    and remove them outside this scope, without claiming differing caller
    overrides. An identical explicit value cannot be distinguished from an SDK
    default and is conservatively scoped to the endpoint too.
    """

    def __init__(self, endpoint: str) -> None:
        self._origin = _origin(endpoint)
        self._prefix = urlsplit(endpoint).path.rstrip("/") + "/fine_tuning/sessions"
        self._context_key = f"finetuning-direct-headers-{id(self)}"

    def on_request(self, request: Any) -> None:
        target = urlsplit(request.http_request.url)
        matches = _origin(request.http_request.url) == self._origin and (
            target.path == self._prefix or target.path.startswith(self._prefix + "/")
        )
        injected = request.context.get(self._context_key, {})
        # HttpRequest headers are case-insensitive, including a caller override
        # of a differently cased key from the plain dict returned by _base_headers.
        headers = request.http_request.headers
        # Lazy import avoids a root-patch/configuration import cycle.
        from ._patch import _base_headers

        for name, value in _base_headers().items():
            if name.lower() in {"accept", "foundry-features"}:
                continue
            if matches and name not in headers:
                headers[name] = value
            if headers.get(name) == value:
                injected[name.lower()] = value
        if not matches:
            for name, value in injected.items():
                if headers.get(name) == value:
                    headers.pop(name, None)
            injected = {}
        request.context[self._context_key] = injected


def _is_local_endpoint(endpoint: str) -> bool:
    """Return True when ``endpoint`` is an HTTP URL for a loopback host.

    Used to bound ``allow_insecure_http``: skipping HTTPS enforcement is only
    ever appropriate against a local dev server, never against a real regional
    ``loom_api`` reached on the direct (non-APIM) path.

    :param endpoint: Endpoint URL to inspect.
    :type endpoint: str
    :return: Whether the URL uses HTTP and a recognized loopback host.
    :rtype: bool
    """
    if "\\" in endpoint:
        return False
    try:
        parsed = urlparse(endpoint)
    except ValueError:
        return False
    hostname = parsed.hostname
    return (
        parsed.scheme.casefold() == "http"
        and hostname is not None
        and hostname.casefold() in _LOCAL_HOSTS
        and parsed.username is None
        and parsed.password is None
    )


def _is_http_endpoint(endpoint: str) -> bool:
    """Return True when ``endpoint`` explicitly uses plaintext HTTP.

    :param endpoint: Endpoint URL to inspect.
    :type endpoint: str
    :return: Whether the URL explicitly uses the HTTP scheme.
    :rtype: bool
    """
    try:
        return urlparse(endpoint).scheme.casefold() == "http"
    except ValueError:
        return False


class _InsecureBearerTokenCredentialPolicy(policies.BearerTokenCredentialPolicy):
    """BearerTokenCredentialPolicy that skips HTTPS enforcement (for local/http:// dev)."""

    def on_request(self, request: Any) -> None:
        request.context.options["enforce_https"] = False
        super().on_request(request)


class _InsecureAsyncBearerTokenCredentialPolicy(policies.AsyncBearerTokenCredentialPolicy):
    """Async bearer policy that permits loopback HTTP for local development."""

    async def on_request(self, request: Any) -> None:
        request.context.options["enforce_https"] = False
        await super().on_request(request)


def _prepare_client_options(
    endpoint: str,
    credential: Any,
    options: dict[str, Any],
    *,
    allow_insecure_http: bool = False,
    asynchronous: bool = False,
) -> dict[str, Any]:
    """Translate the frozen configuration behavior into supported policy kwargs.

    :param endpoint: Service endpoint for policy scope and local-development validation.
    :type endpoint: str
    :param credential: Token or API-key credential supplied by the caller.
    :type credential: ~typing.Any
    :param options: Caller options, copied before adding preview-compatible defaults.
    :type options: dict[str, ~typing.Any]
    :keyword allow_insecure_http: Permit authentication on loopback HTTP only.
    :paramtype allow_insecure_http: bool
    :keyword asynchronous: Select policies compatible with the async pipeline.
    :paramtype asynchronous: bool
    :return: Prepared constructor options, preserving caller-owned policies and pipelines.
    :rtype: dict[str, ~typing.Any]
    """
    if endpoint is None:
        raise ValueError("Parameter 'endpoint' must not be None.")
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if (
        allow_insecure_http
        and not isinstance(credential, AzureKeyCredential)
        and _is_http_endpoint(endpoint)
        and not _is_local_endpoint(endpoint)
    ):
        raise ValueError(
            "allow_insecure_http=True with an HTTP endpoint is only supported "
            "for local endpoints "
            f"(http://localhost, 127.0.0.1, [::1]); got {endpoint!r}."
        )

    kwargs = dict(options)
    kwargs.setdefault("sdk_moniker", "finetuning-sessions/{}".format(VERSION))
    kwargs.setdefault("credential_scopes", ["https://ai.azure.com/.default"])
    # Explicit policy lists/pipelines remain owned by the caller. Default
    # pipelines get the same environment context as the training conveniences.
    if kwargs.get("policies") is None and kwargs.get("pipeline") is None:
        if kwargs.get("retry_policy") is None:
            kwargs["retry_policy"] = _AsyncNoPostRetryPolicy(**kwargs) if asynchronous else _NoPostRetryPolicy(**kwargs)
        custom = kwargs.get("per_retry_policies") or []
        custom = list(custom) if isinstance(custom, (list, tuple)) else [custom]
        if isinstance(credential, AzureKeyCredential):
            custom.append(_ApiKeyTransportPolicy(endpoint, allow_insecure_http=allow_insecure_http))
        # Do not replace the built-in blocked headers or mutate the caller's
        # list. Cleanup runs after authentication and catches reinjection by an
        # explicit auth policy. Direct-context headers are value-owned instead:
        # globally blocking their names would discard distinct caller overrides.
        blocked = policies.SensitiveHeaderCleanupPolicy.DEFAULT_SENSITIVE_HEADERS | {"api-key"}
        blocked.update(kwargs.get("blocked_redirect_headers") or [])
        kwargs["blocked_redirect_headers"] = sorted({name.lower() for name in blocked})
        kwargs["per_retry_policies"] = [*custom, _DirectContextPolicy(endpoint)]
    if credential and not kwargs.get("authentication_policy"):
        if isinstance(credential, AzureKeyCredential):
            kwargs["authentication_policy"] = _ScopedAzureKeyCredentialPolicy(
                credential, endpoint, allow_insecure_http=allow_insecure_http
            )
        else:
            policy_cls: type[Union[policies.BearerTokenCredentialPolicy, policies.AsyncBearerTokenCredentialPolicy]]
            if asynchronous:
                policy_cls = (
                    _InsecureAsyncBearerTokenCredentialPolicy
                    if allow_insecure_http and _is_local_endpoint(endpoint)
                    else policies.AsyncBearerTokenCredentialPolicy
                )
            else:
                policy_cls = (
                    _InsecureBearerTokenCredentialPolicy
                    if allow_insecure_http and _is_local_endpoint(endpoint)
                    else policies.BearerTokenCredentialPolicy
                )
            policy_options = dict(kwargs)
            credential_scopes = policy_options.pop("credential_scopes")
            if not asynchronous:
                policy_options.pop("api_version", None)
            kwargs["authentication_policy"] = policy_cls(credential, *credential_scopes, **policy_options)
    return kwargs


def _patch_configuration(module: Any, *, asynchronous: bool = False) -> None:
    """Keep the preview's private configuration imports regeneration-safe.

    Public clients use constructor options. This hook also preserves existing
    direct configuration callers, including the unmodified upstream tests.

    :param module: Generated configuration module whose compatibility exports are populated.
    :type module: ~typing.Any
    :keyword asynchronous: Whether this is the async configuration module.
    :paramtype asynchronous: bool
    """
    generated = module.FineTuningSessionClientConfiguration
    if getattr(generated, "_preview_configuration", False):
        return

    # This private compatibility class deliberately wraps the runtime-selected
    # sync/async generated configuration; no public type is weakened.
    class FineTuningSessionClientConfiguration(generated):  # type: ignore[valid-type,misc]
        _preview_configuration = True

        def __init__(self, endpoint: str, credential: Any, *, allow_insecure_http: bool = False, **kwargs: Any) -> None:
            options = _prepare_client_options(
                endpoint,
                credential,
                kwargs,
                allow_insecure_http=allow_insecure_http,
                asynchronous=asynchronous,
            )
            super().__init__(endpoint=endpoint, credential=credential, **options)
            self.allow_insecure_http = allow_insecure_http
            if not asynchronous:
                self.api_version = kwargs.get("api_version", "v1")

    module.FineTuningSessionClientConfiguration = FineTuningSessionClientConfiguration
    # These exact private exports preserve direct configuration imports from
    # the tested preview; they are not accesses to a third-party client's state.
    # pylint: disable=protected-access
    module._is_local_endpoint = _is_local_endpoint
    module._is_http_endpoint = _is_http_endpoint
    module._LOCAL_HOSTS = _LOCAL_HOSTS
    if asynchronous:
        module._InsecureAsyncBearerTokenCredentialPolicy = _InsecureAsyncBearerTokenCredentialPolicy
    else:
        module._InsecureBearerTokenCredentialPolicy = _InsecureBearerTokenCredentialPolicy
    # pylint: enable=protected-access
