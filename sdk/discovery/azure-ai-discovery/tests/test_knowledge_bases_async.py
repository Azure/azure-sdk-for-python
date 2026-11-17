# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async tests for Knowledge Bases operations.

Mirrors test_knowledge_bases.py against the async ``BookshelfClient`` from
``azure.ai.discovery.aio``.
"""

import asyncio
import time
import pytest
from devtools_testutils import is_live
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.ai.discovery.models import (
    KnowledgeBase,
    SearchRequest,
    StorageAssetReference,
)
from .testcase import DiscoveryBookshelfTestCase
from .constants import (
    KNOWLEDGE_BASE_NAME,
    KNOWLEDGE_BASE_DESCRIPTION,
    KNOWLEDGE_BASE_COPILOT_INSTRUCTION,
    STORAGE_ASSET_ID,
    USER_ASSIGNED_IDENTITY,
)


class TestKnowledgeBasesOperationsAsync(DiscoveryBookshelfTestCase):
    """Async tests for KnowledgeBasesOperations (GA)."""

    @staticmethod
    async def _sleep(seconds):
        """Sleep only when running live; a no-op during playback."""
        if is_live():
            await asyncio.sleep(seconds)

    @staticmethod
    async def _start_indexing_operation_id(client):
        """Start (or reuse) an indexing run and return its operation id.

        ``node_pool_id``/``project_id`` are omitted (optional; the service
        auto-assigns compute). Only one indexing run is permitted per KB at a
        time, so a concurrent start returns ``409 ConcurrencyConflict``; in that
        case the in-progress run is reused (the KB's ``lastIndexingRun``).
        """
        try:
            poller = await client.knowledge_bases.begin_start_indexing(
                knowledge_base_name=KNOWLEDGE_BASE_NAME,
                polling=False,
            )
        except ResourceExistsError as exc:
            if "ConcurrencyConflict" not in str(exc) and "already in progress" not in str(exc):
                raise
            kb = await client.knowledge_bases.get(knowledge_base_name=KNOWLEDGE_BASE_NAME)
            run = getattr(kb, "last_indexing_run", None)
            run_id = getattr(run, "run_id", None)
            assert run_id, "Indexing already in progress but no lastIndexingRun id is available"
            return run_id
        assert poller is not None
        initial_response = poller._polling_method._initial_response
        op_location = initial_response.http_response.headers.get("operation-location", "")
        operation_id = op_location.split("/operations/")[-1].split("?")[0]
        assert operation_id, "Could not extract operation_id from Operation-Location header"
        return operation_id

    @recorded_by_proxy_async
    async def test_begin_create_or_update(self):
        """Seeds the read-test fixture ``KNOWLEDGE_BASE_NAME`` (matches beta pattern).

        Ordered first in this class. ``begin_create_or_update`` is upsert/PUT
        semantics, so re-running the suite is idempotent.
        """
        client = self.create_async_bookshelf_client()
        async with client:
            poller = await client.knowledge_bases.begin_create_or_update(
                knowledge_base_name=KNOWLEDGE_BASE_NAME,
                resource=KnowledgeBase(
                    description=KNOWLEDGE_BASE_DESCRIPTION,
                    copilot_instruction=KNOWLEDGE_BASE_COPILOT_INSTRUCTION,
                    storage_asset_references=[
                        StorageAssetReference(
                            id=STORAGE_ASSET_ID,
                            user_assigned_identity=USER_ASSIGNED_IDENTITY,
                        )
                    ],
                ),
            )
            final = await poller.result()
            assert final is not None
            assert final.name == KNOWLEDGE_BASE_NAME

    @recorded_by_proxy_async
    async def test_list(self):
        """``knowledge_bases.list`` returns ``AsyncItemPaged[KnowledgeBase]``."""
        client = self.create_async_bookshelf_client()
        async with client:
            knowledge_bases = []
            async for kb in client.knowledge_bases.list():
                knowledge_bases.append(kb)
            assert len(knowledge_bases) > 0
            for kb in knowledge_bases:
                assert kb.name is not None
                assert len(kb.name) <= 24
                assert kb.bookshelf_name is not None
                assert kb.provisioning_state is not None
                assert kb.status is not None

    @recorded_by_proxy_async
    async def test_get(self):
        client = self.create_async_bookshelf_client()
        async with client:
            kb = await client.knowledge_bases.get(knowledge_base_name=KNOWLEDGE_BASE_NAME)
            assert kb is not None
            assert kb.name == KNOWLEDGE_BASE_NAME
            assert kb.bookshelf_name is not None
            assert kb.provisioning_state is not None
            assert isinstance(kb.storage_asset_references, list)

    @recorded_by_proxy_async
    async def test_begin_start_indexing(self):
        client = self.create_async_bookshelf_client()
        async with client:
            operation_id = await self._start_indexing_operation_id(client)
            assert operation_id

    @recorded_by_proxy_async
    async def test_begin_search(self):
        client = self.create_async_bookshelf_client()
        async with client:
            terminal = {"succeeded", "failed", "canceled"}
            overall_deadline = time.time() + 2400  # 40 minutes total across retries
            op_status = None
            attempts = 0
            while time.time() < overall_deadline and attempts < 3:
                attempts += 1
                operation_id = await self._start_indexing_operation_id(client)
                while time.time() < overall_deadline:
                    op = await client.knowledge_bases.get_operation_status(
                        knowledge_base_name=KNOWLEDGE_BASE_NAME,
                        operation_id=operation_id,
                    )
                    op_status = str(getattr(op.status, "value", op.status)).lower()
                    if op_status in terminal:
                        break
                    await self._sleep(10)
                if op_status == "succeeded":
                    break
                await self._sleep(10)

            if op_status != "succeeded":
                pytest.fail(
                    f"Indexing did not reach Succeeded within the deadline "
                    f"(last status: {op_status!r}, attempts: {attempts})"
                )

            # Wait for the KB to become search-ready (KB.status -> Succeeded),
            # then retry begin_search past any lingering KnowledgeBaseNotReady.
            ready_deadline = time.time() + 600
            while time.time() < ready_deadline:
                kb = await client.knowledge_bases.get(knowledge_base_name=KNOWLEDGE_BASE_NAME)
                if str(getattr(kb.status, "value", kb.status)).lower() == "succeeded":
                    break
                await self._sleep(15)

            poller = None
            while time.time() < ready_deadline:
                try:
                    poller = await client.knowledge_bases.begin_search(
                        knowledge_base_name=KNOWLEDGE_BASE_NAME,
                        body=SearchRequest(query="What are common drug interactions?"),
                    )
                    break
                except HttpResponseError as exc:
                    if "KnowledgeBaseNotReady" in str(exc):
                        await self._sleep(15)
                        continue
                    raise

            assert poller is not None, "KnowledgeBase did not become search-ready within the deadline"
            await poller.result()
            assert poller.status() == "Succeeded"

    @recorded_by_proxy_async
    async def test_begin_cancel_indexing(self):
        client = self.create_async_bookshelf_client()
        async with client:
            await self._start_indexing_operation_id(client)
            cancel_poller = await client.knowledge_bases.begin_cancel_indexing(
                knowledge_base_name=KNOWLEDGE_BASE_NAME,
                polling=False,
            )
            assert cancel_poller is not None

    @recorded_by_proxy_async
    async def test_get_operation_status(self):
        client = self.create_async_bookshelf_client()
        async with client:
            operation_id = await self._start_indexing_operation_id(client)

            status = await client.knowledge_bases.get_operation_status(
                knowledge_base_name=KNOWLEDGE_BASE_NAME,
                operation_id=operation_id,
            )
            assert status is not None
            assert status.id is not None
            assert status.status is not None

            await client.knowledge_bases.begin_cancel_indexing(
                knowledge_base_name=KNOWLEDGE_BASE_NAME,
                polling=False,
            )

    @recorded_by_proxy_async
    async def test_begin_delete(self):
        """Delete a knowledge base via the standard Operation-Location LRO callback.

        Mirrors the sync test: uses the **standard** ``AsyncLROBasePolling`` poller
        (which polls the ``Operation-Location`` callback URL the service returns),
        rather than the SDK's custom ``_DeleteUntilGonePolling`` fallback. The monitor
        reports ``Running`` and then ``Succeeded``, after which the resource itself
        returns ``404`` (confirming the delete completed).
        """
        client = self.create_async_bookshelf_client()
        async with client:
            sacrificial_name = "sdk-test-delete-kb-async"

            create_poller = await client.knowledge_bases.begin_create_or_update(
                knowledge_base_name=sacrificial_name,
                resource=KnowledgeBase(
                    description="Sacrificial KB for delete test (async)",
                    copilot_instruction=KNOWLEDGE_BASE_COPILOT_INSTRUCTION,
                    storage_asset_references=[
                        StorageAssetReference(
                            id=STORAGE_ASSET_ID,
                            user_assigned_identity=USER_ASSIGNED_IDENTITY,
                        )
                    ],
                ),
            )
            await create_poller.result()

            # Use the standard Operation-Location poller (NOT the custom
            # _AsyncDeleteUntilGonePolling), so the test exercises the real service
            # LRO callback contract.
            poller = await client.knowledge_bases.begin_delete(
                knowledge_base_name=sacrificial_name,
                polling=AsyncLROBasePolling(0 if not is_live() else 5),
            )
            await poller.result()
            assert poller.status() == "Succeeded"

            with pytest.raises(ResourceNotFoundError):
                await client.knowledge_bases.get(knowledge_base_name=sacrificial_name)
