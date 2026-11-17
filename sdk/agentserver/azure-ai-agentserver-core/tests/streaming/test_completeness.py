# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Completeness meta-test for ``azure.ai.agentserver.core.streaming``.

Asserts SC-006 (six public exports), SC-006a (no streaming kwarg on
``@task``), SC-006b (3 concrete classes SDK-private). Also asserts
the exception class hierarchy.

See spec.md  + SC-006 + SC-006a + SC-006b.
"""

from __future__ import annotations

import importlib
import inspect

import pytest


_EXPECTED_PUBLIC_EXPORTS = {
    "streams",
    "EventStream",
    "EventStreamError",
    "EventStreamClosedError",
    "EventStreamNotFoundError",
}

#: EventStreamGoneError removed from public surface.
# Every former-Gone raise site now raises EventStreamNotFoundError.
_RETIRED_EXPORTS = {
    "EventStreamGoneError",
}

_SDK_PRIVATE_CONCRETE_CLASSES = {
    "BroadcastEventStream",
    "ReplayEventStream",
    "FileBackedReplayEventStream",
}


class TestPublicSurface:
    """SC-006 — public ``__all__`` is exactly five entries (
    removed ``EventStreamGoneError``)."""

    def test_all_shape(self) -> None:
        from azure.ai.agentserver.core import streaming

        assert set(streaming.__all__) == _EXPECTED_PUBLIC_EXPORTS, (
            f"streaming.__all__ should be exactly the entries per  + "
            f"SC-006 (dropped EventStreamGoneError); "
            f"got {set(streaming.__all__)}"
        )
        # __all__ should be a list (Python convention)
        assert isinstance(streaming.__all__, list)
        # And every name in __all__ must be a real attribute
        for name in streaming.__all__:
            assert hasattr(streaming, name), f"{name} listed in __all__ but absent"

    def test_retired_exports_absent(self) -> None:
        """— EventStreamGoneError MUST NOT be in __all__."""
        from azure.ai.agentserver.core import streaming

        leaked = _RETIRED_EXPORTS & set(streaming.__all__)
        assert not leaked, f"streaming.__all__ still exports retired symbols (" f"): {sorted(leaked)}"

    def test_retired_exports_unimportable(self) -> None:
        """— ``... import EventStreamGoneError`` raises ImportError."""
        import importlib

        mod = importlib.import_module("azure.ai.agentserver.core.streaming")
        for name in _RETIRED_EXPORTS:
            assert not hasattr(mod, name), (
                f"{name} should not be importable from " f"azure.ai.agentserver.core.streaming "
            )

    def test_streams_singleton_is_async_lifecycle(self) -> None:
        from azure.ai.agentserver.core.streaming import streams

        # Three async lifecycle methods per
        for name in ("get", "get_or_create", "delete"):
            method = getattr(streams, name)
            assert inspect.iscoroutinefunction(method), f"streams.{name} MUST be async per "

    def test_streams_configurators_are_sync(self) -> None:
        from azure.ai.agentserver.core.streaming import streams

        # Three sync configurators per
        for name in (
            "use_in_memory_live",
            "use_in_memory_replay",
            "use_file_backed_replay",
        ):
            method = getattr(streams, name)
            assert not inspect.iscoroutinefunction(method), f"streams.{name} MUST be sync per "


class TestSDKPrivateConcreteClasses:
    """SC-006b — concrete classes are NOT in public ``__all__`` but
    ARE importable from the private ``_concrete`` module."""

    @pytest.mark.parametrize("class_name", sorted(_SDK_PRIVATE_CONCRETE_CLASSES))
    def test_not_importable_from_public_path(self, class_name: str) -> None:
        from azure.ai.agentserver.core import streaming

        # Must not appear in __all__
        assert class_name not in streaming.__all__, f"{class_name} MUST NOT be in public __all__ per SC-006b"
        # Must not be a top-level attribute either (defensive)
        assert not hasattr(streaming, class_name) or class_name == "EventStream", (
            f"{class_name} MUST NOT be a public attribute of " f"azure.ai.agentserver.core.streaming per SC-006b"
        )

    @pytest.mark.parametrize("class_name", sorted(_SDK_PRIVATE_CONCRETE_CLASSES))
    def test_importable_from_private_module(self, class_name: str) -> None:
        from azure.ai.agentserver.core.streaming import _concrete

        cls = getattr(_concrete, class_name, None)
        assert cls is not None, (
            f"{class_name} MUST be importable from "
            f"azure.ai.agentserver.core.streaming._concrete per SC-006b "
            f"(needed for internal SDK tests)"
        )


class TestExceptionHierarchy:
    """— four exception types, common base."""

    def test_base_class_is_exception(self) -> None:
        from azure.ai.agentserver.core.streaming import EventStreamError

        assert issubclass(EventStreamError, Exception)

    def test_all_subclasses_inherit_from_base(self) -> None:
        from azure.ai.agentserver.core.streaming import (
            EventStreamClosedError,
            EventStreamError,
            EventStreamNotFoundError,
        )

        for sub in (
            EventStreamClosedError,
            EventStreamNotFoundError,
        ):
            assert issubclass(sub, EventStreamError), f"{sub.__name__} MUST inherit from EventStreamError per "


class TestOldSurfaceAbsent:
    """Old ``StreamHandler`` surface has been deleted."""

    def test_old_stream_module_is_gone(self) -> None:
        """``_stream.py`` is deleted."""
        with pytest.raises(ImportError):
            importlib.import_module("azure.ai.agentserver.core.tasks._stream")

    @pytest.mark.parametrize("name", ["StreamHandler", "QueueStreamHandler", "StreamHandlerFactory"])
    def test_old_symbols_not_in_resilient_public_surface(self, name: str) -> None:
        from azure.ai.agentserver.core import tasks as resilient

        assert not hasattr(resilient, name), f"{name} MUST be removed from resilient subpackage per "
        assert name not in resilient.__all__


class TestAtSignTaskHasNoStreamingKwarg:
    """SC-006a — ``@task`` decorator + ``TaskContext`` carry no
    streaming-related public attribute."""

    def test_at_sign_task_signature_has_no_streaming_kwarg(self) -> None:
        from azure.ai.agentserver.core.tasks._decorator import task

        sig = inspect.signature(task)
        offenders = [
            p.name for p in sig.parameters.values() if "stream" in p.name.lower() or "factory" in p.name.lower()
        ]
        assert offenders == [], f"@task MUST have NO streaming-related kwarg per SC-006a; " f"got: {offenders}"

    def test_task_context_has_no_stream_method(self) -> None:
        from azure.ai.agentserver.core.tasks import TaskContext

        assert not hasattr(TaskContext, "stream"), "TaskContext MUST NOT have a stream() method per SC-006a"
        # Also no _stream_handler slot
        if hasattr(TaskContext, "__slots__"):
            assert "_stream_handler" not in TaskContext.__slots__

    def test_task_run_is_not_async_iterable(self) -> None:
        """``async for chunk in run`` is removed. Subscribers use
        ``await streams.get(invocation_id).subscribe()`` instead."""
        from azure.ai.agentserver.core.tasks import TaskRun

        assert not hasattr(TaskRun, "__aiter__"), (
            "TaskRun MUST NOT be async-iterable; " "consumers use streams.get(invocation_id).subscribe() instead"
        )
        assert not hasattr(TaskRun, "__anext__")
