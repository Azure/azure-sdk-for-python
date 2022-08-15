# flake8: noqa
import asyncio

import aiohttp
from aiohttp.test_utils import TestClient


async def aiohttp_request(loop, method, url, output="text", encoding="utf-8", content_type=None, **kwargs):
    session = aiohttp.ClientSession(loop=loop)
    response_ctx = session.request(method, url, **kwargs)

    response = await response_ctx.__aenter__()
    if output == "text":
        content = await response.text()
    elif output == "json":
        content_type = content_type or "application/json"
        content = await response.json(encoding=encoding, content_type=content_type)
    elif output == "raw":
        content = await response.read()
    elif output == "stream":
        content = await response.content.read()

    response_ctx._resp.close()
    await session.close()

    return response, content


def aiohttp_app():
    async def hello(request):
        return aiohttp.web.Response(text="hello")

    async def json(request):
        return aiohttp.web.json_response({})

    async def json_empty_body(request):
        return aiohttp.web.json_response()

    app = aiohttp.web.Application()
    app.router.add_get("/", hello)
    app.router.add_get("/json", json)
    app.router.add_get("/json/empty", json_empty_body)
    return app
