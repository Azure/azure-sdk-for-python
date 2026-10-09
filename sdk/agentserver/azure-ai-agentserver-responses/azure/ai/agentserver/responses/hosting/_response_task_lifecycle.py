# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Caller-scoped ownership and durable deletion fences for response task inputs."""

from __future__ import annotations

from azure.ai.agentserver.core.tasks import TaskManagerNotInitialized
from azure.ai.agentserver.core.tasks._attachments import _read_input_value
from azure.ai.agentserver.core.tasks._exceptions import TaskNotFound
from azure.ai.agentserver.core.tasks._exceptions_internal import _HostedConflict
from azure.ai.agentserver.core.tasks._manager import get_task_manager
from azure.ai.agentserver.core.tasks._models import TaskInfo, TaskPatchRequest

from ._resilient_input import platform_context_from_params
from ._task_id import derive_lifecycle_id


_DELETED_INPUT_IDS = "responses_deleted_input_ids"


def _deleted_input_ids(info: TaskInfo) -> list[str]:
    value = (info.payload or {}).get(_DELETED_INPUT_IDS, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("Invalid durable response deletion fence")
    return value


def _owns_response(info: TaskInfo, response_id: str, user_id_key: str | None) -> bool:
    lifecycle_id = derive_lifecycle_id(response_id, user_id_key)
    if info.status == "completed" or lifecycle_id in _deleted_input_ids(info):
        return False
    payload = info.payload or {}
    if payload.get("last_input_id") == lifecycle_id:
        return True
    slots = [payload.get("input")]
    slots.extend((payload.get("steering") or {}).get("pending_inputs") or [])
    for slot in slots:
        if slot is None:
            continue
        value = _read_input_value(slot, info.attachments)
        if not isinstance(value, dict):
            raise ValueError("Invalid durable response task input")
        if value.get("response_id") == response_id and platform_context_from_params(value).user_id_key == user_id_key:
            return True
    return False


async def _response_tasks(response_id: str, user_id_key: str | None, task_names: tuple[str, ...]) -> list[TaskInfo]:
    """Find current or queued ownership without starting or reclaiming tasks.

    :param response_id: The public response identifier.
    :type response_id: str
    :param user_id_key: The authenticated user partition.
    :type user_id_key: str | None
    :param task_names: The response primitives registered by this host.
    :type task_names: tuple[str, ...]
    :return: Durable tasks owning the caller-scoped response.
    :rtype: list[TaskInfo]
    """
    manager = get_task_manager()
    matches = []
    for name in task_names:
        for info in await manager.list_tasks(fn_name=name):
            if _owns_response(info, response_id, user_id_key):
                matches.append(info)
    return matches


async def _fence_response_tasks(
    response_id: str, user_id_key: str | None, task_names: tuple[str, ...], *, durable_required: bool = True
) -> None:
    """Fence only this response input, retaining other turns and queued work.

    :param response_id: The authorized response being deleted.
    :type response_id: str
    :param user_id_key: The caller's user partition.
    :type user_id_key: str | None
    :param task_names: The host's registered response primitives.
    :type task_names: tuple[str, ...]
    :keyword durable_required: Fail closed when durable admission is enabled but no manager is available.
    :paramtype durable_required: bool
    :rtype: None
    """
    try:
        matches = await _response_tasks(response_id, user_id_key, task_names)
    except TaskManagerNotInitialized:
        if durable_required:
            raise
        return
    if not matches:
        return
    manager = get_task_manager()
    lifecycle_id = derive_lifecycle_id(response_id, user_id_key)
    for info in matches:
        for attempt in range(5):
            if info.status == "completed":
                break  # Immutable terminal tasks cannot recover.
            deleted = _deleted_input_ids(info)
            if lifecycle_id in deleted:
                break
            try:
                await manager.provider.update(
                    info.id,
                    TaskPatchRequest(if_match=info.etag, payload={_DELETED_INPUT_IDS: [*deleted, lifecycle_id]}),
                )
                break
            except TaskNotFound:
                break
            except _HostedConflict as exc:
                code = exc._code  # pylint: disable=protected-access
                if code not in {"etag_mismatch", "task_immutable"} or attempt == 4:
                    raise
                try:
                    latest = await manager.provider.get(info.id)
                except TaskNotFound:
                    break
                if latest is None:
                    break
                info = latest


async def _task_input_deleted(task_id: str, response_id: str, user_id_key: str | None) -> bool:
    """Check durable fencing before any response recovery writes or admission.

    :param task_id: The durable task identifier.
    :type task_id: str
    :param response_id: The input's public response identifier.
    :type response_id: str
    :param user_id_key: The input's persisted user partition.
    :type user_id_key: str | None
    :return: Whether the task is gone, terminal, or this input has been deleted.
    :rtype: bool
    """
    try:
        manager = get_task_manager()
    except TaskManagerNotInitialized:
        return False
    try:
        info = await manager.provider.get(task_id)
    except TaskNotFound:
        return True
    return (
        info is None
        or info.status == "completed"
        or derive_lifecycle_id(response_id, user_id_key) in _deleted_input_ids(info)
    )
