# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import threading
from typing import Dict, Optional
from urllib import parse

from .http_challenge import HttpChallenge


_cache: "Dict[str, HttpChallenge]" = {}
_lock = threading.Lock()


def get_challenge_for_url(url: str) -> "Optional[HttpChallenge]":
    """Gets the challenge for the cached URL.

    :param str url: the URL the challenge is cached for.

    :returns: The challenge for the cached request URL, or None if the request URL isn't cached.
    :rtype: HttpChallenge or None
    """

    if not url:
        raise ValueError("URL cannot be None")

    key = _get_cache_key(url)

    with _lock:
        return _cache.get(key.lower())


def _get_cache_key(url: str) -> str:
    """Use the URL's netloc as cache key except when the URL specifies the default port for its scheme. In that case
    use the netloc without the port. That is to say, https://foo.bar and https://foo.bar:443 are considered equivalent.

    This equivalency prevents an unnecessary challenge when using Key Vault's paging API. The Key Vault client doesn't
    specify ports, but Key Vault's next page links do, so a redundant challenge would otherwise be executed when the
    client requests the next page.

    :param str url: The HTTP request URL.

    :returns: The URL's `netloc`, minus any port attached to the URL.
    :rtype: str
    """

    parsed = parse.urlparse(url)
    if parsed.scheme == "https" and parsed.port == 443:
        return parsed.netloc[:-4]
    return parsed.netloc


def remove_challenge_for_url(url: str, expected_challenge: Optional[HttpChallenge] = None) -> None:
    """Removes the cached challenge for the specified URL.

    :param str url: the URL for which to remove the cached challenge
    :param expected_challenge: Remove only this challenge, if it is still cached. None removes any cached challenge.
    :type expected_challenge: HttpChallenge or None
    """
    if not url:
        raise ValueError("URL cannot be empty")

    key = _get_cache_key(url).lower()
    with _lock:
        if expected_challenge is None or _cache.get(key) is expected_challenge:
            _cache.pop(key, None)


def remove_challenge_for_url_if_matches(url: str, expected_challenge: Optional[HttpChallenge]) -> None:
    """Remove only the cached challenge observed by the caller.

    :param str url: The URL for which to remove the cached challenge.
    :param expected_challenge: The observed challenge, or None when no challenge was observed.
    :type expected_challenge: HttpChallenge or None
    """
    if not url:
        raise ValueError("URL cannot be empty")

    key = _get_cache_key(url).lower()
    with _lock:
        if expected_challenge is not None and _cache.get(key) is expected_challenge:
            _cache.pop(key, None)


def set_challenge_for_url(url: str, challenge: "HttpChallenge") -> None:
    """Caches the challenge for the specified URL.

    :param str url: the URL for which to cache the challenge
    :param challenge: the challenge to cache
    :type challenge: HttpChallenge
    """
    if not url:
        raise ValueError("URL cannot be empty")

    if not challenge:
        raise ValueError("Challenge cannot be empty")

    src_url = parse.urlparse(url)
    if src_url.netloc.lower() != challenge.source_authority.lower():
        raise ValueError("Source URL and Challenge URL do not match")

    key = _get_cache_key(url)
    with _lock:
        _cache[key.lower()] = challenge


def clear() -> None:
    """Clears the cache."""

    with _lock:
        _cache.clear()
