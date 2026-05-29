# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Fixture exercising return-type capture in `create_function_report`.

Includes two classes that share a method name (``list``) and a module-level
function that also shares the same name. This pins down the regression where
the previous AST walk would match the first same-named function in the file,
regardless of class scope.

It also covers ``@typing.overload``-decorated stubs to ensure the AST walk
skips them and reads the implementation's return annotation.
"""
import typing


class FooOperations:
    def list(self) -> str:  # noqa: A003
        return ""

    @typing.overload
    def fetch(self, value: int) -> int: ...
    @typing.overload
    def fetch(self, value: str) -> str: ...
    def fetch(self, value) -> "typing.Union[int, str]":
        return value


class BarOperations:
    def list(self) -> bytes:  # noqa: A003
        return b""


def list() -> int:  # noqa: A001
    return 0
