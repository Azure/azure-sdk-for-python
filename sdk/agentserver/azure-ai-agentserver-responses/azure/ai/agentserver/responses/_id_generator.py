# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""ID generation utilities aligned with the .NET IdGenerator implementation."""

from __future__ import annotations

import base64
import secrets
from typing import Sequence

from .models import _generated as generated_models


class IdGenerator:
    """Generates IDs with embedded partition keys matching the .NET format."""

    _PARTITION_KEY_HEX_LENGTH = 16
    _PARTITION_KEY_SUFFIX = "00"
    _PARTITION_KEY_TOTAL_LENGTH = _PARTITION_KEY_HEX_LENGTH + 2
    _ENTROPY_LENGTH = 32
    _NEW_FORMAT_BODY_LENGTH = _PARTITION_KEY_TOTAL_LENGTH + _ENTROPY_LENGTH
    _LEGACY_BODY_LENGTH = 48
    _LEGACY_PARTITION_KEY_LENGTH = 16

    @staticmethod
    def new_id(prefix: str, partition_key_hint: str | None = "") -> str:
        """Generate a new ID in the format ``{prefix}_{partitionKey}{entropy}``."""
        if prefix is None:
            raise TypeError("prefix must not be None")
        if len(prefix) == 0:
            raise ValueError("Prefix must not be empty.")

        extracted, partition_key = IdGenerator._try_extract_partition_key_raw(partition_key_hint)
        if extracted:
            if len(partition_key) == IdGenerator._LEGACY_PARTITION_KEY_LENGTH:
                partition_key = partition_key + IdGenerator._PARTITION_KEY_SUFFIX
        else:
            partition_key = IdGenerator._generate_partition_key()

        entropy = IdGenerator._generate_entropy()
        return f"{prefix}_{partition_key}{entropy}"

    @staticmethod
    def new_response_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("caresp", partition_key_hint)

    @staticmethod
    def new_message_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("msg", partition_key_hint)

    @staticmethod
    def new_function_call_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("fc", partition_key_hint)

    @staticmethod
    def new_reasoning_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("rs", partition_key_hint)

    @staticmethod
    def new_file_search_call_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("fs", partition_key_hint)

    @staticmethod
    def new_web_search_call_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("ws", partition_key_hint)

    @staticmethod
    def new_code_interpreter_call_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("ci", partition_key_hint)

    @staticmethod
    def new_image_gen_call_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("ig", partition_key_hint)

    @staticmethod
    def new_mcp_call_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("mcp", partition_key_hint)

    @staticmethod
    def new_mcp_list_tools_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("mcpl", partition_key_hint)

    @staticmethod
    def new_custom_tool_call_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("ctc", partition_key_hint)

    @staticmethod
    def new_custom_tool_call_output_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("ctco", partition_key_hint)

    @staticmethod
    def new_function_call_output_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("fco", partition_key_hint)

    @staticmethod
    def new_computer_call_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("cu", partition_key_hint)

    @staticmethod
    def new_computer_call_output_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("cuo", partition_key_hint)

    @staticmethod
    def new_local_shell_call_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("lsh", partition_key_hint)

    @staticmethod
    def new_local_shell_call_output_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("lsho", partition_key_hint)

    @staticmethod
    def new_function_shell_call_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("lsh", partition_key_hint)

    @staticmethod
    def new_function_shell_call_output_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("lsho", partition_key_hint)

    @staticmethod
    def new_apply_patch_call_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("ap", partition_key_hint)

    @staticmethod
    def new_apply_patch_call_output_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("apo", partition_key_hint)

    @staticmethod
    def new_mcp_approval_request_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("mcpr", partition_key_hint)

    @staticmethod
    def new_mcp_approval_response_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("mcpa", partition_key_hint)

    @staticmethod
    def new_compaction_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("cmp", partition_key_hint)

    @staticmethod
    def new_workflow_action_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("wfa", partition_key_hint)

    @staticmethod
    def new_output_message_item_id(partition_key_hint: str | None = "") -> str:
        return IdGenerator.new_id("om", partition_key_hint)

    @staticmethod
    def new_item_id(item: generated_models.Item, partition_key_hint: str | None = "") -> str | None:
        """Generate a type-specific ID for a generated Item subtype."""
        dispatch_map: tuple[tuple[type[object], callable], ...] = (
            (generated_models.ItemMessage, IdGenerator.new_message_item_id),
            (generated_models.ItemOutputMessage, IdGenerator.new_output_message_item_id),
            (generated_models.ItemFunctionToolCall, IdGenerator.new_function_call_item_id),
            (generated_models.FunctionCallOutputItemParam, IdGenerator.new_function_call_output_item_id),
            (generated_models.ItemCustomToolCall, IdGenerator.new_custom_tool_call_item_id),
            (generated_models.ItemCustomToolCallOutput, IdGenerator.new_custom_tool_call_output_item_id),
            (generated_models.ItemComputerToolCall, IdGenerator.new_computer_call_item_id),
            (generated_models.ComputerCallOutputItemParam, IdGenerator.new_computer_call_output_item_id),
            (generated_models.ItemFileSearchToolCall, IdGenerator.new_file_search_call_item_id),
            (generated_models.ItemWebSearchToolCall, IdGenerator.new_web_search_call_item_id),
            (generated_models.ItemImageGenToolCall, IdGenerator.new_image_gen_call_item_id),
            (generated_models.ItemCodeInterpreterToolCall, IdGenerator.new_code_interpreter_call_item_id),
            (generated_models.ItemLocalShellToolCall, IdGenerator.new_local_shell_call_item_id),
            (generated_models.ItemLocalShellToolCallOutput, IdGenerator.new_local_shell_call_output_item_id),
            (generated_models.FunctionShellCallItemParam, IdGenerator.new_function_shell_call_item_id),
            (generated_models.FunctionShellCallOutputItemParam, IdGenerator.new_function_shell_call_output_item_id),
            (generated_models.ApplyPatchToolCallItemParam, IdGenerator.new_apply_patch_call_item_id),
            (generated_models.ApplyPatchToolCallOutputItemParam, IdGenerator.new_apply_patch_call_output_item_id),
            (generated_models.ItemMcpListTools, IdGenerator.new_mcp_list_tools_item_id),
            (generated_models.ItemMcpToolCall, IdGenerator.new_mcp_call_item_id),
            (generated_models.ItemMcpApprovalRequest, IdGenerator.new_mcp_approval_request_item_id),
            (generated_models.MCPApprovalResponse, IdGenerator.new_mcp_approval_response_item_id),
            (generated_models.ItemReasoningItem, IdGenerator.new_reasoning_item_id),
            (generated_models.CompactionSummaryItemParam, IdGenerator.new_compaction_item_id),
        )

        for model_type, generator in dispatch_map:
            if isinstance(item, model_type):
                return generator(partition_key_hint)

        if isinstance(item, generated_models.ItemReferenceParam):
            return None
        return None

    @staticmethod
    def extract_partition_key(id_value: str) -> str:
        extracted, partition_key = IdGenerator._try_extract_partition_key_raw(id_value)
        if extracted:
            return partition_key

        if id_value is None or id_value == "":
            raise ValueError("ID must not be null or empty.")
        if "_" not in id_value:
            raise ValueError(f"ID '{id_value}' has no '_' delimiter.")
        raise ValueError(f"ID '{id_value}' has unexpected body length.")

    @staticmethod
    def is_valid(id_value: str | None, allowed_prefixes: Sequence[str] | None = None) -> tuple[bool, str | None]:
        if id_value is None or id_value == "":
            return False, "ID must not be null or empty."

        delimiter_index = id_value.find("_")
        if delimiter_index < 0:
            return False, f"ID '{id_value}' has no '_' delimiter."

        prefix = id_value[:delimiter_index]
        if len(prefix) == 0:
            return False, "ID has an empty prefix."

        body = id_value[delimiter_index + 1 :]
        if len(body) != IdGenerator._NEW_FORMAT_BODY_LENGTH and len(body) != IdGenerator._LEGACY_BODY_LENGTH:
            return (
                False,
                f"ID '{id_value}' has unexpected body length {len(body)} (expected {IdGenerator._NEW_FORMAT_BODY_LENGTH} or {IdGenerator._LEGACY_BODY_LENGTH}).",
            )

        if allowed_prefixes is not None and prefix not in allowed_prefixes:
            return False, f"ID prefix '{prefix}' is not in the allowed set [{', '.join(allowed_prefixes)}]."

        return True, None

    @staticmethod
    def _generate_partition_key() -> str:
        return f"{secrets.token_bytes(8).hex()}{IdGenerator._PARTITION_KEY_SUFFIX}"

    @staticmethod
    def _generate_entropy() -> str:
        chars: list[str] = []
        while len(chars) < IdGenerator._ENTROPY_LENGTH:
            base64_text = base64.b64encode(secrets.token_bytes(48)).decode("ascii")
            for char in base64_text:
                if char.isalnum():
                    chars.append(char)
                    if len(chars) >= IdGenerator._ENTROPY_LENGTH:
                        break
        return "".join(chars)

    @staticmethod
    def _try_extract_partition_key_raw(id_value: str | None) -> tuple[bool, str]:
        if id_value is None or id_value == "":
            return False, ""

        delimiter_index = id_value.find("_")
        if delimiter_index < 0:
            return False, ""

        body = id_value[delimiter_index + 1 :]
        if len(body) == IdGenerator._NEW_FORMAT_BODY_LENGTH:
            return True, body[: IdGenerator._PARTITION_KEY_TOTAL_LENGTH]

        if len(body) == IdGenerator._LEGACY_BODY_LENGTH:
            return True, body[-IdGenerator._LEGACY_PARTITION_KEY_LENGTH :]

        return False, ""
