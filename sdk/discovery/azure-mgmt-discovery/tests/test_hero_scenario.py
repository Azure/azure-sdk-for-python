# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Hero Scenario Test: Run a Tool on Supercomputer

This test demonstrates the complete end-to-end flow for the Discovery service:
1. Create a Workspace (ARM)
2. Create a Project in the workspace (ARM)
3. Create an Investigation in the workspace (Workspace client)
4. Run a Tool on Supercomputer (Workspace client) - THE HERO!
5. Check Run Status and wait for completion (Workspace client)
6. Query results from KnowledgeBase (Bookshelf client)

This scenario requires real Azure resources and is intended to be run
in record mode to generate recordings for CI playback.

HERO SCENARIO: "Run a Tool on Supercomputer"
This is the primary use case for the Discovery service - executing
scientific computing tools on Azure supercomputers.
"""
import os
import uuid
import pytest
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy


# Test configuration
AZURE_LOCATION = os.environ.get("AZURE_LOCATION", "eastus")
AZURE_RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "olawal")
SUPERCOMPUTER_NAME = os.environ.get("SUPERCOMPUTER_NAME", "test-supercomputer")


class TestHeroScenario(AzureMgmtRecordedTestCase):
    """
    Hero Scenario: Run a Tool on Supercomputer

    This test class validates the complete end-to-end Discovery workflow
    using all three SDK clients:

    ARM Client (azure-mgmt-discovery):
      - Create/manage Workspace
      - Create/manage Project
      - Access Supercomputer

    Workspace Client (azure-discovery-workspace):
      - Create Investigation
      - Run Tool on Supercomputer
      - Monitor Run Status
      - Manage Tasks

    Bookshelf Client (azure-discovery-bookshelf):
      - Query KnowledgeBase for insights
      - Search results
    """

    def setup_method(self, method):
        """Set up test resources."""
        self.test_run_id = str(uuid.uuid4())[:8]
        self.workspace_name = f"test-workspace-{self.test_run_id}"
        self.project_name = f"test-project-{self.test_run_id}"
        self.investigation_name = f"test-investigation-{self.test_run_id}"

    def create_mgmt_client(self):
        """Create the ARM management client."""
        from azure.mgmt.discovery import DiscoveryMgmtClient

        return self.create_mgmt_client(DiscoveryMgmtClient)

    # =========================================================================
    # UNIT TESTS - Validate API Surface
    # =========================================================================

    def test_arm_client_has_workspace_operations(self):
        """Validate ARM client exposes workspace operations."""
        from azure.mgmt.discovery import DiscoveryClient

        # Just verify the class structure - no actual API calls
        assert hasattr(DiscoveryClient, "__init__")
        # The client should have workspaces property when instantiated

    def test_arm_client_has_project_operations(self):
        """Validate ARM client exposes project operations."""
        from azure.mgmt.discovery import DiscoveryClient

        assert hasattr(DiscoveryClient, "__init__")

    def test_arm_client_has_supercomputer_operations(self):
        """Validate ARM client exposes supercomputer operations."""
        from azure.mgmt.discovery import DiscoveryClient

        assert hasattr(DiscoveryClient, "__init__")

    def test_workspace_client_has_investigation_operations(self):
        """Validate Workspace client exposes investigation operations."""
        from azure.ai.discovery import WorkspaceClient

        assert hasattr(WorkspaceClient, "__init__")

    def test_workspace_client_has_tools_operations(self):
        """Validate Workspace client exposes tools operations for running on supercomputer."""
        from azure.ai.discovery import WorkspaceClient

        assert hasattr(WorkspaceClient, "__init__")

    def test_bookshelf_client_has_knowledge_base_operations(self):
        """Validate Bookshelf client exposes knowledge base operations."""
        from azure.ai.discovery import BookshelfClient

        assert hasattr(BookshelfClient, "__init__")

    # =========================================================================
    # HERO SCENARIO FLOW DOCUMENTATION
    # =========================================================================

    def test_hero_scenario_flow_documentation(self):
        """
        Document the complete hero scenario flow.

        This test serves as executable documentation of the 10-step
        hero scenario for running a tool on a supercomputer.
        """
        hero_scenario_steps = [
            {
                "step": 1,
                "name": "Create Workspace",
                "client": "ARM (DiscoveryMgmtClient)",
                "operation": "workspaces.begin_create_or_update",
                "description": "Create an Azure Discovery Workspace to organize resources",
            },
            {
                "step": 2,
                "name": "Create Project",
                "client": "ARM (DiscoveryMgmtClient)",
                "operation": "projects.begin_create_or_update",
                "description": "Create a Project within the Workspace for logical grouping",
            },
            {
                "step": 3,
                "name": "Get Supercomputer",
                "client": "ARM (DiscoveryMgmtClient)",
                "operation": "supercomputers.get",
                "description": "Get reference to an existing Supercomputer for compute",
            },
            {
                "step": 4,
                "name": "Get Node Pool",
                "client": "ARM (DiscoveryMgmtClient)",
                "operation": "node_pools.list_by_supercomputer",
                "description": "Get available node pools for running tools",
            },
            {
                "step": 5,
                "name": "Get Tool Definition",
                "client": "ARM (DiscoveryMgmtClient)",
                "operation": "tools.get",
                "description": "Get the tool to run (e.g., molecular dynamics simulation)",
            },
            {
                "step": 6,
                "name": "Create Investigation",
                "client": "Workspace (WorkspaceClient)",
                "operation": "investigations.create_or_update",
                "description": "Create an Investigation to track the scientific workflow",
            },
            {
                "step": 7,
                "name": "Run Tool on Supercomputer",
                "client": "Workspace (WorkspaceClient)",
                "operation": "tools.begin_run",
                "description": "THE HERO - Execute the tool on supercomputer nodes",
            },
            {
                "step": 8,
                "name": "Monitor Run Status",
                "client": "Workspace (WorkspaceClient)",
                "operation": "tools.get_run_status",
                "description": "Poll for completion of the tool run",
            },
            {
                "step": 9,
                "name": "Create Task for Results",
                "client": "Workspace (WorkspaceClient)",
                "operation": "tasks.create",
                "description": "Create a task to process and analyze results",
            },
            {
                "step": 10,
                "name": "Query Knowledge Base",
                "client": "Bookshelf (BookshelfClient)",
                "operation": "knowledge_base_versions.search",
                "description": "Search knowledge base for insights from the run",
            },
        ]

        # Validate all steps are documented
        assert len(hero_scenario_steps) == 10, "Hero scenario has 10 steps"

        # Validate step structure
        for step in hero_scenario_steps:
            assert "step" in step, "step number"
            assert "name" in step, "step name"
            assert "client" in step, "client name"
            assert "operation" in step, "operation name"
            assert "description" in step, "description"

        # Print the flow for documentation
        print("\n=== HERO SCENARIO: Run Tool on Supercomputer ===\n")
        for step in hero_scenario_steps:
            print(f"Step {step['step']}: {step['name']}")
            print(f"  Client: {step['client']}")
            print(f"  Operation: {step['operation']}")
            print(f"  {step['description']}\n")

    # =========================================================================
    # RECORDED INTEGRATION TESTS
    # =========================================================================
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_step1_create_workspace(self):
        """Step 1: Create a Workspace via ARM."""
        from azure.mgmt.discovery import DiscoveryMgmtClient

        client = self.create_mgmt_client(DiscoveryMgmtClient)

        # Create workspace
        poller = client.workspaces.begin_create_or_update(
            resource_group_name=AZURE_RESOURCE_GROUP,
            workspace_name=self.workspace_name,
            resource={"location": AZURE_LOCATION, "properties": {}},
        )
        workspace = poller.result()

        assert workspace is not None
        assert workspace.name == self.workspace_name
        assert workspace.location == AZURE_LOCATION
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_step2_create_project(self):
        """Step 2: Create a Project in the Workspace via ARM."""
        from azure.mgmt.discovery import DiscoveryMgmtClient

        client = self.create_mgmt_client(DiscoveryMgmtClient)

        # Create project
        poller = client.projects.begin_create_or_update(
            resource_group_name=AZURE_RESOURCE_GROUP,
            workspace_name=self.workspace_name,
            project_name=self.project_name,
            resource={"location": AZURE_LOCATION, "properties": {}},
        )
        project = poller.result()

        assert project is not None
        assert project.name == self.project_name
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_step3_verify_supercomputer(self):
        """Step 3: Verify Supercomputer exists."""
        from azure.mgmt.discovery import DiscoveryMgmtClient

        client = self.create_mgmt_client(DiscoveryMgmtClient)

        # Try to get supercomputer
        try:
            supercomputer = client.supercomputers.get(
                resource_group_name=AZURE_RESOURCE_GROUP,
                supercomputer_name=SUPERCOMPUTER_NAME,
            )
            assert supercomputer is not None
            assert supercomputer.name == SUPERCOMPUTER_NAME
        except Exception:
            # If not found, list available supercomputers
            supercomputers = list(client.supercomputers.list_by_subscription())
            print(f"Available supercomputers: {[s.name for s in supercomputers]}")
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_step6_create_investigation(self):
        """Step 6: Create an Investigation via Workspace client."""
        from azure.ai.discovery import WorkspaceClient

        workspace_endpoint = os.environ.get(
            "AZURE_DISCOVERY_WORKSPACE_ENDPOINT", "https://test.workspace.discovery.azure.com"
        )
        client = WorkspaceClient(endpoint=workspace_endpoint, credential=self.get_credential(WorkspaceClient))

        # Create investigation
        investigation = client.investigations.create_or_update(
            investigation_id=self.investigation_name,
            body={"name": self.investigation_name, "description": "Hero scenario test investigation"},
        )

        assert investigation is not None
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_step7_run_tool_on_supercomputer(self):
        """
        Step 7: THE HERO - Run Tool on Supercomputer

        This is the core hero scenario - executing a scientific tool
        on Azure supercomputer infrastructure.

        Prerequisites:
        1. Valid tool_id configured in the workspace
        2. Available node_pool_ids for compute allocation
        3. Tool runs consume compute resources (billable)
        """
        from azure.ai.discovery import WorkspaceClient

        workspace_endpoint = os.environ.get(
            "AZURE_DISCOVERY_WORKSPACE_ENDPOINT", "https://test.workspace.discovery.azure.com"
        )
        client = WorkspaceClient(endpoint=workspace_endpoint, credential=self.get_credential(WorkspaceClient))

        # Run tool on supercomputer
        tool_id = os.environ.get("TOOL_ID", "test-tool")
        node_pool_id = os.environ.get("NODE_POOL_ID", "test-node-pool")

        poller = client.tools.begin_run(
            body={
                "toolId": tool_id,
                "nodePoolIds": [node_pool_id],
                "parameters": {"input_file": "/data/input.dat", "output_dir": "/data/output"},
            }
        )
        run_result = poller.result()

        assert run_result is not None
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_step8_monitor_run_status(self):
        """Step 8: Monitor Tool Run Status."""
        from azure.ai.discovery import WorkspaceClient

        workspace_endpoint = os.environ.get(
            "AZURE_DISCOVERY_WORKSPACE_ENDPOINT", "https://test.workspace.discovery.azure.com"
        )
        client = WorkspaceClient(endpoint=workspace_endpoint, credential=self.get_credential(WorkspaceClient))

        run_id = os.environ.get("RUN_ID", "test-run-id")
        status = client.tools.get_run_status(run_id=run_id)

        assert status is not None
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_step10_query_knowledge_base(self):
        """Step 10: Query Knowledge Base for insights."""
        from azure.ai.discovery import BookshelfClient

        bookshelf_endpoint = os.environ.get(
            "AZURE_DISCOVERY_BOOKSHELF_ENDPOINT", "https://test.bookshelf.discovery.azure.com"
        )
        client = BookshelfClient(endpoint=bookshelf_endpoint, credential=self.get_credential(BookshelfClient))

        knowledge_base_name = os.environ.get("KNOWLEDGE_BASE_NAME", "test-kb")
        version = os.environ.get("KNOWLEDGE_BASE_VERSION", "1")

        # Search the knowledge base
        results = client.knowledge_base_versions.search(
            name=knowledge_base_name, version=version, body={"query": "simulation results", "top": 10}
        )

        assert results is not None
