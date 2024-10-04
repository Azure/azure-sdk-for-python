from async_wrapper import async_wrapper
import pytest


class TestAyncWrapper:
    @pytest.mark.asyncio
    async def test_iscoroutine(self):
        async def func():
            return 1

        result = await async_wrapper(func())
        assert result == 1

    @pytest.mark.asyncio
    async def test_isAsyncIterable(self):
        async def func():
            for i in range(3):
                yield i

        result = await async_wrapper(func())
        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_isNestedAsyncIterable(self):
        async def func():
            async def nested():
                for i in range(3):
                    yield i

            return nested()

        result = await async_wrapper(func())
        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_isNestedCoroutine(self):
        async def func():
            async def nested():
                return 2

            return nested()

        result = await async_wrapper(func())
        assert result == 2

    @pytest.mark.asyncio
    async def test_isIterable(self):
        def func():
            for i in range(3):
                yield i

        iterable = func()
        result = await async_wrapper(iterable)
        assert result == iterable

    @pytest.mark.asyncio
    async def test_isSync(self):
        def func():
            return 1

        assert await async_wrapper(func()) == 1
