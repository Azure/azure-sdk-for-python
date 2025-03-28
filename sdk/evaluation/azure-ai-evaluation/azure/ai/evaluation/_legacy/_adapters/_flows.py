# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing_extensions import TypeAlias


try:
    from promptflow._sdk.entities._flows import AsyncPrompty as _AsyncPrompty
    from promptflow._sdk.entities._flows import FlexFlow as _FlexFlow
    from promptflow._sdk.entities._flows.dag import Flow as _Flow
except ImportError:
    from azure.ai.evaluation._legacy.prompty import AsyncPrompty as _AsyncPrompty

    class _FlexFlow:
        pass

    _FlexFlow.__name__ = "FlexFlow"

    class _Flow:
        name: str

    _Flow.__name__ = "Flow"


AsyncPrompty: TypeAlias = _AsyncPrompty
FlexFlow: TypeAlias = _FlexFlow
Flow: TypeAlias = _Flow
