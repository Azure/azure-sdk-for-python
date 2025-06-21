# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing_extensions import TypeAlias


try:
    from promptflow.core._flow import AsyncPrompty
    from promptflow._sdk.entities._flows import FlexFlow
    from promptflow._sdk.entities._flows.dag import Flow
except ImportError:
    from azure.ai.evaluation._legacy.prompty import AsyncPrompty

    class FlexFlow:
        pass

    FlexFlow.__name__ = "FlexFlow"

    class Flow:
        name: str

    Flow.__name__ = "Flow"
