# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Base test classes for azure-ai-discovery recorded tests.

Provides AzureRecordedTestCase subclasses for recorded/playback testing
and helper methods for client creation.
"""
from devtools_testutils import AzureRecordedTestCase
from .constants import (
    WORKSPACE_ENDPOINT,
    PROJECT_NAME,
    INVESTIGATION_NAME,
    BOOKSHELF_ENDPOINT,
    DISCOVERY_SCOPE,
)


class DiscoveryWorkspaceTestCase(AzureRecordedTestCase):
    """Base class for Discovery Workspace data plane SDK tests.

    Inherits from AzureRecordedTestCase which provides:
    - Recorded test infrastructure (record/playback)
    - Automatic credential handling
    - Test proxy integration
    """

    def setup_method(self, method):
        """Set up test resources before each test method."""
        self.project_name = PROJECT_NAME
        self.investigation_name = INVESTIGATION_NAME
        self.workspace_endpoint = WORKSPACE_ENDPOINT

    def create_workspace_client(self, endpoint=None, **kwargs):
        """Create a WorkspaceClient for testing."""
        from azure.ai.discovery import WorkspaceClient

        return WorkspaceClient(
            endpoint=endpoint or self.workspace_endpoint,
            credential=self.get_credential(WorkspaceClient),
            credential_scopes=[DISCOVERY_SCOPE],
            **kwargs,
        )


class DiscoveryBookshelfTestCase(AzureRecordedTestCase):
    """Base class for Discovery Bookshelf data plane SDK tests.

    Inherits from AzureRecordedTestCase which provides:
    - Recorded test infrastructure (record/playback)
    - Automatic credential handling
    - Test proxy integration
    """

    def setup_method(self, method):
        """Set up test resources before each test method."""
        self.bookshelf_endpoint = BOOKSHELF_ENDPOINT

    def create_bookshelf_client(self, **kwargs):
        """Create a BookshelfClient for testing."""
        from azure.ai.discovery import BookshelfClient

        return BookshelfClient(
            endpoint=self.bookshelf_endpoint,
            credential=self.get_credential(BookshelfClient),
            credential_scopes=[DISCOVERY_SCOPE],
            **kwargs,
        )
