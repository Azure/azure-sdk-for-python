from async_wrapper import wrap_list_result, wrap_result
import pytest


class TestAyncWrapper:
    @pytest.mark.asyncio
    async def test_iscoroutine(self):
        async def func():
            return 1

        result = await wrap_result(func())
        assert result == 1

    @pytest.mark.asyncio
    async def test_isAsyncIterable(self):
        async def func():
            for i in range(3):
                yield i

        result = await wrap_list_result(func())
        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_isNestedCoroutine(self):
        async def func():
            async def nested():
                return 2

            return nested()

        result = await wrap_result(func())
        assert result == 2

    @pytest.mark.asyncio
    async def test_isIterable(self):
        def func():
            for i in range(3):
                yield i

        iterable = func()
        result = await wrap_list_result(iterable)
        assert result == iterable

    @pytest.mark.asyncio
    async def test_isSync(self):
        def func():
            return 1

        assert await wrap_result(func()) == 1
