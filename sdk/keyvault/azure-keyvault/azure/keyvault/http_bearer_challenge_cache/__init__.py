#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

from threading import Lock

try:
    import urllib.parse as parse
except ImportError:
    import urlparse as parse # pylint: disable=import-error

_cache = {}
_lock = Lock()

def get_challenge_for_url(url):
    """ Gets the challenge for the cached URL.
    :param url: the URL the challenge is cached for.
    :rtype: HttpBearerChallenge """
    if not url:
        raise ValueError('URL cannot be None')

    url = parse.urlparse(url)

    _lock.acquire()

    val = _cache.get(url.netloc)

    _lock.release()

    return val


def remove_challenge_for_url(url):
    """ Removes the cached challenge for the specified URL.
    :param url: the URL for which to remove the cached challenge """
    if not url:
        raise ValueError('URL cannot be empty')

    url = parse.urlparse(url)

    _lock.acquire()

    del _cache[url.netloc]

    _lock.release()


def set_challenge_for_url(url, challenge):
    """ Caches the challenge for the specified URL.
    :param url: the URL for which to cache the challenge
    :param challenge: the challenge to cache """
    if not url:
        raise ValueError('URL cannot be empty')

    if not challenge:
        raise ValueError('Challenge cannot be empty')

    src_url = parse.urlparse(url)
    if src_url.netloc != challenge.source_authority:
        raise ValueError('Source URL and Challenge URL do not match')

    _lock.acquire()

    _cache[src_url.netloc] = challenge

    _lock.release()


def clear():
    """ Clears the cache. """

    _lock.acquire()

    _cache.clear() # pylint: disable=redefined-outer-name,unused-variable

    _lock.release()
