# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Unit tests for azure-ai-discovery models.

These tests verify model initialization without making HTTP calls.
"""
import pytest
from azure.ai.discovery import models


class TestWorkspaceModelsUnit:
    """Unit tests for Workspace data plane SDK models."""

    def test_task_model(self):
        """Test Task model can be initialized."""
        task = models.Task(title="Analyze data", description="Run analysis")
        assert task.title == "Analyze data"
        assert task.description == "Run analysis"

    def test_tag_model(self):
        """Test Tag model can be initialized."""
        tag = models.Tag(key="environment", value="production")
        assert tag.key == "environment"
        assert tag.value == "production"

    def test_run_request_environment_variable_model(self):
        """Test RunRequestEnvironmentVariable model can be initialized."""
        env_var = models.RunRequestEnvironmentVariable(name="MY_VAR", value="my_value")
        assert env_var.name == "MY_VAR"
        assert env_var.value == "my_value"

    def test_inline_file_model(self):
        """Test InlineFile model can be initialized."""
        inline_file = models.InlineFile(mount_path="/data/input.txt", encoded_file="base64data")
        assert inline_file.mount_path == "/data/input.txt"
        assert inline_file.encoded_file == "base64data"

    def test_input_data_mount_model(self):
        """Test InputDataMount model can be initialized."""
        mount = models.InputDataMount(storage_uri="https://storage/container", mount_path="/data/input")
        assert mount.storage_uri == "https://storage/container"
        assert mount.mount_path == "/data/input"

    def test_output_data_mount_model(self):
        """Test OutputDataMount model can be initialized."""
        mount = models.OutputDataMount(storage_uri="https://storage/output", mount_path="/data/output")
        assert mount.storage_uri == "https://storage/output"
        assert mount.mount_path == "/data/output"

    def test_task_status_enum(self):
        """Test TaskStatus enum values exist."""
        assert models.TaskStatus.NEW is not None
        assert models.TaskStatus.COMPLETE is not None
        assert models.TaskStatus.EXECUTING is not None
        assert models.TaskStatus.FAILED is not None

    def test_investigation_status_enum(self):
        """Test InvestigationStatus enum values exist."""
        assert models.InvestigationStatus.CREATED is not None
        assert models.InvestigationStatus.VALIDATED is not None
        assert models.InvestigationStatus.FAILED is not None

    def test_by_type_enum(self):
        """Test ByType enum values exist."""
        assert models.ByType.USER is not None
        assert models.ByType.APPLICATION is not None
        assert models.ByType.SYSTEM is not None

    def test_discovery_engine_status_enum(self):
        """Test DiscoveryEngineStatus enum values exist."""
        assert models.DiscoveryEngineStatus.INACTIVE is not None
        assert models.DiscoveryEngineStatus.ACTIVE is not None

    def test_run_status_enum(self):
        """Test RunStatus enum values exist."""
        assert models.RunStatus.NOT_STARTED is not None
        assert models.RunStatus.RUNNING is not None
        assert models.RunStatus.SUCCEEDED is not None
        assert models.RunStatus.FAILED is not None
        assert models.RunStatus.CANCELED is not None


class TestBookshelfModelsUnit:
    """Unit tests for Bookshelf data plane SDK models."""

    def test_knowledge_base_model(self):
        """Test KnowledgeBase model can be initialized."""
        kb = models.KnowledgeBase(
            description="A test knowledge base",
            copilot_instruction="Test instruction",
        )
        assert kb.description == "A test knowledge base"
        assert kb.copilot_instruction == "Test instruction"

    def test_knowledge_base_version_model(self):
        """Test KnowledgeBaseVersion model can be initialized."""
        version = models.KnowledgeBaseVersion(
            description="Version 1",
            copilot_instruction="Instruction v1",
        )
        assert version.description == "Version 1"
        assert version.copilot_instruction == "Instruction v1"

    def test_storage_asset_reference_model(self):
        """Test StorageAssetReference model can be initialized."""
        ref = models.StorageAssetReference(id="asset-123")
        assert ref.id == "asset-123"
