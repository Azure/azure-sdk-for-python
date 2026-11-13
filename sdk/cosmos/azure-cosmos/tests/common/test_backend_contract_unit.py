# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared routing and no-replay contracts, using offline backend doubles."""

import asyncio
from dataclasses import FrozenInstanceError
from types import SimpleNamespace
import unittest

from azure.cosmos._backend.capabilities import OperationRouting
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend


class TestBackendContract(unittest.TestCase):
    def test_operation_routing_is_frozen_rust(self):
        """Operation identity and compatibility cannot change during execution."""
        op = OperationRouting(op="create_item")
        self.assertEqual(op.op, "create_item")
        with self.assertRaises(FrozenInstanceError):
            op.op = "delete_item"  # type: ignore[misc]

    def test_backend_execution_errors_never_replay_rust(self):
        """Dispatch failure propagates, even for an operation allowing preflight fallback."""

        class _RejectingBackend(CosmosBackend):
            """Reject a prepared request to check that execution is not replayed."""

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

    def test_async_backend_execution_errors_never_replay_rust(self):
        """An async execution failure cannot switch transports."""

        async def _run():
            class _RejectingBackend(AsyncCosmosBackend):
                """Reject an async prepared request to check that execution is not replayed."""

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
