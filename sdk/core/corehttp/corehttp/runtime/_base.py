# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from typing import Any, Dict
from urllib.parse import urlparse


def _format_url_section(template, **kwargs: Dict[str, str]) -> str:
    """String format the template with the kwargs, auto-skip sections of the template that are NOT in the kwargs.

    By default in Python, "format" will raise a KeyError if a template element is not found. Here the section between
    the slashes will be removed from the template instead.

    This is used for API like Storage, where when Swagger has template section not defined as parameter.

    :param str template: a string template to fill
    :rtype: str
    :returns: Template completed
    """
    last_template = template
    components = template.split("/")
    while components:
        try:
            return template.format(**kwargs)
        except KeyError as key:
            formatted_components = template.split("/")
            components = [c for c in formatted_components if "{{{}}}".format(key.args[0]) not in c]
            template = "/".join(components)
            if last_template == template:
                raise ValueError(
                    f"The value provided for the url part '{template}' was incorrect, and resulted in an invalid url"
                ) from key
            last_template = template
    return last_template


def _urljoin(base_url: str, stub_url: str) -> str:
    """Append to end of base URL without losing query parameters.

    :param str base_url: The base URL.
    :param str stub_url: Section to append to the end of the URL path.
    :returns: The updated URL.
    :rtype: str
    """
    parsed_base_url = urlparse(base_url)

    # Can't use "urlparse" on a partial url, we get incorrect parsing for things like
    # document:build?format=html&api-version=2019-05-01
    split_url = stub_url.split("?", 1)
    stub_url_path = split_url.pop(0)
    stub_url_query = split_url.pop() if split_url else None

    # Note that _replace is a public API named that way to avoid conflicts in namedtuple
    # https://docs.python.org/3/library/collections.html?highlight=namedtuple#collections.namedtuple
    parsed_base_url = parsed_base_url._replace(
        path=parsed_base_url.path.rstrip("/") + "/" + stub_url_path,
    )
    if stub_url_query:
        query_params = [stub_url_query]
        if parsed_base_url.query:
            query_params.insert(0, parsed_base_url.query)
        parsed_base_url = parsed_base_url._replace(query="&".join(query_params))
    return parsed_base_url.geturl()


class PipelineClientBase:
    """Base class for pipeline clients.

    :param str endpoint: URL for the request.
    """

    def __init__(self, endpoint: str):
        self._endpoint = endpoint

    def format_url(self, url_template: str, **kwargs: Any) -> str:
        """Format request URL with the client base URL, unless the
        supplied URL is already absolute.

        Note that both the base url and the template url can contain query parameters.

        :param str url_template: The request URL to be formatted if necessary.
        :rtype: str
        :return: The formatted URL.
        """
        url = _format_url_section(url_template, **kwargs)
        if url:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                url = url.lstrip("/")
                try:
                    base = self._endpoint.format(**kwargs).rstrip("/")
                except KeyError as key:
                    err_msg = "The value provided for the url part {} was incorrect, and resulted in an invalid url"
                    raise ValueError(err_msg.format(key.args[0])) from key

                url = _urljoin(base, url)
        else:
            url = self._endpoint.format(**kwargs)
        return url
