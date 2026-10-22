# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Custom redirect policies that cache the redirect target URL for write operations.

Write requests (POST / PUT / PATCH / DELETE) that receive a 307 redirect from
the load-balancer are followed, and the target URL's base (scheme + host) is
cached so that subsequent writes skip the load-balancer entirely.

Read requests (GET, HEAD, OPTIONS, …) **never** consult or populate the cache
and always go through the load-balancer.

The cache is invalidated on 5xx responses or transport errors so that a
failover is respected on the next write.

Redirect destination policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A redirect is only followed when **all** of the following hold for the target:

* the scheme is ``https`` (an ``https`` -> ``http`` downgrade is rejected so the
  bearer token can never travel over cleartext);
* the effective port matches the original request's effective port (the scheme
  default — 443 for ``https`` — is used when no port is given); and
* the host is the original request host or one of its subdomains (e.g. an
  individual ledger node).

Redirects to sibling ledgers, parent domains, unrelated hosts, look-alike suffix
domains, downgraded (``http``) schemes, or different ports are rejected and never
followed or cached. This prevents a misconfigured or malicious load-balancer from
redirecting requests (and their sensitive headers, including the ``Authorization``
bearer token which is *not* stripped on redirect) to an unintended destination.

Thread-safety
~~~~~~~~~~~~~
* Reads of the cached value are lock-free (CPython GIL guarantees atomic
  reference reads — *Volatile.Read* semantics).
* Writes are protected by a :class:`threading.Lock` (*Volatile.Write*
  semantics) so that at most one thread mutates the cached reference at a
  time.
"""

import logging
import threading
from typing import FrozenSet, Optional
from urllib.parse import ParseResult, urlparse, urlunparse

from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import AsyncHTTPPolicy, HTTPPolicy

_LOGGER = logging.getLogger(__name__)

_WRITE_METHODS: FrozenSet[str] = frozenset({"POST", "PUT", "PATCH", "DELETE"})

_REDIRECT_STATUS_CODES = frozenset({301, 302, 307, 308})


class _RedirectUrlCache:
    """Thread-safe cache for a redirect target base URL."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cached_base_url: Optional[str] = None

    # -- Volatile.Read --------------------------------------------------
    def get(self) -> Optional[str]:
        """Return the cached base URL or *None* (lock-free)."""
        return self._cached_base_url

    # -- Volatile.Write -------------------------------------------------
    def set(self, url: str) -> None:  # pylint: disable=redefined-builtin
        """Extract and cache the base URL (scheme + host) from *url*.

        :param str url: The full redirect target URL.
        """
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        with self._lock:
            self._cached_base_url = base_url

    def invalidate(self) -> None:
        """Clear the cached value."""
        with self._lock:
            self._cached_base_url = None


def _rewrite_url(original_url: str, cached_base_url: str) -> str:
    """Replace the scheme + host of *original_url* with *cached_base_url*.

    :param str original_url: The original request URL.
    :param str cached_base_url: The cached base URL (scheme + host) to use.
    :return: The rewritten URL.
    :rtype: str
    """
    original = urlparse(original_url)
    cached = urlparse(cached_base_url)
    return urlunparse(
        (
            cached.scheme,
            cached.netloc,
            original.path,
            original.params,
            original.query,
            original.fragment,
        )
    )


def _is_redirect(status_code: int) -> bool:
    return status_code in _REDIRECT_STATUS_CODES


def _effective_port(parsed: ParseResult) -> Optional[int]:
    """Return the effective port for a parsed URL, applying the scheme default.

    :param parsed: A :func:`urllib.parse.urlparse` result.
    :type parsed: ~urllib.parse.ParseResult
    :return: The explicit port, or the scheme default (443 for ``https``,
        80 for ``http``), or ``None`` if it cannot be determined.
    :rtype: Optional[int]
    """
    try:
        explicit = parsed.port
    except ValueError:
        # An invalid (out-of-range) port in the URL.
        return None
    if explicit is not None:
        return explicit
    scheme = (parsed.scheme or "").lower()
    if scheme == "https":
        return 443
    if scheme == "http":
        return 80
    return None


def _is_allowed_redirect_target(original_url: str, target_url: str) -> bool:
    """Return whether *target_url* is an allowed redirect destination.

    A redirect is permitted only when **all** of these hold:

    * the target scheme is ``https`` (no downgrade — the bearer token must never
      travel over cleartext);
    * the target's effective port equals the original request's effective port
      (the scheme default is used when no port is present); and
    * the target host is identical to the original request host or is a subdomain
      of it.

    All other targets — sibling hosts, parent domains, unrelated hosts, look-alike
    suffix domains, downgraded schemes, and different ports — are rejected. Host
    comparison is case-insensitive.

    :param str original_url: The URL of the original request.
    :param str target_url: The redirect target URL (e.g. from a ``Location`` header).
    :return: True if the redirect target is permitted, otherwise False.
    :rtype: bool
    """
    original = urlparse(original_url)
    target = urlparse(target_url)

    original_host = (original.hostname or "").lower()
    target_host = (target.hostname or "").lower()

    # Fail safe: if either host cannot be determined, do not follow the redirect.
    if not original_host or not target_host:
        return False

    # Require HTTPS on the target so the bearer token is never sent over cleartext.
    if (target.scheme or "").lower() != "https":
        return False

    # Require the same effective port (scheme default applied when absent).
    original_port = _effective_port(original)
    target_port = _effective_port(target)
    if original_port is None or target_port is None or original_port != target_port:
        return False

    # Require the same host or a subdomain of the original host.
    return target_host == original_host or target_host.endswith("." + original_host)


class RedirectCachingPolicy(HTTPPolicy):
    """Synchronous redirect policy with write-URL caching.

    Replaces the default :class:`~azure.core.pipeline.policies.RedirectPolicy`
    in the pipeline.  See module docstring for caching semantics.

    :keyword bool permit_redirects: Whether redirects are followed at all.
        Defaults to ``True``.
    :keyword int redirect_max: Maximum number of redirects to follow per
        request.  Defaults to ``5``.
    """

    def __init__(
        self,
        *,
        permit_redirects: bool = True,
        redirect_max: int = 5,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        super().__init__()
        self._permit_redirects = permit_redirects
        self._max_redirects = redirect_max
        self._cache = _RedirectUrlCache()

    def send(self, request: PipelineRequest) -> PipelineResponse:
        method = request.http_request.method.upper()
        is_write = method in _WRITE_METHODS

        # Capture the pristine request host (before any cache rewrite) so that
        # redirect targets are validated against the original ledger endpoint.
        original_url = request.http_request.url

        # For writes, rewrite the URL to the cached primary (if warm).
        if is_write:
            cached = self._cache.get()
            if cached:
                request.http_request.url = _rewrite_url(
                    request.http_request.url, cached
                )
                _LOGGER.debug(
                    "Using cached redirect URL for %s: %s",
                    method,
                    request.http_request.url,
                )

        # Send the request downstream.
        try:
            response = self.next.send(request)
        except Exception:
            if is_write:
                self._cache.invalidate()
                _LOGGER.debug("Transport error on write; invalidated redirect cache")
            raise

        if not self._permit_redirects:
            return response

        # Follow redirect chain.
        redirects_remaining = self._max_redirects
        while (
            _is_redirect(response.http_response.status_code)
            and redirects_remaining > 0
        ):
            redirect_url = response.http_response.headers.get("Location")
            if not redirect_url:
                break

            # Enforce the redirect destination policy: only the original host or
            # one of its subdomains may be followed.
            if not _is_allowed_redirect_target(original_url, redirect_url):
                _LOGGER.warning(
                    "Refusing to follow redirect to disallowed target: %s",
                    redirect_url,
                )
                break

            # Only cache for write methods.
            if is_write:
                self._cache.set(redirect_url)
                _LOGGER.debug("Cached redirect target for writes: %s", redirect_url)

            request.http_request.url = redirect_url
            redirects_remaining -= 1

            try:
                response = self.next.send(request)
            except Exception:
                if is_write:
                    self._cache.invalidate()
                    _LOGGER.debug(
                        "Transport error following redirect; invalidated cache"
                    )
                raise

        # Invalidate cache on server errors for writes.
        if is_write and response.http_response.status_code >= 500:
            self._cache.invalidate()
            _LOGGER.debug("5xx on write; invalidated redirect cache")

        return response


class AsyncRedirectCachingPolicy(AsyncHTTPPolicy):
    """Asynchronous redirect policy with write-URL caching.

    Async counterpart of :class:`RedirectCachingPolicy`.
    """

    def __init__(
        self,
        *,
        permit_redirects: bool = True,
        redirect_max: int = 5,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        super().__init__()
        self._permit_redirects = permit_redirects
        self._max_redirects = redirect_max
        self._cache = _RedirectUrlCache()

    async def send(self, request: PipelineRequest) -> PipelineResponse:
        method = request.http_request.method.upper()
        is_write = method in _WRITE_METHODS

        # Capture the pristine request host (before any cache rewrite) so that
        # redirect targets are validated against the original ledger endpoint.
        original_url = request.http_request.url

        if is_write:
            cached = self._cache.get()
            if cached:
                request.http_request.url = _rewrite_url(
                    request.http_request.url, cached
                )
                _LOGGER.debug(
                    "Using cached redirect URL for %s: %s",
                    method,
                    request.http_request.url,
                )

        try:
            response = await self.next.send(request)
        except Exception:
            if is_write:
                self._cache.invalidate()
                _LOGGER.debug("Transport error on write; invalidated redirect cache")
            raise

        if not self._permit_redirects:
            return response

        redirects_remaining = self._max_redirects
        while (
            _is_redirect(response.http_response.status_code)
            and redirects_remaining > 0
        ):
            redirect_url = response.http_response.headers.get("Location")
            if not redirect_url:
                break

            # Enforce the redirect destination policy: only the original host or
            # one of its subdomains may be followed.
            if not _is_allowed_redirect_target(original_url, redirect_url):
                _LOGGER.warning(
                    "Refusing to follow redirect to disallowed target: %s",
                    redirect_url,
                )
                break

            if is_write:
                self._cache.set(redirect_url)
                _LOGGER.debug("Cached redirect target for writes: %s", redirect_url)

            request.http_request.url = redirect_url
            redirects_remaining -= 1

            try:
                response = await self.next.send(request)
            except Exception:
                if is_write:
                    self._cache.invalidate()
                    _LOGGER.debug(
                        "Transport error following redirect; invalidated cache"
                    )
                raise

        if is_write and response.http_response.status_code >= 500:
            self._cache.invalidate()
            _LOGGER.debug("5xx on write; invalidated redirect cache")

        return response
