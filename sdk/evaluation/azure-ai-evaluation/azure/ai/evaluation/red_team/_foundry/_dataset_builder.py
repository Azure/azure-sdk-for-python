# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DatasetConfigurationBuilder for transforming RAI service responses into PyRIT data structures."""

import uuid
from typing import Any, Dict, List, Optional

from pyrit.models.literals import PromptDataType
from pyrit.models.seeds import SeedGroup, SeedObjective, SeedPrompt
from pyrit.scenario.core.dataset_configuration import DatasetConfiguration

from .._utils.formatting_utils import format_content_by_modality


class DatasetConfigurationBuilder:
    """Builds PyRIT DatasetConfiguration from RAI service responses.

    This builder transforms RAI service attack objectives and context data
    into PyRIT's native data structures (SeedGroup, SeedObjective, SeedPrompt).

    For standard attacks, the SeedObjective value is automatically used as the
    prompt sent to the target.

    For indirect/XPIA attacks, the attack string is injected into the context
    (email, document, etc.) using modality-based formatting.
    """

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
        elif context_items:
            # Standard: Just add context prompts if present (objective is used as-is)
            seeds.extend(self._create_context_prompts(context_items, group_uuid))

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

    def _create_context_prompts(
        self,
        context_items: List[Dict[str, Any]],
        group_uuid: uuid.UUID,
    ) -> List[SeedPrompt]:
        """Create SeedPrompt objects from context items.

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

            ctx_metadata = {
                "is_context": True,
                "context_index": idx,
            }
            if ctx.get("tool_name"):
                ctx_metadata["tool_name"] = ctx.get("tool_name")
            if ctx.get("context_type"):
                ctx_metadata["context_type"] = ctx.get("context_type")

            prompt = SeedPrompt(
                value=content,
                data_type=self._determine_data_type(ctx),
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
            context_type = ctx.get("context_type", "text")
            tool_name = ctx.get("tool_name")

            # Format and inject attack string into content based on context type
            injected_content = self._inject_attack_into_vehicle(
                attack_string=attack_string,
                content=content,
                context_type=context_type,
            )

            # Create attack vehicle prompt (with injection) - this is what gets sent
            attack_vehicle = SeedPrompt(
                value=injected_content,
                data_type=self._determine_data_type(ctx),
                prompt_group_id=group_uuid,
                metadata={
                    "context_type": context_type,
                    "tool_name": tool_name,
                    "is_attack_vehicle": True,
                    "contains_injected_attack": True,
                    "context_index": idx,
                },
                role="user",
                sequence=idx + 1,
            )
            prompts.append(attack_vehicle)

            # Keep original context for reference (for result reconstruction)
            if content:
                original_prompt = SeedPrompt(
                    value=content,
                    data_type=self._determine_data_type(ctx),
                    prompt_group_id=group_uuid,
                    metadata={
                        "context_type": context_type,
                        "tool_name": tool_name,
                        "is_original_context": True,
                        "context_index": idx,
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
        - tool_call → tool_call (direct match)
        - email, document, code, text, markdown, footnote → text
        - html, url, web → url
        - image-related → image_path
        - audio-related → audio_path
        - video-related → video_path

        The original context_type is preserved in metadata for semantic information
        and XPIA formatting.

        :param context: Context dictionary with optional 'context_type' key
        :type context: Dict[str, Any]
        :return: Appropriate PromptDataType
        :rtype: PromptDataType
        """
        context_type = context.get("context_type", "").lower()

        # Direct semantic matches
        if context_type == "tool_call":
            return "tool_call"
        elif "image" in context_type:
            return "image_path"
        elif "audio" in context_type:
            return "audio_path"
        elif "video" in context_type:
            return "video_path"
        elif context_type in ("html", "url", "web"):
            return "url"
        else:
            # Default for email, document, code, text, markdown, footnote, and unspecified
            return "text"

    def build(self) -> DatasetConfiguration:
        """Build the final DatasetConfiguration.

        :return: DatasetConfiguration containing all seed groups
        :rtype: DatasetConfiguration
        """
        return DatasetConfiguration(seed_groups=self.seed_groups)

    def __len__(self) -> int:
        """Return number of seed groups (objectives) added."""
        return len(self.seed_groups)
