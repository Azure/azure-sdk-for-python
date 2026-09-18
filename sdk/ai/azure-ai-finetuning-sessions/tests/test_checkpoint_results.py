from __future__ import annotations

from azure.ai.finetuning_sessions import _patch as sync_patch
from azure.ai.finetuning_sessions.aio import _patch as async_patch
from azure.ai.finetuning_sessions.models import SaveCheckpointOperationResult


_CHECKPOINT_NAME = "checkpoint_name"
_COMPLETED = {
    "status": "completed",
    "result": {"path": "loom://weights/checkpoint_name"},
}


class _FakeResponse:
    def __init__(self, body: dict) -> None:
        self.status_code = 200
        self.headers: dict[str, str] = {}
        self._body = body

    def json(self) -> dict:
        return self._body

    def raise_for_status(self) -> None:
        return None


class _FakeSyncClient:
    def send_request(self, request):
        if request.method == "POST":
            return _FakeResponse({"request_id": "request_1", "session_id": "session_s1"})
        return _FakeResponse(_COMPLETED)


class _FakeAsyncClient:
    async def send_request(self, request, **kwargs):
        if request.method == "POST":
            return _FakeResponse({"request_id": "request_1", "session_id": "session_s1"})
        return _FakeResponse(_COMPLETED)


def _assert_checkpoint_result(result) -> None:
    assert isinstance(result, SaveCheckpointOperationResult)
    assert result.checkpoint_id == _CHECKPOINT_NAME
    assert result.path == "loom://weights/checkpoint_name"


def test_sync_save_weights_completed_result_has_checkpoint_id() -> None:
    session = sync_patch.FineTuningSession.__new__(sync_patch.FineTuningSession)
    session._client = _FakeSyncClient()
    session.session_id = "session_s1"

    result = session.save_weights(_CHECKPOINT_NAME)

    _assert_checkpoint_result(result)


async def test_async_save_weights_completed_result_has_checkpoint_id() -> None:
    result = await async_patch.save_weights(_FakeAsyncClient(), "session_s1", _CHECKPOINT_NAME)

    _assert_checkpoint_result(result)


async def test_async_save_weights_post_completed_result_has_checkpoint_id() -> None:
    pending = await async_patch.save_weights_post(_FakeAsyncClient(), "session_s1", _CHECKPOINT_NAME)

    result = await pending.poll_result()

    _assert_checkpoint_result(result)


async def test_async_save_weights_task_completed_result_has_checkpoint_id() -> None:
    task = await async_patch.save_weights_async(_FakeAsyncClient(), "session_s1", _CHECKPOINT_NAME)

    result = await task

    _assert_checkpoint_result(result)
