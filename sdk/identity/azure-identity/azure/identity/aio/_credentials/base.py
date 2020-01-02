# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc


class AsyncCredentialBase(abc.ABC):
    @abc.abstractmethod
    async def close(self):
        pass

    @abc.abstractmethod
    async def __aenter__(self):
        pass

    async def __aexit__(self, *args):
        await self.close()

    @abc.abstractmethod
    async def get_token(self, *scopes, **kwargs):
        pass
