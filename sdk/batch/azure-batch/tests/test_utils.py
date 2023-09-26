

from utils import async_wrapper
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
    async def test_isIterable(self):
        def func():
            for i in range(3):
                yield i
        result = await async_wrapper(func())
        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_isSync(self):
        def func():
            return 1
        result = await async_wrapper(func())
        assert 1 == await async_wrapper(1)
