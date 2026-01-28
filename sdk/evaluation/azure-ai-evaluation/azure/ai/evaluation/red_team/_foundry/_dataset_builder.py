# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DatasetConfigurationBuilder for transforming RAI service responses into PyRIT data structures."""

import atexit
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Set

from pyrit.models import PromptDataType, SeedGroup, SeedObjective, SeedPrompt
from pyrit.scenario import DatasetConfiguration

from .._utils.formatting_utils import format_content_by_modality


class DatasetConfigurationBuilder:
    """Builds PyRIT DatasetConfiguration from RAI service responses.

    This builder transforms RAI service attack objectives and context data
    into PyRIT's native data structures (SeedGroup, SeedObjective, SeedPrompt).

    For standard attacks, the SeedObjective value is automatically used as the
    prompt sent to the target.

    For indirect/XPIA attacks, the attack string is injected into the context
    (email, document, etc.) using modality-based formatting.

    Context data (except tool_call) is stored as files using binary_path data type
    for proper handling of multimodal content.
    """

    # Class-level tracking for temp files
    _temp_files: ClassVar[Set[str]] = set()
    _cleanup_registered: ClassVar[bool] = False

    # Extension mapping for context types
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
        """Initialize builder.

        :param risk_category: The risk category (e.g., "violence", "hate_unfairness")
        :type risk_category: str
        :param is_indirect_attack: If True, use XPIA pattern with injection;
                                   If False, use standard pattern where objective is the prompt
        :type is_indirect_attack: bool
        """
        self.risk_category = risk_category
        self.is_indirect_attack = is_indirect_attack
        self.seed_groups: List[SeedGroup] = []

    def add_objective_with_context(
        self,
        objective_content: str,
        objective_id: Optional[str] = None,
        context_items: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an objective and its associated context to the dataset.

        :param objective_content: The attack string/objective prompt
        :type objective_content: str
        :param objective_id: Unique identifier (UUID string) from RAI service
        :type objective_id: Optional[str]
        :param context_items: List of context dicts with 'content', 'tool_name', 'context_type'
        :type context_items: Optional[List[Dict[str, Any]]]
        :param metadata: Additional metadata like risk_subtype
        :type metadata: Optional[Dict[str, Any]]
        """
        # Generate or parse UUID for grouping
        group_uuid = self._parse_or_generate_uuid(objective_id)

        seeds = []

        # 1. Create SeedObjective (automatically used as prompt to target for standard attacks)
        objective_metadata = metadata.copy() if metadata else {}
        objective_metadata["risk_category"] = self.risk_category

        objective = SeedObjective(
            value=objective_content,
            prompt_group_id=group_uuid,
            metadata=objective_metadata,
            harm_categories=[self.risk_category],
        )
        seeds.append(objective)

        # 2. Handle prompt creation based on strategy type
        if self.is_indirect_attack and context_items:
            # XPIA: Create separate SeedPrompt with injected attack string
            seeds.extend(self._create_xpia_prompts(objective_content, context_items, group_uuid))
        # Note: For standard attacks, we don't add context prompts to the SeedGroup
        # because PyRIT's converters don't support non-text data types.
        # Context is stored in objective metadata for reference if needed.

        # 3. Create seed group
        seed_group = SeedGroup(seeds=seeds)
        self.seed_groups.append(seed_group)

    def _parse_or_generate_uuid(self, objective_id: Optional[str]) -> uuid.UUID:
        """Parse UUID from string or generate a new one.

        :param objective_id: UUID string to parse, or None to generate
        :type objective_id: Optional[str]
        :return: UUID object
        :rtype: uuid.UUID
        """
        if objective_id is None:
            return uuid.uuid4()
        try:
            return uuid.UUID(objective_id)
        except (ValueError, AttributeError):
            return uuid.uuid4()

    def _get_extension_for_context_type(self, context_type: str) -> str:
        """Map context type to appropriate file extension.

        :param context_type: The context type (email, document, code, etc.)
        :type context_type: str
        :return: File extension including the dot (e.g., ".eml")
        :rtype: str
        """
        if not context_type:
            return ".bin"
        return self._EXTENSION_MAP.get(context_type.lower(), ".bin")

    def _get_context_file_directory(self) -> Path:
        """Get the directory for storing context files.

        Uses PyRIT's DB_DATA_PATH if available, otherwise system temp.

        :return: Path to the context file directory
        :rtype: Path
        """
        try:
            from pyrit.common.path import DB_DATA_PATH
            base_dir = Path(DB_DATA_PATH) / "seed-prompt-entries" / "binaries"
        except ImportError:
            base_dir = Path(tempfile.gettempdir()) / "pyrit_foundry_context"

        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir

    def _create_context_file(self, content: str, context_type: str) -> str:
        """Create a file for context content and return its path.

        The file is created in PyRIT's data directory (or system temp) and
        tracked for cleanup.

        :param content: The context content to write
        :type content: str
        :param context_type: The context type (determines file extension)
        :type context_type: str
        :return: Absolute path to the created file
        :rtype: str
        """
        extension = self._get_extension_for_context_type(context_type)
        base_dir = self._get_context_file_directory()

        # Generate unique filename using UUID
        filename = f"context_{uuid.uuid4().hex}{extension}"
        file_path = base_dir / filename

        # Write content to file
        file_path.write_text(content, encoding="utf-8")

        # Track for cleanup
        DatasetConfigurationBuilder._temp_files.add(str(file_path))
        self._register_cleanup()

        return str(file_path)

    def _register_cleanup(self) -> None:
        """Register atexit handler for cleanup (once only)."""
        if not DatasetConfigurationBuilder._cleanup_registered:
            atexit.register(DatasetConfigurationBuilder._cleanup_all_files)
            DatasetConfigurationBuilder._cleanup_registered = True

    @classmethod
    def _cleanup_all_files(cls) -> None:
        """Clean up all tracked temp files."""
        for file_path in cls._temp_files.copy():
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                cls._temp_files.discard(file_path)
            except Exception:
                pass  # Best effort cleanup

    def cleanup(self) -> None:
        """Explicitly clean up temp files created by this builder."""
        DatasetConfigurationBuilder._cleanup_all_files()

    def _create_context_prompts(
        self,
        context_items: List[Dict[str, Any]],
        group_uuid: uuid.UUID,
    ) -> List[SeedPrompt]:
        """Create SeedPrompt objects from context items.

        For non-tool_call context, content is written to files and the file path
        is used as the SeedPrompt value with binary_path data type.

        :param context_items: List of context dictionaries
        :type context_items: List[Dict[str, Any]]
        :param group_uuid: UUID linking this context to its objective
        :type group_uuid: uuid.UUID
        :return: List of SeedPrompt objects
        :rtype: List[SeedPrompt]
        """
        prompts = []
        for idx, ctx in enumerate(context_items):
            if not ctx or not isinstance(ctx, dict):
                continue

            content = ctx.get("content", "")
            if not content:
                continue

            context_type = ctx.get("context_type") or "text"
            data_type = self._determine_data_type(ctx)

            # For binary_path, write content to file and use path as value
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

            prompt = SeedPrompt(
                value=value,
                data_type=data_type,
                prompt_group_id=group_uuid,
                metadata=ctx_metadata,
                role="user",
                sequence=idx + 1,  # Sequence 0 is reserved for the objective
            )
            prompts.append(prompt)

        return prompts

    def _create_xpia_prompts(
        self,
        attack_string: str,
        context_items: List[Dict[str, Any]],
        group_uuid: uuid.UUID,
    ) -> List[SeedPrompt]:
        """Create XPIA prompts with attack string injected into context.

        For indirect attacks, we inject the attack string into the
        attack vehicle (email, document, etc.) using modality-based formatting,
        and create prompts for both the injected version and original context.

        For non-tool_call context, content is written to files and the file path
        is used as the SeedPrompt value with binary_path data type.

        :param attack_string: The attack objective to inject
        :type attack_string: str
        :param context_items: List of context dictionaries
        :type context_items: List[Dict[str, Any]]
        :param group_uuid: UUID linking prompts to their objective
        :type group_uuid: uuid.UUID
        :return: List of SeedPrompt objects
        :rtype: List[SeedPrompt]
        """
        prompts = []

        for idx, ctx in enumerate(context_items):
            if not ctx or not isinstance(ctx, dict):
                continue

            content = ctx.get("content", "")
            context_type = ctx.get("context_type") or "text"
            tool_name = ctx.get("tool_name")
            data_type = self._determine_data_type(ctx)

            # Format and inject attack string into content based on context type
            injected_content = self._inject_attack_into_vehicle(
                attack_string=attack_string,
                content=content,
                context_type=context_type,
            )

            # For binary_path, write content to files and use paths as values
            if data_type == "binary_path":
                attack_vehicle_value = self._create_context_file(injected_content, context_type)
                original_value = self._create_context_file(content, context_type) if content else None
            else:
                attack_vehicle_value = injected_content
                original_value = content

            # Create attack vehicle prompt (with injection) - this is what gets sent
            attack_vehicle = SeedPrompt(
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

            # Keep original context for reference (for result reconstruction)
            if original_value:
                original_prompt = SeedPrompt(
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
                    sequence=idx + 100,  # High sequence to keep separate
                )
                prompts.append(original_prompt)

        return prompts

    def _inject_attack_into_vehicle(
        self,
        attack_string: str,
        content: str,
        context_type: str,
    ) -> str:
        """Inject attack string into context based on context type.

        Uses modality-based formatting to hide the attack within the context
        in a format appropriate for the context type.

        :param attack_string: The attack objective to inject
        :type attack_string: str
        :param content: The original context content
        :type content: str
        :param context_type: Type of context (email, document, html, code, etc.)
        :type context_type: str
        :return: Content with attack string injected
        :rtype: str
        """
        context_type = context_type.lower() if context_type else "text"

        # Use format_content_by_modality to format the attack appropriately
        # This applies random formatting based on context type (hidden divs, comments, etc.)
        try:
            formatted_attack = format_content_by_modality(attack_string, context_type)
        except Exception:
            # Fallback if formatting fails
            formatted_attack = attack_string

        # Check if content has {attack_text} placeholder
        if "{attack_text}" in content:
            return content.replace("{attack_text}", formatted_attack)

        # Otherwise, inject based on context type
        if context_type == "email":
            return f"{content}\n\n{formatted_attack}"
        elif context_type == "document":
            return f"{content}\n\n{formatted_attack}"
        elif context_type == "html":
            # Inject as hidden element
            return f"{content}\n<div style=\"display:none\">{formatted_attack}</div>"
        elif context_type == "code":
            # Inject as comment
            return f"{content}\n# {formatted_attack}"
        elif context_type == "markdown":
            # Inject in markdown comment-like structure
            return f"{content}\n\n[//]: # ({formatted_attack})"
        elif context_type == "footnote":
            return f"{content}\n\n[^note]: {formatted_attack}"
        else:
            # Default: append
            return f"{content}\n\n{formatted_attack}"

    def _determine_data_type(self, context: Dict[str, Any]) -> PromptDataType:
        """Determine appropriate PromptDataType for context.

        Maps RAI service context_type to PyRIT PromptDataType:
        - tool_call → tool_call (stored inline, not as file)
        - All other types → binary_path (stored as files)

        The original context_type is preserved in metadata for semantic information
        and XPIA formatting. The content is written to files with appropriate
        extensions based on context_type.

        :param context: Context dictionary with optional 'context_type' key
        :type context: Dict[str, Any]
        :return: Appropriate PromptDataType
        :rtype: PromptDataType
        """
        context_type = (context.get("context_type") or "").lower()

        # tool_call is always stored inline (not as file)
        if context_type == "tool_call":
            return "tool_call"

        # All other context types are stored as files using binary_path
        return "binary_path"

    def build(self) -> DatasetConfiguration:
        """Build the final DatasetConfiguration.

        :return: DatasetConfiguration containing all seed groups
        :rtype: DatasetConfiguration
        """
        return DatasetConfiguration(seed_groups=self.seed_groups)

    def __len__(self) -> int:
        """Return number of seed groups (objectives) added."""
        return len(self.seed_groups)
