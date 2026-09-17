# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests pinning the core-python engine as an explicit backend object.

Architecture invariant under test: the core-python ("legacy") engine is a
concrete :class:`~azure.cosmos._backend.cosmos_backend.CosmosBackend` /
:class:`~azure.cosmos.aio._backend.cosmos_backend.AsyncCosmosBackend` implementation
(``LegacyBackend`` / ``AsyncLegacyBackend``), not ``None`` and not an
``execute() -> None`` sentinel. No coordinator or public helper branches on
``None``, on backend type, or on ``execute`` returning ``None`` to decide
whether to run the legacy path -- that selection lives entirely behind
``run_operation`` / ``run_page_operation`` polymorphism, exercised directly here.

These tests run in milliseconds: no network, no emulator, no compiled rust
binding required.
"""

from __future__ import annotations
from azure.cosmos._backend.capabilities import OperationRouting

import asyncio
import unittest
from types import SimpleNamespace
from dataclasses import FrozenInstanceError

from azure.cosmos._backend.cosmos_backend import CosmosBackend

from azure.cosmos._backend.constants import BACKEND_NAME_CORE_PYTHON
from azure.cosmos._backend.legacy import LEGACY_BACKEND, LegacyBackend
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._backend.legacy import (
    ASYNC_LEGACY_BACKEND,
    AsyncLegacyBackend,
)


class TestLegacyBackendIsAnExplicitBackend(unittest.TestCase):
    """``LegacyBackend`` is a real ``CosmosBackend``, never a ``None`` stand-in."""

    def test_legacy_backend_is_a_cosmos_backend_subclass(self):
        """Prove the shared Python implementation is a concrete backend."""
        self.assertIsInstance(LEGACY_BACKEND, CosmosBackend)
        self.assertIsInstance(LEGACY_BACKEND, LegacyBackend)

    def test_legacy_backend_name_is_core_python(self):
        """Prove the Python implementation reports its public backend name."""
        self.assertEqual(LEGACY_BACKEND.name, BACKEND_NAME_CORE_PYTHON)

    def test_legacy_backend_execute_is_not_prepared_request_driven(self):
        """``execute`` is the rust wire primitive; the legacy engine does not
        implement it (its work is the original call arguments, not a wire
        request), so calling it raises rather than silently returning ``None``."""
        with self.assertRaises(NotImplementedError):
            LEGACY_BACKEND.execute(None)

    def test_run_operation_always_invokes_the_legacy_operation(self):
        """``LegacyBackend.run_operation`` unconditionally runs
        ``legacy_operation.invoke()`` -- it never calls ``build_request`` or
        ``execute``, and ignores ``rust_eligible`` entirely (there is no ``None``
        or backend-type branch here, only "always legacy")."""
        prepare_request_calls = []
        parse_response_calls = []

        def build_request():
            prepare_request_calls.append(1)
            raise AssertionError("build_request must not run on LegacyBackend")

        def process_response(_response):
            parse_response_calls.append(1)
            raise AssertionError("process_response must not run on LegacyBackend")

        for rust_eligible in (True, False):
            result = LEGACY_BACKEND.run_operation(
                build_request=build_request,
                routing=OperationRouting("read_item", rust_eligible),
                legacy_call=lambda: "legacy-result",
                process_response=process_response,
            )
            self.assertEqual(result, "legacy-result")

        self.assertEqual(prepare_request_calls, [])
        self.assertEqual(parse_response_calls, [])

    def test_run_page_operation_always_invokes_the_legacy_operation(self):
        """Prove paged calls use the supplied Python operation."""
        result = LEGACY_BACKEND.run_page_operation(
            build_request=lambda: self.fail("build_request must not run"),
            routing=OperationRouting("query_items", True),
            legacy_call=lambda: "legacy-page",
            process_response=lambda _response: self.fail(
                "process_response must not run"
            ),
        )
        self.assertEqual(result, "legacy-page")

    def test_operation_routing_is_frozen(self):
        """Operation identity and compatibility cannot change during execution."""
        op = OperationRouting(op="create_item")
        self.assertEqual(op.op, "create_item")
        with self.assertRaises(FrozenInstanceError):
            op.op = "delete_item"  # type: ignore[misc]


class TestBackendCompatibilityFallback(unittest.TestCase):
    """The backend boundary owns temporary parity fallback."""

    def test_backend_execution_errors_never_replay(self):
        """Dispatch failure propagates, even for an operation allowing preflight fallback."""

        class _RejectingBackend(CosmosBackend):
            """Reject a prepared request to exercise explicit fallback."""

            name = "rust"

            def execute(self, prepared, *, deadline=None):
                raise ValueError("unsupported input shape")

        with self.assertRaisesRegex(ValueError, "unsupported input shape"):
            _RejectingBackend().run_operation(
                build_request=lambda: SimpleNamespace(op="is_feed_range_subset"),
                routing=OperationRouting("is_feed_range_subset"),
                legacy_call=lambda: self.fail("Execution must not replay"),
                process_response=lambda _response: "rust",
            )


class TestAsyncLegacyBackendIsAnExplicitBackend(unittest.TestCase):
    """Async twin: ``AsyncLegacyBackend`` is a real ``AsyncCosmosBackend``."""

    def test_async_legacy_backend_is_an_async_cosmos_backend_subclass(self):
        """Prove the shared async Python implementation is a concrete backend."""
        self.assertIsInstance(ASYNC_LEGACY_BACKEND, AsyncCosmosBackend)
        self.assertIsInstance(ASYNC_LEGACY_BACKEND, AsyncLegacyBackend)

    def test_async_legacy_backend_name_is_core_python(self):
        """Prove the async Python implementation reports its public name."""
        self.assertEqual(ASYNC_LEGACY_BACKEND.name, BACKEND_NAME_CORE_PYTHON)

    def test_async_execute_is_not_prepared_request_driven(self):
        """Prove direct prepared-request execution is unsupported."""

        async def _run():
            with self.assertRaises(NotImplementedError):
                await ASYNC_LEGACY_BACKEND.execute(None)

        asyncio.run(_run())

    def test_async_run_operation_always_invokes_the_legacy_operation(self):
        """Prove async calls use the supplied Python operation."""

        async def _run():
            prepare_request_calls = []

            def build_request():
                prepare_request_calls.append(1)
                raise AssertionError("build_request must not run on AsyncLegacyBackend")

            def process_response(_response):
                raise AssertionError(
                    "process_response must not run on AsyncLegacyBackend"
                )

            async def invoke():
                return "async-legacy-result"

            for rust_eligible in (True, False):
                result = await ASYNC_LEGACY_BACKEND.run_operation(
                    build_request=build_request,
                    routing=OperationRouting("read_item", rust_eligible),
                    legacy_call=invoke,
                    process_response=process_response,
                )
                self.assertEqual(result, "async-legacy-result")

            self.assertEqual(prepare_request_calls, [])

        asyncio.run(_run())

    def test_async_run_page_operation_always_invokes_the_legacy_operation(self):
        """Prove async paged calls use the supplied Python operation."""

        async def _run():
            def build_request():
                self.fail("build_request must not run")

            async def invoke():
                return "async-legacy-page"

            result = await ASYNC_LEGACY_BACKEND.run_page_operation(
                build_request=build_request,
                routing=OperationRouting("query_items", True),
                legacy_call=invoke,
                process_response=lambda _response: self.fail(
                    "process_response must not run"
                ),
            )
            self.assertEqual(result, "async-legacy-page")

        asyncio.run(_run())

    def test_async_backend_execution_errors_never_replay(self):
        """An async execution failure cannot switch transports."""

        async def _run():
            class _RejectingBackend(AsyncCosmosBackend):
                """Reject an async prepared request to exercise fallback."""

                name = "rust"

                async def execute(self, prepared, *, deadline=None):
                    raise ValueError("unsupported input shape")

            def build_request():
                return SimpleNamespace(op="is_feed_range_subset")

            async def run_legacy():
                self.fail("Execution must not replay")

            with self.assertRaisesRegex(ValueError, "unsupported input shape"):
                await _RejectingBackend().run_operation(
                    build_request=build_request,
                    routing=OperationRouting("is_feed_range_subset"),
                    legacy_call=run_legacy,
                    process_response=lambda _response: "rust",
                )

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
