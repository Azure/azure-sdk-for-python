# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc


class AsyncCredentialBase(abc.ABC):
    @abc.abstractmethod
    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    @abc.abstractmethod
    async def get_token(self, *scopes, **kwargs):
        pass
