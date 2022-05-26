# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import abc


class AsyncContextManager(abc.ABC):
    @abc.abstractmethod
    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


__all__ = ["AsyncContextManager"]
