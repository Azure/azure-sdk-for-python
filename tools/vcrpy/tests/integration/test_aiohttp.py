import contextlib
import logging

import pytest

asyncio = pytest.importorskip("asyncio")
aiohttp = pytest.importorskip("aiohttp")

import vcr  # noqa: E402
from .aiohttp_utils import aiohttp_app, aiohttp_request  # noqa: E402


def run_in_loop(fn):
    with contextlib.closing(asyncio.new_event_loop()) as loop:
        asyncio.set_event_loop(loop)
        task = loop.create_task(fn(loop))
        return loop.run_until_complete(task)


def request(method, url, output="text", **kwargs):
    def run(loop):
        return aiohttp_request(loop, method, url, output=output, **kwargs)

    return run_in_loop(run)


def get(url, output="text", **kwargs):
    return request("GET", url, output=output, **kwargs)


def post(url, output="text", **kwargs):
    return request("POST", url, output="text", **kwargs)


@pytest.fixture(params=["https", "http"])
def scheme(request):
    """Fixture that returns both http and https."""
    return request.param


def test_status(tmpdir, scheme):
    url = scheme + "://httpbin.org"
    with vcr.use_cassette(str(tmpdir.join("status.yaml"))):
        response, _ = get(url)

    with vcr.use_cassette(str(tmpdir.join("status.yaml"))) as cassette:
        cassette_response, _ = get(url)
        assert cassette_response.status == response.status
        assert cassette.play_count == 1


@pytest.mark.parametrize("auth", [None, aiohttp.BasicAuth("vcrpy", "test")])
def test_headers(tmpdir, scheme, auth):
    url = scheme + "://httpbin.org"
    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))):
        response, _ = get(url, auth=auth)

    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))) as cassette:
        if auth is not None:
            request = cassette.requests[0]
            assert "AUTHORIZATION" in request.headers
        cassette_response, _ = get(url, auth=auth)
        assert dict(cassette_response.headers) == dict(response.headers)
        assert cassette.play_count == 1
        assert "istr" not in cassette.data[0]
        assert "yarl.URL" not in cassette.data[0]


def test_case_insensitive_headers(tmpdir, scheme):
    url = scheme + "://httpbin.org"
    with vcr.use_cassette(str(tmpdir.join("whatever.yaml"))):
        _, _ = get(url)

    with vcr.use_cassette(str(tmpdir.join("whatever.yaml"))) as cassette:
        cassette_response, _ = get(url)
        assert "Content-Type" in cassette_response.headers
        assert "content-type" in cassette_response.headers
        assert cassette.play_count == 1


def test_text(tmpdir, scheme):
    url = scheme + "://httpbin.org"
    with vcr.use_cassette(str(tmpdir.join("text.yaml"))):
        _, response_text = get(url)

    with vcr.use_cassette(str(tmpdir.join("text.yaml"))) as cassette:
        _, cassette_response_text = get(url)
        assert cassette_response_text == response_text
        assert cassette.play_count == 1


def test_json(tmpdir, scheme):
    url = scheme + "://httpbin.org/get"
    headers = {"Content-Type": "application/json"}

    with vcr.use_cassette(str(tmpdir.join("json.yaml"))):
        _, response_json = get(url, output="json", headers=headers)

    with vcr.use_cassette(str(tmpdir.join("json.yaml"))) as cassette:
        _, cassette_response_json = get(url, output="json", headers=headers)
        assert cassette_response_json == response_json
        assert cassette.play_count == 1


def test_binary(tmpdir, scheme):
    url = scheme + "://httpbin.org/image/png"
    with vcr.use_cassette(str(tmpdir.join("binary.yaml"))):
        _, response_binary = get(url, output="raw")

    with vcr.use_cassette(str(tmpdir.join("binary.yaml"))) as cassette:
        _, cassette_response_binary = get(url, output="raw")
        assert cassette_response_binary == response_binary
        assert cassette.play_count == 1


def test_stream(tmpdir, scheme):
    url = scheme + "://httpbin.org/get"

    with vcr.use_cassette(str(tmpdir.join("stream.yaml"))):
        resp, body = get(url, output="raw")  # Do not use stream here, as the stream is exhausted by vcr

    with vcr.use_cassette(str(tmpdir.join("stream.yaml"))) as cassette:
        cassette_resp, cassette_body = get(url, output="stream")
        assert cassette_body == body
        assert cassette.play_count == 1


@pytest.mark.parametrize("body", ["data", "json"])
def test_post(tmpdir, scheme, body, caplog):
    caplog.set_level(logging.INFO)
    data = {"key1": "value1", "key2": "value2"}
    url = scheme + "://httpbin.org/post"
    with vcr.use_cassette(str(tmpdir.join("post.yaml"))):
        _, response_json = post(url, **{body: data})

    with vcr.use_cassette(str(tmpdir.join("post.yaml"))) as cassette:
        request = cassette.requests[0]
        assert request.body == data
        _, cassette_response_json = post(url, **{body: data})
        assert cassette_response_json == response_json
        assert cassette.play_count == 1

    assert next(
        (
            log
            for log in caplog.records
            if log.getMessage() == "<Request (POST) {}> not in cassette, sending to real server".format(url)
        ),
        None,
    ), "Log message not found."


def test_params(tmpdir, scheme):
    url = scheme + "://httpbin.org/get"
    headers = {"Content-Type": "application/json"}
    params = {"a": 1, "b": False, "c": "c"}

    with vcr.use_cassette(str(tmpdir.join("get.yaml"))) as cassette:
        _, response_json = get(url, output="json", params=params, headers=headers)

    with vcr.use_cassette(str(tmpdir.join("get.yaml"))) as cassette:
        _, cassette_response_json = get(url, output="json", params=params, headers=headers)
        assert cassette_response_json == response_json
        assert cassette.play_count == 1


def test_params_same_url_distinct_params(tmpdir, scheme):
    url = scheme + "://httpbin.org/get"
    headers = {"Content-Type": "application/json"}
    params = {"a": 1, "b": False, "c": "c"}

    with vcr.use_cassette(str(tmpdir.join("get.yaml"))) as cassette:
        _, response_json = get(url, output="json", params=params, headers=headers)

    with vcr.use_cassette(str(tmpdir.join("get.yaml"))) as cassette:
        _, cassette_response_json = get(url, output="json", params=params, headers=headers)
        assert cassette_response_json == response_json
        assert cassette.play_count == 1

    other_params = {"other": "params"}
    with vcr.use_cassette(str(tmpdir.join("get.yaml"))) as cassette:
        response, cassette_response_text = get(url, output="text", params=other_params)
        assert "No match for the request" in cassette_response_text
        assert response.status == 599


def test_params_on_url(tmpdir, scheme):
    url = scheme + "://httpbin.org/get?a=1&b=foo"
    headers = {"Content-Type": "application/json"}

    with vcr.use_cassette(str(tmpdir.join("get.yaml"))) as cassette:
        _, response_json = get(url, output="json", headers=headers)
        request = cassette.requests[0]
        assert request.url == url

    with vcr.use_cassette(str(tmpdir.join("get.yaml"))) as cassette:
        _, cassette_response_json = get(url, output="json", headers=headers)
        request = cassette.requests[0]
        assert request.url == url
        assert cassette_response_json == response_json
        assert cassette.play_count == 1


def test_aiohttp_test_client(aiohttp_client, tmpdir):
    loop = asyncio.get_event_loop()
    app = aiohttp_app()
    url = "/"
    client = loop.run_until_complete(aiohttp_client(app))

    with vcr.use_cassette(str(tmpdir.join("get.yaml"))):
        response = loop.run_until_complete(client.get(url))

    assert response.status == 200
    response_text = loop.run_until_complete(response.text())
    assert response_text == "hello"
    response_text = loop.run_until_complete(response.text(errors="replace"))
    assert response_text == "hello"

    with vcr.use_cassette(str(tmpdir.join("get.yaml"))) as cassette:
        response = loop.run_until_complete(client.get(url))

    request = cassette.requests[0]
    assert request.url == str(client.make_url(url))
    response_text = loop.run_until_complete(response.text())
    assert response_text == "hello"
    assert cassette.play_count == 1


def test_aiohttp_test_client_json(aiohttp_client, tmpdir):
    loop = asyncio.get_event_loop()
    app = aiohttp_app()
    url = "/json/empty"
    client = loop.run_until_complete(aiohttp_client(app))

    with vcr.use_cassette(str(tmpdir.join("get.yaml"))):
        response = loop.run_until_complete(client.get(url))

    assert response.status == 200
    response_json = loop.run_until_complete(response.json())
    assert response_json is None

    with vcr.use_cassette(str(tmpdir.join("get.yaml"))) as cassette:
        response = loop.run_until_complete(client.get(url))

    request = cassette.requests[0]
    assert request.url == str(client.make_url(url))
    response_json = loop.run_until_complete(response.json())
    assert response_json is None
    assert cassette.play_count == 1


def test_redirect(aiohttp_client, tmpdir):
    url = "https://httpbin.org/redirect/2"

    with vcr.use_cassette(str(tmpdir.join("redirect.yaml"))):
        response, _ = get(url)

    with vcr.use_cassette(str(tmpdir.join("redirect.yaml"))) as cassette:
        cassette_response, _ = get(url)

        assert cassette_response.status == response.status
        assert len(cassette_response.history) == len(response.history)
        assert len(cassette) == 3
        assert cassette.play_count == 3

    # Assert that the real response and the cassette response have a similar
    # looking request_info.
    assert cassette_response.request_info.url == response.request_info.url
    assert cassette_response.request_info.method == response.request_info.method
    assert {k: v for k, v in cassette_response.request_info.headers.items()} == {
        k: v for k, v in response.request_info.headers.items()
    }
    assert cassette_response.request_info.real_url == response.request_info.real_url


def test_double_requests(tmpdir):
    """We should capture, record, and replay all requests and response chains,
        even if there are duplicate ones.

        We should replay in the order we saw them.
    """
    url = "https://httpbin.org/get"

    with vcr.use_cassette(str(tmpdir.join("text.yaml"))):
        _, response_text1 = get(url, output="text")
        _, response_text2 = get(url, output="text")

    with vcr.use_cassette(str(tmpdir.join("text.yaml"))) as cassette:
        resp, cassette_response_text = get(url, output="text")
        assert resp.status == 200
        assert cassette_response_text == response_text1

        # We made only one request, so we should only play 1 recording.
        assert cassette.play_count == 1

        # Now make the second test to url
        resp, cassette_response_text = get(url, output="text")

        assert resp.status == 200

        assert cassette_response_text == response_text2

        # Now that we made both requests, we should have played both.
        assert cassette.play_count == 2
