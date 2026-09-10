# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from collections.abc import Callable
from typing import Concatenate, ParamSpec, TypeAlias

from starlette.types import ASGIApp

P = ParamSpec("P")
MiddlewareFactory: TypeAlias = Callable[Concatenate[ASGIApp, P], ASGIApp]
StreamContent: TypeAlias = str | bytes | memoryview
