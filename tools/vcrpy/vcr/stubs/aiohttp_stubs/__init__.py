"""Stubs for aiohttp HTTP clients"""
from __future__ import absolute_import

import asyncio
import functools
import logging
import json

from aiohttp import ClientConnectionError, ClientResponse, RequestInfo, streams
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from vcr.request import Request

log = logging.getLogger(__name__)


class MockStream(asyncio.StreamReader, streams.AsyncStreamReaderMixin):
    pass


class MockClientResponse(ClientResponse):
    def __init__(self, method, url, request_info=None):
        super().__init__(
            method=method,
            url=url,
            writer=None,
            continue100=None,
            timer=None,
            request_info=request_info,
            traces=None,
            loop=asyncio.get_event_loop(),
            session=None,
        )
        self._content = None

    async def json(self, *, encoding="utf-8", loads=json.loads, **kwargs):  # NOQA: E999
        stripped = self._body.strip()
        if not stripped:
            return None

        return loads(stripped.decode(encoding))

    async def text(self, encoding="utf-8", errors="strict"):
        return self._body.decode(encoding, errors=errors)

    async def read(self):
        return self._body

    def release(self):
        pass

    @property
    def content(self):
        if not self._content:
            self._content = MockStream()
            self._content.feed_data(self._body)
            self._content.feed_eof()
        return self._content


def build_response(vcr_request, vcr_response, history):
    request_info = RequestInfo(
        url=URL(vcr_request.url),
        method=vcr_request.method,
        headers=CIMultiDictProxy(CIMultiDict(vcr_request.headers)),
        real_url=URL(vcr_request.url),
    )
    response = MockClientResponse(vcr_request.method, URL(vcr_response.get("url")), request_info=request_info)
    response.status = vcr_response["status"]["code"]
    response._body = vcr_response["body"].get("string", b"")
    response.reason = vcr_response["status"]["message"]
    response._headers = CIMultiDictProxy(CIMultiDict(vcr_response["headers"]))
    response._history = tuple(history)

    return response


def _serialize_headers(headers):
    """Serialize CIMultiDictProxy to a pickle-able dict because proxy
        objects forbid pickling:

        https://github.com/aio-libs/multidict/issues/340
    """
    # Mark strings as keys so 'istr' types don't show up in
    # the cassettes as comments.
    return {str(k): v for k, v in headers.items()}


def play_responses(cassette, vcr_request):
    history = []
    vcr_response = cassette.play_response(vcr_request)
    response = build_response(vcr_request, vcr_response, history)

    # If we're following redirects, continue playing until we reach
    # our final destination.
    while 300 <= response.status <= 399:
        new_location = response.headers["location"]
        potential_next_url = URL(new_location)
        next_url = (potential_next_url
            if potential_next_url.is_absolute()
            else URL(response.url).with_path(new_location))

        # Make a stub VCR request that we can then use to look up the recorded
        # VCR request saved to the cassette. This feels a little hacky and
        # may have edge cases based on the headers we're providing (e.g. if
        # there's a matcher that is used to filter by headers).
        vcr_request = Request("GET", str(next_url), None, _serialize_headers(response.request_info.headers))
        vcr_request = cassette.find_requests_with_most_matches(vcr_request)[0][0]

        # Tack on the response we saw from the redirect into the history
        # list that is added on to the final response.
        history.append(response)
        vcr_response = cassette.play_response(vcr_request)
        response = build_response(vcr_request, vcr_response, history)

    return response


async def record_response(cassette, vcr_request, response):
    """Record a VCR request-response chain to the cassette."""

    try:
        data = await response.read()
        body = {"string": (data)}
        response.content = MockStream()
        response.content.feed_data(data)
        response.content.feed_eof()
    # aiohttp raises a ClientConnectionError on reads when
    # there is no body. We can use this to know to not write one.
    except ClientConnectionError:
        body = {}

    vcr_response = {
        "status": {"code": response.status, "message": response.reason},
        "headers": _serialize_headers(response.headers),
        "body": body,  # NOQA: E999
        "url": str(response.url),
    }

    cassette.append(vcr_request, vcr_response)


async def record_responses(cassette, vcr_request, response):
    """Because aiohttp follows redirects by default, we must support
        them by default. This method is used to write individual
        request-response chains that were implicitly followed to get
        to the final destination.
    """

    for past_response in response.history:
        aiohttp_request = past_response.request_info

        # No data because it's following a redirect.
        past_request = Request(
            aiohttp_request.method,
            str(aiohttp_request.url),
            None,
            _serialize_headers(aiohttp_request.headers),
        )
        await record_response(cassette, past_request, past_response)

    # If we're following redirects, then the last request-response
    # we record is the one attached to the `response`.
    if response.history:
        aiohttp_request = response.request_info
        vcr_request = Request(
            aiohttp_request.method,
            str(aiohttp_request.url),
            None,
            _serialize_headers(aiohttp_request.headers),
        )

    await record_response(cassette, vcr_request, response)


def vcr_request(cassette, real_request):
    @functools.wraps(real_request)
    async def new_request(self, method, url, **kwargs):
        headers = kwargs.get("headers")
        auth = kwargs.get("auth")
        headers = self._prepare_headers(headers)
        data = kwargs.get("data", kwargs.get("json"))
        params = kwargs.get("params")

        if auth is not None:
            headers["AUTHORIZATION"] = auth.encode()

        request_url = URL(url)
        if params:
            for k, v in params.items():
                params[k] = str(v)
            request_url = URL(url).with_query(params)

        vcr_request = Request(method, str(request_url), data, headers)

        if cassette.can_play_response_for(vcr_request):
            return play_responses(cassette, vcr_request)

        if cassette.write_protected and cassette.filter_request(vcr_request):
            response = MockClientResponse(method, URL(url))
            response.status = 599
            msg = (
                "No match for the request {!r} was found. Can't overwrite "
                "existing cassette {!r} in your current record mode {!r}."
            )
            msg = msg.format(vcr_request, cassette._path, cassette.record_mode)
            response._body = msg.encode()
            response.close()
            return response

        log.info("%s not in cassette, sending to real server", vcr_request)

        response = await real_request(self, method, url, **kwargs)  # NOQA: E999
        await record_responses(cassette, vcr_request, response)
        return response

    return new_request
