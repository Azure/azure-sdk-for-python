# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Result processor for converting Foundry scenario results to JSONL format."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pyrit.models.attack_result import AttackOutcome, AttackResult
from pyrit.scenario.core.dataset_configuration import DatasetConfiguration


class FoundryResultProcessor:
    """Processes Foundry scenario results into JSONL format.

    Extracts AttackResult objects from the completed Foundry scenario and
    converts them to the JSONL format expected by the main ResultProcessor.
    This ensures compatibility with existing result processing and reporting
    infrastructure.
    """

    def __init__(
        self,
        scenario,
        dataset_config: DatasetConfiguration,
        risk_category: str,
    ):
        """Initialize the processor.

        :param scenario: Completed Foundry scenario (ScenarioOrchestrator)
        :type scenario: ScenarioOrchestrator
        :param dataset_config: DatasetConfiguration used for the scenario
        :type dataset_config: DatasetConfiguration
        :param risk_category: The risk category being processed
        :type risk_category: str
        """
        self.scenario = scenario
        self.dataset_config = dataset_config
        self.risk_category = risk_category
        self._context_lookup: Dict[str, Dict[str, Any]] = {}
        self._build_context_lookup()

    def _build_context_lookup(self) -> None:
        """Build lookup from prompt_group_id (UUID) to context data."""
        for seed_group in self.dataset_config.get_all_seed_groups():
            if not seed_group.seeds:
                continue

            # Get prompt_group_id from first seed
            group_id = seed_group.seeds[0].prompt_group_id
            if not group_id:
                continue

            # Find objective and context seeds
            objective_seed = None
            context_seeds = []

            for seed in seed_group.seeds:
                seed_class = seed.__class__.__name__
                if seed_class == "SeedObjective":
                    objective_seed = seed
                elif seed_class == "SeedPrompt":
                    context_seeds.append(seed)

            if objective_seed:
                # Extract context data
                contexts = []
                for ctx_seed in context_seeds:
                    metadata = ctx_seed.metadata or {}

                    # For XPIA, include the injected vehicle
                    if metadata.get("is_attack_vehicle"):
                        contexts.append({
                            "content": ctx_seed.value,
                            "tool_name": metadata.get("tool_name"),
                            "context_type": metadata.get("context_type"),
                            "is_attack_vehicle": True,
                        })
                    elif not metadata.get("is_original_context"):
                        # Standard context
                        contexts.append({
                            "content": ctx_seed.value,
                            "tool_name": metadata.get("tool_name"),
                            "context_type": metadata.get("context_type"),
                        })

                self._context_lookup[str(group_id)] = {
                    "contexts": contexts,
                    "metadata": objective_seed.metadata or {},
                    "objective": objective_seed.value,
                }

    def to_jsonl(self, output_path: str) -> str:
        """Convert scenario results to JSONL format.

        :param output_path: Path to write JSONL file
        :type output_path: str
        :return: JSONL content string
        :rtype: str
        """
        # Get attack results from scenario
        attack_results = self.scenario.get_attack_results()

        # Get memory instance for querying conversations
        memory = self.scenario.get_memory()

        jsonl_lines = []

        # Process each AttackResult
        for attack_result in attack_results:
            entry = self._process_attack_result(attack_result, memory)
            if entry:
                jsonl_lines.append(json.dumps(entry, ensure_ascii=False))

        # Write to file
        jsonl_content = "\n".join(jsonl_lines)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(jsonl_content)

        return jsonl_content

    def _process_attack_result(
        self,
        attack_result: AttackResult,
        memory,
    ) -> Optional[Dict[str, Any]]:
        """Process a single AttackResult into JSONL entry format.

        :param attack_result: The attack result to process
        :type attack_result: AttackResult
        :param memory: Memory interface for conversation lookup
        :type memory: MemoryInterface
        :return: JSONL entry dictionary or None if processing fails
        :rtype: Optional[Dict[str, Any]]
        """
        try:
            # Get conversation messages for this result
            conversation_pieces = memory.get_message_pieces(
                conversation_id=attack_result.conversation_id
            )

            # Extract prompt_group_id from conversation metadata
            group_id = self._get_prompt_group_id_from_conversation(conversation_pieces)

            # Lookup context and metadata
            context_data = self._context_lookup.get(str(group_id), {}) if group_id else {}

            # Build conversation structure (matching existing format)
            messages = self._build_messages_from_pieces(conversation_pieces)

            conversation = {
                "messages": messages,
            }

            # Build JSONL entry (matching format expected by ResultProcessor)
            entry: Dict[str, Any] = {
                "conversation": conversation,
            }

            # Add context if available
            contexts = context_data.get("contexts", [])
            if contexts:
                entry["context"] = json.dumps({"contexts": contexts})

            # Add risk_sub_type if present in metadata
            metadata = context_data.get("metadata", {})
            if metadata.get("risk_subtype"):
                entry["risk_sub_type"] = metadata["risk_subtype"]

            # Add attack success based on outcome
            if attack_result.outcome == AttackOutcome.SUCCESS:
                entry["attack_success"] = True
            elif attack_result.outcome == AttackOutcome.FAILURE:
                entry["attack_success"] = False
            # UNDETERMINED leaves attack_success unset

            # Add strategy information
            attack_identifier = attack_result.attack_identifier or {}
            entry["attack_strategy"] = attack_identifier.get("__type__", "Unknown")

            # Add score information if available
            if attack_result.last_score:
                score = attack_result.last_score
                entry["score"] = {
                    "value": score.score_value,
                    "rationale": score.score_rationale,
                    "metadata": score.score_metadata,
                }

            return entry

        except Exception as e:
            # Log error but don't fail entire processing
            return {
                "conversation": {"messages": []},
                "error": str(e),
                "conversation_id": attack_result.conversation_id,
            }

    def _get_prompt_group_id_from_conversation(
        self,
        conversation_pieces: List,
    ) -> Optional[str]:
        """Extract prompt_group_id from conversation pieces.

        :param conversation_pieces: List of message pieces from conversation
        :type conversation_pieces: List
        :return: prompt_group_id string or None
        :rtype: Optional[str]
        """
        for piece in conversation_pieces:
            if hasattr(piece, "prompt_metadata") and piece.prompt_metadata:
                group_id = piece.prompt_metadata.get("prompt_group_id")
                if group_id:
                    return str(group_id)

            # Also check labels
            if hasattr(piece, "labels") and piece.labels:
                group_id = piece.labels.get("prompt_group_id")
                if group_id:
                    return str(group_id)

        return None

    def _build_messages_from_pieces(
        self,
        conversation_pieces: List,
    ) -> List[Dict[str, Any]]:
        """Build message list from conversation pieces.

        :param conversation_pieces: List of message pieces
        :type conversation_pieces: List
        :return: List of message dictionaries
        :rtype: List[Dict[str, Any]]
        """
        messages = []

        # Sort by sequence if available
        sorted_pieces = sorted(
            conversation_pieces,
            key=lambda p: getattr(p, "sequence", 0)
        )

        for piece in sorted_pieces:
            # Get role, handling api_role property
            role = getattr(piece, "api_role", None) or getattr(piece, "role", "user")

            # Get content (prefer converted_value over original_value)
            content = getattr(piece, "converted_value", None) or getattr(piece, "original_value", "")

            message: Dict[str, Any] = {
                "role": role,
                "content": content,
            }

            # Add context from labels if present (for XPIA)
            if hasattr(piece, "labels") and piece.labels:
                context_str = piece.labels.get("context")
                if context_str:
                    try:
                        context_dict = json.loads(context_str) if isinstance(context_str, str) else context_str
                        if isinstance(context_dict, dict) and "contexts" in context_dict:
                            message["context"] = context_dict["contexts"]
                    except (json.JSONDecodeError, TypeError):
                        pass

            messages.append(message)

        return messages

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics from the scenario results.

        :return: Dictionary with ASR and other metrics
        :rtype: Dict[str, Any]
        """
        attack_results = self.scenario.get_attack_results()

        if not attack_results:
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "undetermined": 0,
                "asr": 0.0,
            }

        successful = sum(1 for r in attack_results if r.outcome == AttackOutcome.SUCCESS)
        failed = sum(1 for r in attack_results if r.outcome == AttackOutcome.FAILURE)
        undetermined = sum(1 for r in attack_results if r.outcome == AttackOutcome.UNDETERMINED)
        total = len(attack_results)

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "undetermined": undetermined,
            "asr": successful / total if total > 0 else 0.0,
        }
