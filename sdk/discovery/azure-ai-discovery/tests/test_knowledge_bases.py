# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Knowledge Bases operations.

Covers all 8 methods on BookshelfClient.knowledge_bases (GA surface):
  - list (ItemPaged)
  - get
  - begin_create_or_update (LRO)
  - begin_start_indexing, begin_cancel_indexing (LROs)
  - begin_search (LRO)
  - get_operation_status
  - begin_delete (LRO)

These tests exercise the redesigned ``KnowledgeBasesOperations`` group that
in GA replaces the beta ``KnowledgeBaseVersionsOperations``. Recordings will
be authored in Phase 4b against a live environment.
"""

import pytest
import time
from devtools_testutils import recorded_by_proxy, is_live
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.core.polling.base_polling import LROBasePolling
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


class TestKnowledgeBasesOperations(DiscoveryBookshelfTestCase):
    """Tests for KnowledgeBasesOperations (GA)."""

    @recorded_by_proxy
    def test_begin_create_or_update(self):
        """Test creating/updating a knowledge base via LRO.

        Ordered first in this class so it seeds the read-test fixture
        (``KNOWLEDGE_BASE_NAME``) for subsequent tests, matching the pattern
        used in the beta ``test_knowledge_base_versions.py`` file.
        ``begin_create_or_update`` is upsert/PUT semantics, so re-running the
        suite is idempotent.
        """
        client = self.create_bookshelf_client()
        poller = client.knowledge_bases.begin_create_or_update(
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
        final = poller.result()
        assert final is not None
        assert final.name == KNOWLEDGE_BASE_NAME

    @recorded_by_proxy
    def test_list(self):
        """Test listing knowledge bases via ItemPaged."""
        client = self.create_bookshelf_client()
        knowledge_bases = list(client.knowledge_bases.list())
        assert isinstance(knowledge_bases, list)
        assert len(knowledge_bases) > 0
        for kb in knowledge_bases:
            # Required read-visible fields per spec
            assert kb.name is not None
            assert len(kb.name) <= 24  # @maxLength(24)
            assert kb.bookshelf_name is not None
            assert kb.provisioning_state is not None
            assert kb.status is not None  # IndexingStatus

    @recorded_by_proxy
    def test_get(self):
        """Test getting a specific knowledge base by name."""
        client = self.create_bookshelf_client()
        kb = client.knowledge_bases.get(knowledge_base_name=KNOWLEDGE_BASE_NAME)
        assert kb is not None
        assert kb.name == KNOWLEDGE_BASE_NAME
        assert kb.bookshelf_name is not None
        assert kb.provisioning_state is not None
        assert isinstance(kb.storage_asset_references, list)

    @staticmethod
    def _sleep(seconds):
        """Sleep only when running live; a no-op during playback.

        The indexing/search tests poll long-running operations, so they sleep
        between polls when live. During playback the recorded responses are
        returned instantly, so skipping the sleeps keeps recorded test runs fast.
        """
        if is_live():
            time.sleep(seconds)

    @staticmethod
    def _start_indexing_operation_id(client):
        """Start an indexing run (polling=False) and return its operation id.

        The service permits only one indexing run per KnowledgeBase at a time and
        rejects a concurrent start with ``409 ConcurrencyConflict``. When a run
        is already in progress we reuse it (its id is the KB's
        ``lastIndexingRun``), so the indexing-dependent tests are robust no
        matter how long a run takes on a given deployment.
        """
        try:
            poller = client.knowledge_bases.begin_start_indexing(
                knowledge_base_name=KNOWLEDGE_BASE_NAME,
                polling=False,
            )
        except ResourceExistsError as exc:
            if "ConcurrencyConflict" not in str(exc) and "already in progress" not in str(exc):
                raise
            kb = client.knowledge_bases.get(knowledge_base_name=KNOWLEDGE_BASE_NAME)
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

    @recorded_by_proxy
    def test_begin_start_indexing(self):
        """Test starting indexing as a long-running operation.

        Starts the operation without waiting (polling=False) and verifies a
        poller and a valid ``Operation-Location`` (operation id) are returned.
        This test is self-contained and does not depend on, or leave state for,
        any other test in this class.

        Note: The operation may have already completed (Succeeded) if the KB
        was indexed in a previous test run, since the KB is reused across tests.
        We extract the operation ID regardless of current status.
        """
        client = self.create_bookshelf_client()
        operation_id = self._start_indexing_operation_id(client)
        assert operation_id

    @recorded_by_proxy
    def test_begin_search(self):
        """Test the long-running search operation.

        ``begin_search`` returns ``LROPoller[None]``; the textual search
        results are surfaced via the operation-status endpoint
        (``KnowledgeBaseSearchOperationResponse``). This test only verifies
        the operation can be kicked off and reaches a terminal state.

        Search readiness has two stages, both handled here:
          1. The indexing *operation* must reach ``OperationState.Succeeded``
             (polled via ``get_operation_status``).
          2. After that, the KB needs a short additional window to finish
             processing before ``:search`` is accepted. During that window the
             service rejects ``:search`` with ``KnowledgeBaseNotReady`` ("must
             be in 'Completed' state ... Current state: Processing"). That
             window closes when the typed ``KB.status`` reaches
             ``IndexingStatus.Succeeded``. We therefore gate on
             ``KB.status == Succeeded`` and additionally retry ``begin_search``
             past any lingering ``KnowledgeBaseNotReady``.

        This test is self-contained: it drives its own indexing run to
        ``Succeeded`` and is resilient to a run that the service dedupes into a
        terminal non-success state (e.g. ``Canceled`` left by another test) by
        starting a fresh indexing run and retrying within an overall deadline.
        """
        client = self.create_bookshelf_client()

        terminal = {"succeeded", "failed", "canceled"}
        # Generous deadline to cover a full GraphRAG indexing run
        overall_deadline = time.time() + 2400  # 40 minutes total across retries
        op_status = None
        attempts = 0
        while time.time() < overall_deadline and attempts < 3:
            attempts += 1
            # Start (or reuse) an indexing run and gate on the operation-status endpoint.
            operation_id = self._start_indexing_operation_id(client)
            while time.time() < overall_deadline:
                op = client.knowledge_bases.get_operation_status(
                    knowledge_base_name=KNOWLEDGE_BASE_NAME,
                    operation_id=operation_id,
                )
                # Normalize to the bare enum value (e.g. "Failed"), not the
                # "OperationState.Failed" repr, so terminal detection works.
                op_status = str(getattr(op.status, "value", op.status)).lower()
                if op_status in terminal:
                    break
                self._sleep(10)
            if op_status == "succeeded":
                break
            # Indexing reached a terminal non-success state (e.g. a deduped
            # Canceled/Failed run). Wait briefly, then start a fresh run.
            self._sleep(10)

        if op_status != "succeeded":
            pytest.fail(
                f"Indexing did not reach Succeeded within the deadline "
                f"(last status: {op_status!r}, attempts: {attempts})"
            )

        # After the indexing *operation* reports Succeeded, the KB needs a short
        # additional window to become search-ready: the service reports the KB
        # as 'Processing' and rejects :search with KnowledgeBaseNotReady until it
        # reaches 'Completed'. That readiness corresponds to the typed KB.status
        # reaching IndexingStatus.Succeeded. Gate on it before searching.
        ready_deadline = time.time() + 600
        while time.time() < ready_deadline:
            kb = client.knowledge_bases.get(knowledge_base_name=KNOWLEDGE_BASE_NAME)
            if str(getattr(kb.status, "value", kb.status)).lower() == "succeeded":
                break
            self._sleep(15)

        # Now search the indexed KB, retrying while it is still becoming ready.
        poller = None
        while time.time() < ready_deadline:
            try:
                poller = client.knowledge_bases.begin_search(
                    knowledge_base_name=KNOWLEDGE_BASE_NAME,
                    body=SearchRequest(query="What are common drug interactions?"),
                )
                break
            except HttpResponseError as exc:
                if "KnowledgeBaseNotReady" in str(exc):
                    self._sleep(15)
                    continue
                raise

        assert poller is not None, "KnowledgeBase did not become search-ready within the deadline"
        poller.result(timeout=300)
        assert poller.status() == "Succeeded"

    @recorded_by_proxy
    def test_begin_cancel_indexing(self):
        """Test cancelling an in-flight indexing run.

        Self-contained: starts its own indexing run (polling=False) and then
        cancels it, so it does not depend on, or poison the state for, any other
        test. Ordered after ``test_begin_search`` so the search test is never
        run against a KB left in a ``Canceled`` state by this test.
        """
        client = self.create_bookshelf_client()
        # Start a fresh run to cancel.
        self._start_indexing_operation_id(client)

        cancel_poller = client.knowledge_bases.begin_cancel_indexing(
            knowledge_base_name=KNOWLEDGE_BASE_NAME,
            polling=False,
        )
        # Verify the cancel operation was initiated (got a poller back)
        assert cancel_poller is not None

    @recorded_by_proxy
    def test_get_operation_status(self):
        """Test getting operation status for a knowledge-base LRO.

        Starts an indexing LRO to obtain a real operation ID, then queries
        ``get_operation_status``. Cleans up by cancelling the indexing.
        """
        client = self.create_bookshelf_client()
        operation_id = self._start_indexing_operation_id(client)

        status = client.knowledge_bases.get_operation_status(
            knowledge_base_name=KNOWLEDGE_BASE_NAME,
            operation_id=operation_id,
        )
        assert status is not None
        assert status.id is not None
        assert status.status is not None

        # Cleanup
        client.knowledge_bases.begin_cancel_indexing(
            knowledge_base_name=KNOWLEDGE_BASE_NAME,
            polling=False,
        )

    @recorded_by_proxy
    def test_begin_delete(self):
        """Test deleting a knowledge base via the standard LRO callback.

        Uses a sacrificial KB name so the read-test fixture
        (``KNOWLEDGE_BASE_NAME``) is preserved.

        This test deliberately uses the **standard** long-running-operation poller
        (``LROBasePolling``), which polls the ``Operation-Location`` callback URL the
        service returns -- i.e. the documented LRO contract -- rather than the SDK's
        custom ``_DeleteUntilGonePolling`` fallback. The monitor reports ``Running``
        and then ``Succeeded``, after which the resource itself returns ``404``
        (confirming the delete completed).
        """
        client = self.create_bookshelf_client()
        sacrificial_name = "sdk-test-delete-kb"

        # Create the KB we will delete (delete requires a terminal
        # provisioningState, so wait for create to complete).
        client.knowledge_bases.begin_create_or_update(
            knowledge_base_name=sacrificial_name,
            resource=KnowledgeBase(
                description="Sacrificial KB for delete test",
                copilot_instruction=KNOWLEDGE_BASE_COPILOT_INSTRUCTION,
                storage_asset_references=[
                    StorageAssetReference(
                        id=STORAGE_ASSET_ID,
                        user_assigned_identity=USER_ASSIGNED_IDENTITY,
                    )
                ],
            ),
        ).result()

        # Use the standard Operation-Location poller (NOT the custom
        # _DeleteUntilGonePolling), so the test exercises the real service LRO
        # callback contract.
        poller = client.knowledge_bases.begin_delete(
            knowledge_base_name=sacrificial_name,
            polling=LROBasePolling(0 if not is_live() else 5),
        )
        poller.result()
        assert poller.status() == "Succeeded"

        # The resource must no longer be retrievable.
        with pytest.raises(ResourceNotFoundError):
            client.knowledge_bases.get(knowledge_base_name=sacrificial_name)
