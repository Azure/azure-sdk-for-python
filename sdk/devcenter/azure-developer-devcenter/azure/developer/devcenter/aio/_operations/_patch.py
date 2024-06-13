# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from ._operations import DevCenterClientOperationsMixin as DevCenterClientOperationsMixinGenerated
from azure.core.polling import AsyncLROPoller
from azure.core.tracing.decorator_async import distributed_trace_async
from typing import Any, List, Optional

class DevCenterClientOperationsMixin(DevCenterClientOperationsMixinGenerated):

    @distributed_trace_async
    async def begin_delete_dev_box(
        self, project_name: str, user_id: str, dev_box_name: str, **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return super().begin_delete_dev_box(project_name, user_id, dev_box_name, **kwargs)

    @distributed_trace_async
    async def begin_start_dev_box(
        self, project_name: str, user_id: str, dev_box_name: str, **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return super().begin_start_dev_box(project_name, user_id, dev_box_name, **kwargs)

    @distributed_trace_async
    async def begin_stop_dev_box(
        self, project_name: str, user_id: str, dev_box_name: str, *, hibernate: Optional[bool] = None, **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return super().begin_stop_dev_box(project_name, user_id, dev_box_name, hibernate, **kwargs)

    @distributed_trace_async
    async def begin_restart_dev_box(
        self, project_name: str, user_id: str, dev_box_name: str, **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return super().begin_restart_dev_box(project_name, user_id, dev_box_name, **kwargs)

    @distributed_trace_async
    async def begin_delete_environment(
        self, project_name: str, user_id: str, environment_name: str, **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return super().begin_delete_environment(project_name, user_id, environment_name, **kwargs)

__all__: List[str] = ["DevCenterClientOperationsMixin"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
