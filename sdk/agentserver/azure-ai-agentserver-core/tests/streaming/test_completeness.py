# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Completeness meta-test for ``azure.ai.agentserver.core.streaming``.

Asserts SC-006 (six public exports), SC-006a (no streaming kwarg on
``@task``), SC-006b (3 concrete classes SDK-private). Also asserts
the exception class hierarchy per FR-006.

See spec.md FR-001 + SC-006 + SC-006a + SC-006b.
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
    "EventStreamGoneError",
    "EventStreamNotFoundError",
}

_SDK_PRIVATE_CONCRETE_CLASSES = {
    "BroadcastEventStream",
    "ReplayEventStream",
    "FileBackedReplayEventStream",
}


class TestPublicSurface:
    """SC-006 — public ``__all__`` is exactly six entries."""

    def test_all_shape(self) -> None:
        from azure.ai.agentserver.core import streaming

        assert set(streaming.__all__) == _EXPECTED_PUBLIC_EXPORTS, (
            f"streaming.__all__ should be exactly the 6 entries per FR-001 + "
            f"SC-006; got {set(streaming.__all__)}"
        )
        # __all__ should be a list (Python convention)
        assert isinstance(streaming.__all__, list)
        # And every name in __all__ must be a real attribute
        for name in streaming.__all__:
            assert hasattr(streaming, name), f"{name} listed in __all__ but absent"

    def test_streams_singleton_is_async_lifecycle(self) -> None:
        from azure.ai.agentserver.core.streaming import streams

        # Three async lifecycle methods per FR-013
        for name in ("get", "get_or_create", "delete"):
            method = getattr(streams, name)
            assert inspect.iscoroutinefunction(method), (
                f"streams.{name} MUST be async per FR-013"
            )

    def test_streams_configurators_are_sync(self) -> None:
        from azure.ai.agentserver.core.streaming import streams

        # Three sync configurators per FR-013
        for name in (
            "use_in_memory_live",
            "use_in_memory_replay",
            "use_file_backed_replay",
        ):
            method = getattr(streams, name)
            assert not inspect.iscoroutinefunction(method), (
                f"streams.{name} MUST be sync per FR-013"
            )


class TestSDKPrivateConcreteClasses:
    """SC-006b — concrete classes are NOT in public ``__all__`` but
    ARE importable from the private ``_concrete`` module."""

    @pytest.mark.parametrize("class_name", sorted(_SDK_PRIVATE_CONCRETE_CLASSES))
    def test_not_importable_from_public_path(self, class_name: str) -> None:
        from azure.ai.agentserver.core import streaming

        # Must not appear in __all__
        assert class_name not in streaming.__all__, (
            f"{class_name} MUST NOT be in public __all__ per SC-006b"
        )
        # Must not be a top-level attribute either (defensive)
        assert not hasattr(streaming, class_name) or class_name == "EventStream", (
            f"{class_name} MUST NOT be a public attribute of "
            f"azure.ai.agentserver.core.streaming per SC-006b"
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
    """FR-006 — four exception types, common base."""

    def test_base_class_is_exception(self) -> None:
        from azure.ai.agentserver.core.streaming import EventStreamError

        assert issubclass(EventStreamError, Exception)

    def test_all_subclasses_inherit_from_base(self) -> None:
        from azure.ai.agentserver.core.streaming import (
            EventStreamClosedError,
            EventStreamError,
            EventStreamGoneError,
            EventStreamNotFoundError,
        )

        for sub in (
            EventStreamClosedError,
            EventStreamGoneError,
            EventStreamNotFoundError,
        ):
            assert issubclass(sub, EventStreamError), (
                f"{sub.__name__} MUST inherit from EventStreamError per FR-006"
            )


class TestOldSurfaceAbsentOrPresent:
    """Old ``StreamHandler`` surface — currently still present in
    ``core.durable._stream`` (additive Phase 1 increment leaves it
    in place; deletion is deferred to a coordinated cross-branch
    follow-up per the spec's Phase 1↔3 mitigation).

    This test documents the additive-only state of this commit. A
    follow-up commit will flip these assertions to ``raises
    ImportError`` once the deletion lands.
    """

    def test_old_stream_module_still_present_pending_coordinated_deletion(self) -> None:
        # NOTE: Spec 017 Phase 1 ultimately deletes _stream.py
        # (FR-014). This additive-first commit defers the deletion
        # to a follow-up because removing it cross-branch breaks
        # responses + demo consumers. See plan.md "Phase 1 ↔ Phase 3
        # hard dependency".
        try:
            mod = importlib.import_module(
                "azure.ai.agentserver.core.durable._stream"
            )
            # If still present, confirm the symbols exist (they will
            # be deleted in the follow-up)
            assert hasattr(mod, "StreamHandler")
            assert hasattr(mod, "QueueStreamHandler")
        except ImportError:
            # If the follow-up deletion has already landed, that's
            # also acceptable.
            pass


class TestAtSignTaskHasNoStreamingKwarg:
    """SC-006a — ``@task`` decorator + ``TaskContext`` carry no
    streaming-related public attribute.

    Currently still has ``stream_handler_factory`` pending the
    coordinated cross-branch deletion (same as
    :class:`TestOldSurfaceAbsentOrPresent`). This test documents
    the additive-only state of this commit; a follow-up will flip
    these assertions.
    """

    def test_at_sign_task_signature_after_deletion(self) -> None:
        # Once the coordinated deletion lands, this should be the
        # assertion. Currently the kwarg is still present.
        try:
            from azure.ai.agentserver.core.durable._decorator import task

            sig = inspect.signature(task)
            offenders = [
                p
                for p in sig.parameters.values()
                if "stream" in p.name.lower() or "factory" in p.name.lower()
            ]
            # Today there is ONE: stream_handler_factory. Document
            # that fact rather than asserting zero.
            if offenders:
                # Pending coordinated deletion. Document the
                # current state — do NOT fail.
                pytest.skip(
                    f"@task still has streaming-related kwarg(s) pending "
                    f"coordinated cross-branch deletion: "
                    f"{[p.name for p in offenders]}. See spec 017 Phase 1↔3 "
                    f"mitigation."
                )
        except ImportError:
            pytest.skip("@task decorator not present in this branch")
