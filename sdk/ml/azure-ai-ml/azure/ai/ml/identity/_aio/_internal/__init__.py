# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import abc
from typing import Any


class AsyncContextManager(abc.ABC):
    @abc.abstractmethod
    async def close(self) -> None:
        pass

    async def __aenter__(self) -> "AsyncContextManager":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()


__all__ = ["AsyncContextManager"]
