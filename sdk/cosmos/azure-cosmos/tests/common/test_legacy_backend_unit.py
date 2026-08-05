# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests pinning the core-python engine as an explicit backend object.

Architecture invariant under test: the core-python ("legacy") engine is a
concrete :class:`~azure.cosmos._backend.base.CosmosBackend` /
:class:`~azure.cosmos.aio._backend.base.AsyncCosmosBackend` implementation
(``LegacyBackend`` / ``AsyncLegacyBackend``), not ``None`` and not an
``execute() -> None`` sentinel. No coordinator or public helper branches on
``None``, on backend type, or on ``execute`` returning ``None`` to decide
whether to run the legacy path -- that selection lives entirely behind
``run_operation`` / ``run_page_operation`` polymorphism, exercised directly here.

These tests run in milliseconds: no network, no emulator, no compiled rust
binding required.
"""
from __future__ import annotations

import asyncio
import unittest
from dataclasses import FrozenInstanceError

from azure.cosmos._backend.base import CosmosBackend, LegacyOperation
from azure.cosmos._backend.constants import BACKEND_NAME_CORE_PYTHON
from azure.cosmos._backend.legacy import LEGACY_BACKEND, LegacyBackend, coerce_backend
from azure.cosmos.aio._backend.base import AsyncCosmosBackend
from azure.cosmos.aio._backend.legacy import (
    ASYNC_LEGACY_BACKEND,
    AsyncLegacyBackend,
    coerce_async_backend,
)


class TestLegacyBackendIsAnExplicitBackend(unittest.TestCase):
    """``LegacyBackend`` is a real ``CosmosBackend``, never a ``None`` stand-in."""

    def test_legacy_backend_is_a_cosmos_backend_subclass(self):
        self.assertIsInstance(LEGACY_BACKEND, CosmosBackend)
        self.assertIsInstance(LEGACY_BACKEND, LegacyBackend)

    def test_legacy_backend_name_is_core_python(self):
        self.assertEqual(LEGACY_BACKEND.name, BACKEND_NAME_CORE_PYTHON)

    def test_legacy_backend_execute_is_not_prepared_request_driven(self):
        """``execute`` is the rust wire primitive; the legacy engine does not
        implement it (its work is the original call arguments, not a wire
        request), so calling it raises rather than silently returning ``None``."""
        with self.assertRaises(NotImplementedError):
            LEGACY_BACKEND.execute(None)

    def test_run_operation_always_invokes_the_legacy_operation(self):
        """``LegacyBackend.run_operation`` unconditionally runs
        ``legacy_operation.invoke()`` -- it never calls ``build_prepared`` or
        ``execute``, and ignores ``rust_eligible`` entirely (there is no ``None``
        or backend-type branch here, only "always legacy")."""
        build_prepared_calls = []
        parse_response_calls = []

        def build_prepared():
            build_prepared_calls.append(1)
            raise AssertionError("build_prepared must not run on LegacyBackend")

        def parse_response(_response):
            parse_response_calls.append(1)
            raise AssertionError("parse_response must not run on LegacyBackend")

        for rust_eligible in (True, False):
            result = LEGACY_BACKEND.run_operation(
                build_prepared=build_prepared,
                legacy_operation=LegacyOperation(op="read_item", invoke=lambda: "legacy-result"),
                parse_response=parse_response,
                rust_eligible=rust_eligible,
            )
            self.assertEqual(result, "legacy-result")

        self.assertEqual(build_prepared_calls, [])
        self.assertEqual(parse_response_calls, [])

    def test_run_page_operation_always_invokes_the_legacy_operation(self):
        result = LEGACY_BACKEND.run_page_operation(
            build_prepared=lambda: self.fail("build_prepared must not run"),
            legacy_operation=LegacyOperation(
                op="query_items", invoke=lambda: "legacy-page"
            ),
            parse_response=lambda _response: self.fail("parse_response must not run"),
            rust_eligible=True,
        )
        self.assertEqual(result, "legacy-page")

    def test_legacy_operation_is_a_typed_frozen_port_not_a_bare_callable(self):
        """``LegacyOperation`` carries a named ``op`` alongside ``invoke``, and is
        frozen like the other prepared/request dataclasses."""
        op = LegacyOperation(op="create_item", invoke=lambda: None)
        self.assertEqual(op.op, "create_item")
        with self.assertRaises(FrozenInstanceError):
            op.op = "delete_item"  # type: ignore[misc]


class TestCoerceBackendNeverReturnsNone(unittest.TestCase):
    """``coerce_backend`` is the single place a coordinator maps the client's
    ``Optional[CosmosBackend]`` selection to an explicit, never-``None`` backend."""

    def test_none_selection_coerces_to_the_shared_legacy_backend(self):
        self.assertIs(coerce_backend(None), LEGACY_BACKEND)

    def test_a_real_backend_passes_through_unchanged(self):
        class _FakeRustBackend(CosmosBackend):
            name = "rust"

            def execute(self, prepared):
                return None

        backend = _FakeRustBackend()
        self.assertIs(coerce_backend(backend), backend)

    def test_coercion_result_is_never_none(self):
        for selection in (None, LEGACY_BACKEND):
            self.assertIsNotNone(coerce_backend(selection))

    def test_backend_boundary_owns_explicit_compatibility_fallback(self):
        class _RejectingBackend(CosmosBackend):
            name = "rust"

            def execute(self, prepared):
                raise ValueError("unsupported input shape")

        result = _RejectingBackend().run_operation(
            build_prepared=lambda: object(),
            legacy_operation=LegacyOperation(op="is_feed_range_subset", invoke=lambda: "legacy"),
            parse_response=lambda _response: "rust",
            fallback_exceptions=(ValueError,),
        )

        self.assertEqual(result, "legacy")


class TestAsyncLegacyBackendIsAnExplicitBackend(unittest.TestCase):
    """Async twin: ``AsyncLegacyBackend`` is a real ``AsyncCosmosBackend``."""

    def test_async_legacy_backend_is_an_async_cosmos_backend_subclass(self):
        self.assertIsInstance(ASYNC_LEGACY_BACKEND, AsyncCosmosBackend)
        self.assertIsInstance(ASYNC_LEGACY_BACKEND, AsyncLegacyBackend)

    def test_async_legacy_backend_name_is_core_python(self):
        self.assertEqual(ASYNC_LEGACY_BACKEND.name, BACKEND_NAME_CORE_PYTHON)

    def test_async_execute_is_not_prepared_request_driven(self):
        async def _run():
            with self.assertRaises(NotImplementedError):
                await ASYNC_LEGACY_BACKEND.execute(None)

        asyncio.run(_run())

    def test_async_run_operation_always_invokes_the_legacy_operation(self):
        async def _run():
            build_prepared_calls = []

            async def build_prepared():
                build_prepared_calls.append(1)
                raise AssertionError("build_prepared must not run on AsyncLegacyBackend")

            def parse_response(_response):
                raise AssertionError("parse_response must not run on AsyncLegacyBackend")

            async def invoke():
                return "async-legacy-result"

            for rust_eligible in (True, False):
                result = await ASYNC_LEGACY_BACKEND.run_operation(
                    build_prepared=build_prepared,
                    legacy_operation=LegacyOperation(op="read_item", invoke=invoke),
                    parse_response=parse_response,
                    rust_eligible=rust_eligible,
                )
                self.assertEqual(result, "async-legacy-result")

            self.assertEqual(build_prepared_calls, [])

        asyncio.run(_run())

    def test_async_run_page_operation_always_invokes_the_legacy_operation(self):
        async def _run():
            async def build_prepared():
                self.fail("build_prepared must not run")

            async def invoke():
                return "async-legacy-page"

            result = await ASYNC_LEGACY_BACKEND.run_page_operation(
                build_prepared=build_prepared,
                legacy_operation=LegacyOperation(op="query_items", invoke=invoke),
                parse_response=lambda _response: self.fail("parse_response must not run"),
                rust_eligible=True,
            )
            self.assertEqual(result, "async-legacy-page")

        asyncio.run(_run())

    def test_none_selection_coerces_to_the_shared_async_legacy_backend(self):
        self.assertIs(coerce_async_backend(None), ASYNC_LEGACY_BACKEND)

    def test_a_real_async_backend_passes_through_unchanged(self):
        class _FakeAsyncRustBackend(AsyncCosmosBackend):
            name = "rust"

            async def execute(self, prepared):
                return None

        backend = _FakeAsyncRustBackend()
        self.assertIs(coerce_async_backend(backend), backend)

    def test_async_backend_boundary_owns_explicit_compatibility_fallback(self):
        async def _run():
            class _RejectingBackend(AsyncCosmosBackend):
                name = "rust"

                async def execute(self, prepared):
                    raise ValueError("unsupported input shape")

            async def build_prepared():
                return object()

            async def run_legacy():
                return "legacy"

            result = await _RejectingBackend().run_operation(
                build_prepared=build_prepared,
                legacy_operation=LegacyOperation(
                    op="is_feed_range_subset", invoke=run_legacy
                ),
                parse_response=lambda _response: "rust",
                fallback_exceptions=(ValueError,),
            )
            self.assertEqual(result, "legacy")

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
