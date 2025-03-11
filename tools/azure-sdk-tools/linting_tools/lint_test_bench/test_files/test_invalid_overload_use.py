# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import overload, Union

# This code violates invalid-use-of-overload

class TestingOverload:
    @overload
    def double(self, a: str):
        ...

    @overload
    def double(self, a: int):
        ...

    async def double(self, a: Union[str, int]):
        if isinstance(a, str):
            return len(a)*2
        return a * 2


    @overload
    async def doubleAgain(self, a: str) -> int:
        ...

    @overload
    def doubleAgain(self, a: int) -> int:
        ...

    async def doubleAgain(self, a: Union[str, int]) -> int:
        if isinstance(a, str):
            return len(a)*2
        return a * 2
