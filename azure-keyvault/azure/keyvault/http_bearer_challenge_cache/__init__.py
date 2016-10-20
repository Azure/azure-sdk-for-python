#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

try:
    import urllib.parse as parse
except ImportError:
    import urlparse as parse # pylint: disable=import-error

_cache = {}

def get_challenge_for_url(url):
    """ Gets the challenge for the cached URL.
    :param url: the URL the challenge is cached for.
    :rtype: HttpBearerChallenge """
    if not url:
        raise ValueError('URL cannot be None')

    url = parse.urlparse(url)
    return _cache.get(url.netloc)

def remove_challenge_for_url(url):
    """ Removes the cached challenge for the specified URL.
    :param url: the URL for which to remove the cached challenge """
    if not url:
        raise ValueError('URL cannot be empty')

    url = parse.urlparse(url)
    del _cache[url.netloc]

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

    _cache[src_url.netloc] = challenge

def clear():
    """ Clears the cache. """
    _cache.clear() # pylint: disable=redefined-outer-name,unused-variable
