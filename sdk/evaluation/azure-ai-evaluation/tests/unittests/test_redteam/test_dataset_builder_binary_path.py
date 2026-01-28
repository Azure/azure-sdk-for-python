# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Unit tests for DatasetConfigurationBuilder binary_path functionality.

These tests verify the new binary_path-based context storage introduced
to store all context (except tool_call) as files.
"""

import atexit
import os
import pytest
import tempfile
import uuid
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Set
from unittest.mock import MagicMock, patch


# =============================================================================
# Mock PyRIT classes
# =============================================================================
class MockSeedGroup:
    def __init__(self, seeds=None):
        self.seeds = seeds or []


class MockSeedObjective:
    def __init__(self, value="", prompt_group_id=None, metadata=None, harm_categories=None):
        self.value = value
        self.prompt_group_id = prompt_group_id
        self.metadata = metadata or {}
        self.harm_categories = harm_categories or []


class MockSeedPrompt:
    def __init__(self, value="", data_type="text", prompt_group_id=None, metadata=None, role="user", sequence=0):
        self.value = value
        self.data_type = data_type
        self.prompt_group_id = prompt_group_id
        self.metadata = metadata or {}
        self.role = role
        self.sequence = sequence


class MockDatasetConfiguration:
    def __init__(self, seed_groups=None):
        self.seed_groups = seed_groups or []

    def get_all_seed_groups(self):
        return self.seed_groups


def mock_format_content_by_modality(text, modality):
    """Mock formatting function."""
    return f"[{modality}]{text}"


# =============================================================================
# DatasetConfigurationBuilder copy for testing
# =============================================================================
class DatasetConfigurationBuilder:
    """Copy of the DatasetConfigurationBuilder for isolated testing."""

    _temp_files: ClassVar[Set[str]] = set()
    _cleanup_registered: ClassVar[bool] = False

    _EXTENSION_MAP: ClassVar[Dict[str, str]] = {
        "email": ".eml",
        "document": ".txt",
        "code": ".py",
        "markdown": ".md",
        "html": ".html",
        "footnote": ".txt",
        "text": ".txt",
    }

    def __init__(self, risk_category: str, is_indirect_attack: bool = False):
        self.risk_category = risk_category
        self.is_indirect_attack = is_indirect_attack
        self.seed_groups: List[MockSeedGroup] = []

    def add_objective_with_context(
        self,
        objective_content: str,
        objective_id: Optional[str] = None,
        context_items: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        group_uuid = self._parse_or_generate_uuid(objective_id)
        seeds = []

        objective_metadata = metadata.copy() if metadata else {}
        objective_metadata["risk_category"] = self.risk_category

        objective = MockSeedObjective(
            value=objective_content,
            prompt_group_id=group_uuid,
            metadata=objective_metadata,
            harm_categories=[self.risk_category],
        )
        seeds.append(objective)

        if self.is_indirect_attack and context_items:
            seeds.extend(self._create_xpia_prompts(objective_content, context_items, group_uuid))
        elif context_items:
            seeds.extend(self._create_context_prompts(context_items, group_uuid))

        seed_group = MockSeedGroup(seeds=seeds)
        self.seed_groups.append(seed_group)

    def _parse_or_generate_uuid(self, objective_id: Optional[str]) -> uuid.UUID:
        if objective_id is None:
            return uuid.uuid4()
        try:
            return uuid.UUID(objective_id)
        except (ValueError, AttributeError):
            return uuid.uuid4()

    def _get_extension_for_context_type(self, context_type: str) -> str:
        return self._EXTENSION_MAP.get(context_type.lower(), ".bin")

    def _get_context_file_directory(self) -> Path:
        base_dir = Path(tempfile.gettempdir()) / "pyrit_foundry_context_test"
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir

    def _create_context_file(self, content: str, context_type: str) -> str:
        extension = self._get_extension_for_context_type(context_type)
        base_dir = self._get_context_file_directory()

        filename = f"context_{uuid.uuid4().hex}{extension}"
        file_path = base_dir / filename

        file_path.write_text(content, encoding="utf-8")

        DatasetConfigurationBuilder._temp_files.add(str(file_path))
        self._register_cleanup()

        return str(file_path)

    def _register_cleanup(self) -> None:
        if not DatasetConfigurationBuilder._cleanup_registered:
            atexit.register(DatasetConfigurationBuilder._cleanup_all_files)
            DatasetConfigurationBuilder._cleanup_registered = True

    @classmethod
    def _cleanup_all_files(cls) -> None:
        for file_path in cls._temp_files.copy():
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                cls._temp_files.discard(file_path)
            except Exception:
                pass

    def cleanup(self) -> None:
        DatasetConfigurationBuilder._cleanup_all_files()

    def _create_context_prompts(
        self,
        context_items: List[Dict[str, Any]],
        group_uuid: uuid.UUID,
    ) -> List[MockSeedPrompt]:
        prompts = []
        for idx, ctx in enumerate(context_items):
            if not ctx or not isinstance(ctx, dict):
                continue

            content = ctx.get("content", "")
            if not content:
                continue

            context_type = ctx.get("context_type", "text")
            data_type = self._determine_data_type(ctx)

            if data_type == "binary_path":
                value = self._create_context_file(content, context_type)
            else:
                value = content

            ctx_metadata = {
                "is_context": True,
                "context_index": idx,
                "original_content_length": len(content),
            }
            if ctx.get("tool_name"):
                ctx_metadata["tool_name"] = ctx.get("tool_name")
            if context_type:
                ctx_metadata["context_type"] = context_type

            prompt = MockSeedPrompt(
                value=value,
                data_type=data_type,
                prompt_group_id=group_uuid,
                metadata=ctx_metadata,
                role="user",
                sequence=idx + 1,
            )
            prompts.append(prompt)

        return prompts

    def _create_xpia_prompts(
        self,
        attack_string: str,
        context_items: List[Dict[str, Any]],
        group_uuid: uuid.UUID,
    ) -> List[MockSeedPrompt]:
        prompts = []

        for idx, ctx in enumerate(context_items):
            if not ctx or not isinstance(ctx, dict):
                continue

            content = ctx.get("content", "")
            context_type = ctx.get("context_type", "text")
            tool_name = ctx.get("tool_name")
            data_type = self._determine_data_type(ctx)

            injected_content = self._inject_attack_into_vehicle(
                attack_string=attack_string,
                content=content,
                context_type=context_type,
            )

            if data_type == "binary_path":
                attack_vehicle_value = self._create_context_file(injected_content, context_type)
                original_value = self._create_context_file(content, context_type) if content else None
            else:
                attack_vehicle_value = injected_content
                original_value = content

            attack_vehicle = MockSeedPrompt(
                value=attack_vehicle_value,
                data_type=data_type,
                prompt_group_id=group_uuid,
                metadata={
                    "context_type": context_type,
                    "tool_name": tool_name,
                    "is_attack_vehicle": True,
                    "contains_injected_attack": True,
                    "context_index": idx,
                    "original_content_length": len(injected_content),
                },
                role="user",
                sequence=idx + 1,
            )
            prompts.append(attack_vehicle)

            if original_value:
                original_prompt = MockSeedPrompt(
                    value=original_value,
                    data_type=data_type,
                    prompt_group_id=group_uuid,
                    metadata={
                        "context_type": context_type,
                        "tool_name": tool_name,
                        "is_original_context": True,
                        "context_index": idx,
                        "original_content_length": len(content) if content else 0,
                    },
                    role="user",
                    sequence=idx + 100,
                )
                prompts.append(original_prompt)

        return prompts

    def _inject_attack_into_vehicle(
        self,
        attack_string: str,
        content: str,
        context_type: str,
    ) -> str:
        context_type = context_type.lower() if context_type else "text"

        try:
            formatted_attack = mock_format_content_by_modality(attack_string, context_type)
        except Exception:
            formatted_attack = attack_string

        if "{attack_text}" in content:
            return content.replace("{attack_text}", formatted_attack)

        if context_type == "email":
            return f"{content}\n\n{formatted_attack}"
        elif context_type == "document":
            return f"{content}\n\n{formatted_attack}"
        elif context_type == "html":
            return f"{content}\n<div style=\"display:none\">{formatted_attack}</div>"
        elif context_type == "code":
            return f"{content}\n# {formatted_attack}"
        elif context_type == "markdown":
            return f"{content}\n\n[//]: # ({formatted_attack})"
        elif context_type == "footnote":
            return f"{content}\n\n[^note]: {formatted_attack}"
        else:
            return f"{content}\n\n{formatted_attack}"

    def _determine_data_type(self, context: Dict[str, Any]) -> str:
        context_type = context.get("context_type", "").lower()

        if context_type == "tool_call":
            return "tool_call"

        return "binary_path"

    def build(self) -> MockDatasetConfiguration:
        return MockDatasetConfiguration(seed_groups=self.seed_groups)

    def __len__(self) -> int:
        return len(self.seed_groups)


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Clean up temp files after each test."""
    yield
    DatasetConfigurationBuilder._cleanup_all_files()


@pytest.fixture
def builder():
    """Create a fresh DatasetConfigurationBuilder for each test."""
    return DatasetConfigurationBuilder(risk_category="violence", is_indirect_attack=False)


@pytest.fixture
def indirect_builder():
    """Create a DatasetConfigurationBuilder for indirect attacks."""
    return DatasetConfigurationBuilder(risk_category="violence", is_indirect_attack=True)


@pytest.fixture
def sample_context_items():
    """Sample context items for testing."""
    return [
        {"content": "Email body content here", "context_type": "email", "tool_name": "email_reader"},
        {"content": "<html><body>Page</body></html>", "context_type": "html", "tool_name": "browser"},
        {"content": "def main(): pass", "context_type": "code", "tool_name": "code_reader"},
    ]


# =============================================================================
# Tests for Extension Mapping
# =============================================================================
@pytest.mark.unittest
class TestExtensionMapping:
    """Test the context type to file extension mapping."""

    def test_email_extension(self, builder):
        """Test email context type maps to .eml extension."""
        assert builder._get_extension_for_context_type("email") == ".eml"

    def test_document_extension(self, builder):
        """Test document context type maps to .txt extension."""
        assert builder._get_extension_for_context_type("document") == ".txt"

    def test_code_extension(self, builder):
        """Test code context type maps to .py extension."""
        assert builder._get_extension_for_context_type("code") == ".py"

    def test_markdown_extension(self, builder):
        """Test markdown context type maps to .md extension."""
        assert builder._get_extension_for_context_type("markdown") == ".md"

    def test_html_extension(self, builder):
        """Test html context type maps to .html extension."""
        assert builder._get_extension_for_context_type("html") == ".html"

    def test_footnote_extension(self, builder):
        """Test footnote context type maps to .txt extension."""
        assert builder._get_extension_for_context_type("footnote") == ".txt"

    def test_text_extension(self, builder):
        """Test text context type maps to .txt extension."""
        assert builder._get_extension_for_context_type("text") == ".txt"

    def test_unknown_extension(self, builder):
        """Test unknown context type maps to .bin extension."""
        assert builder._get_extension_for_context_type("unknown") == ".bin"
        assert builder._get_extension_for_context_type("random_type") == ".bin"

    def test_case_insensitive(self, builder):
        """Test extension mapping is case insensitive."""
        assert builder._get_extension_for_context_type("EMAIL") == ".eml"
        assert builder._get_extension_for_context_type("Html") == ".html"


# =============================================================================
# Tests for Data Type Determination
# =============================================================================
@pytest.mark.unittest
class TestDataTypeDetermination:
    """Test the _determine_data_type method."""

    def test_tool_call_returns_tool_call(self, builder):
        """Test that tool_call context returns tool_call data type."""
        result = builder._determine_data_type({"context_type": "tool_call"})
        assert result == "tool_call"

    def test_email_returns_binary_path(self, builder):
        """Test that email context returns binary_path data type."""
        result = builder._determine_data_type({"context_type": "email"})
        assert result == "binary_path"

    def test_document_returns_binary_path(self, builder):
        """Test that document context returns binary_path data type."""
        result = builder._determine_data_type({"context_type": "document"})
        assert result == "binary_path"

    def test_code_returns_binary_path(self, builder):
        """Test that code context returns binary_path data type."""
        result = builder._determine_data_type({"context_type": "code"})
        assert result == "binary_path"

    def test_html_returns_binary_path(self, builder):
        """Test that html context returns binary_path data type."""
        result = builder._determine_data_type({"context_type": "html"})
        assert result == "binary_path"

    def test_markdown_returns_binary_path(self, builder):
        """Test that markdown context returns binary_path data type."""
        result = builder._determine_data_type({"context_type": "markdown"})
        assert result == "binary_path"

    def test_empty_context_type_returns_binary_path(self, builder):
        """Test that empty context type returns binary_path data type."""
        result = builder._determine_data_type({"context_type": ""})
        assert result == "binary_path"

    def test_no_context_type_returns_binary_path(self, builder):
        """Test that missing context type returns binary_path data type."""
        result = builder._determine_data_type({})
        assert result == "binary_path"

    def test_unknown_type_returns_binary_path(self, builder):
        """Test that unknown context type returns binary_path data type."""
        result = builder._determine_data_type({"context_type": "unknown_type"})
        assert result == "binary_path"


# =============================================================================
# Tests for File Creation
# =============================================================================
@pytest.mark.unittest
class TestFileCreation:
    """Test the _create_context_file method."""

    def test_creates_file_with_content(self, builder):
        """Test that file is created with correct content."""
        content = "Test content for file"
        file_path = builder._create_context_file(content, "email")

        assert os.path.exists(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            assert f.read() == content

    def test_file_has_correct_extension(self, builder):
        """Test that created file has correct extension."""
        file_path = builder._create_context_file("content", "email")
        assert file_path.endswith(".eml")

        file_path = builder._create_context_file("content", "code")
        assert file_path.endswith(".py")

        file_path = builder._create_context_file("content", "html")
        assert file_path.endswith(".html")

    def test_files_tracked_for_cleanup(self, builder):
        """Test that created files are tracked for cleanup."""
        initial_count = len(DatasetConfigurationBuilder._temp_files)

        builder._create_context_file("content1", "email")
        builder._create_context_file("content2", "code")

        assert len(DatasetConfigurationBuilder._temp_files) >= initial_count + 2

    def test_unique_filenames(self, builder):
        """Test that each file gets a unique filename."""
        file_path1 = builder._create_context_file("content", "email")
        file_path2 = builder._create_context_file("content", "email")

        assert file_path1 != file_path2

    def test_handles_unicode_content(self, builder):
        """Test that unicode content is handled correctly."""
        content = "Unicode content: 你好世界 🌍 émoji"
        file_path = builder._create_context_file(content, "text")

        with open(file_path, "r", encoding="utf-8") as f:
            assert f.read() == content


# =============================================================================
# Tests for Cleanup
# =============================================================================
@pytest.mark.unittest
class TestCleanup:
    """Test the cleanup functionality."""

    def test_cleanup_removes_files(self, builder):
        """Test that cleanup removes created files."""
        file_path = builder._create_context_file("content", "email")
        assert os.path.exists(file_path)

        builder.cleanup()

        assert not os.path.exists(file_path)

    def test_cleanup_clears_tracking_set(self, builder):
        """Test that cleanup clears the tracking set."""
        builder._create_context_file("content", "email")
        builder._create_context_file("content", "code")

        builder.cleanup()

        assert len(DatasetConfigurationBuilder._temp_files) == 0

    def test_cleanup_handles_already_deleted_files(self, builder):
        """Test that cleanup handles files that were already deleted."""
        file_path = builder._create_context_file("content", "email")
        os.remove(file_path)

        builder.cleanup()


# =============================================================================
# Tests for Context Prompt Creation
# =============================================================================
@pytest.mark.unittest
class TestContextPromptCreation:
    """Test the _create_context_prompts method."""

    def test_creates_prompts_with_binary_path(self, builder, sample_context_items):
        """Test that context prompts are created with binary_path data type."""
        group_uuid = uuid.uuid4()
        prompts = builder._create_context_prompts(sample_context_items, group_uuid)

        for prompt in prompts:
            assert prompt.data_type == "binary_path"

    def test_prompt_values_are_file_paths(self, builder, sample_context_items):
        """Test that prompt values are file paths, not content."""
        group_uuid = uuid.uuid4()
        prompts = builder._create_context_prompts(sample_context_items, group_uuid)

        for prompt in prompts:
            assert os.path.exists(prompt.value)
            with open(prompt.value, "r", encoding="utf-8") as f:
                content = f.read()
                assert any(item["content"] in content for item in sample_context_items)

    def test_metadata_includes_original_content_length(self, builder, sample_context_items):
        """Test that metadata includes original content length."""
        group_uuid = uuid.uuid4()
        prompts = builder._create_context_prompts(sample_context_items, group_uuid)

        for prompt in prompts:
            assert "original_content_length" in prompt.metadata

    def test_tool_call_stored_inline(self, builder):
        """Test that tool_call context is stored inline, not as file."""
        context_items = [
            {"content": "Tool output here", "context_type": "tool_call", "tool_name": "my_tool"}
        ]
        group_uuid = uuid.uuid4()
        prompts = builder._create_context_prompts(context_items, group_uuid)

        assert len(prompts) == 1
        assert prompts[0].data_type == "tool_call"
        assert prompts[0].value == "Tool output here"

    def test_empty_content_skipped(self, builder):
        """Test that empty content items are skipped."""
        context_items = [
            {"content": "", "context_type": "email"},
            {"content": "Valid content", "context_type": "document"},
        ]
        group_uuid = uuid.uuid4()
        prompts = builder._create_context_prompts(context_items, group_uuid)

        assert len(prompts) == 1


# =============================================================================
# Tests for XPIA Prompt Creation
# =============================================================================
@pytest.mark.unittest
class TestXPIAPromptCreation:
    """Test the _create_xpia_prompts method."""

    def test_creates_attack_vehicle_as_file(self, indirect_builder, sample_context_items):
        """Test that XPIA attack vehicle is stored as file."""
        group_uuid = uuid.uuid4()
        prompts = indirect_builder._create_xpia_prompts(
            attack_string="Malicious prompt",
            context_items=sample_context_items,
            group_uuid=group_uuid,
        )

        attack_vehicles = [p for p in prompts if p.metadata.get("is_attack_vehicle")]
        for av in attack_vehicles:
            assert av.data_type == "binary_path"
            assert os.path.exists(av.value)

    def test_creates_original_context_as_file(self, indirect_builder, sample_context_items):
        """Test that original context is stored as file."""
        group_uuid = uuid.uuid4()
        prompts = indirect_builder._create_xpia_prompts(
            attack_string="Malicious prompt",
            context_items=sample_context_items,
            group_uuid=group_uuid,
        )

        originals = [p for p in prompts if p.metadata.get("is_original_context")]
        for orig in originals:
            assert orig.data_type == "binary_path"
            assert os.path.exists(orig.value)

    def test_attack_vehicle_contains_injected_content(self, indirect_builder):
        """Test that attack vehicle file contains injected attack."""
        context_items = [{"content": "Original email body", "context_type": "email"}]
        group_uuid = uuid.uuid4()
        prompts = indirect_builder._create_xpia_prompts(
            attack_string="INJECT_THIS",
            context_items=context_items,
            group_uuid=group_uuid,
        )

        attack_vehicle = next(p for p in prompts if p.metadata.get("is_attack_vehicle"))
        with open(attack_vehicle.value, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Original email body" in content
            assert "INJECT_THIS" in content

    def test_original_and_vehicle_are_different_files(self, indirect_builder):
        """Test that original and attack vehicle are different files."""
        context_items = [{"content": "Content here", "context_type": "email"}]
        group_uuid = uuid.uuid4()
        prompts = indirect_builder._create_xpia_prompts(
            attack_string="Attack",
            context_items=context_items,
            group_uuid=group_uuid,
        )

        attack_vehicle = next(p for p in prompts if p.metadata.get("is_attack_vehicle"))
        original = next(p for p in prompts if p.metadata.get("is_original_context"))

        assert attack_vehicle.value != original.value


# =============================================================================
# Tests for Full Build Flow
# =============================================================================
@pytest.mark.unittest
class TestFullBuildFlow:
    """Test the full build flow with binary_path."""

    def test_add_objective_with_context_creates_files(self, builder, sample_context_items):
        """Test that add_objective_with_context creates files for context."""
        initial_file_count = len(DatasetConfigurationBuilder._temp_files)

        builder.add_objective_with_context(
            objective_content="Test objective",
            objective_id=str(uuid.uuid4()),
            context_items=sample_context_items,
            metadata={"risk_subtype": "test"},
        )

        assert len(DatasetConfigurationBuilder._temp_files) >= initial_file_count + 3

    def test_build_returns_valid_configuration(self, builder, sample_context_items):
        """Test that build() returns valid DatasetConfiguration."""
        builder.add_objective_with_context(
            objective_content="Test objective",
            context_items=sample_context_items,
        )

        config = builder.build()

        assert hasattr(config, "get_all_seed_groups")
        assert len(config.get_all_seed_groups()) == 1

    def test_indirect_attack_with_context_creates_files(self, indirect_builder, sample_context_items):
        """Test that indirect attack creates files for attack vehicles."""
        indirect_builder.add_objective_with_context(
            objective_content="Hidden attack",
            objective_id=str(uuid.uuid4()),
            context_items=sample_context_items,
            metadata={"risk_subtype": "xpia"},
        )

        assert len(DatasetConfigurationBuilder._temp_files) > 0

    def test_len_method(self, builder):
        """Test that __len__ returns correct count."""
        assert len(builder) == 0

        builder.add_objective_with_context(objective_content="Test 1")
        assert len(builder) == 1

        builder.add_objective_with_context(objective_content="Test 2")
        assert len(builder) == 2
