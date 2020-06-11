async def handle_coroutine(vcr, fn):  # noqa: E999
    with vcr as cassette:
        return await fn(cassette)  # noqa: E999
