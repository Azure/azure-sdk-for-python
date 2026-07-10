# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""ID generation utilities for deterministic response and item IDs."""

from __future__ import annotations

import base64
import secrets
from typing import Callable, Sequence

from .models import _generated as generated_models


class IdGenerator:  # pylint: disable=too-many-public-methods
    """Generates IDs with embedded partition keys."""

    _PARTITION_KEY_HEX_LENGTH = 16
    _PARTITION_KEY_SUFFIX = "00"
    _PARTITION_KEY_TOTAL_LENGTH = _PARTITION_KEY_HEX_LENGTH + 2
    _ENTROPY_LENGTH = 32
    _NEW_FORMAT_BODY_LENGTH = _PARTITION_KEY_TOTAL_LENGTH + _ENTROPY_LENGTH
    _LEGACY_BODY_LENGTH = 48
    _LEGACY_PARTITION_KEY_LENGTH = 16

    @staticmethod
    def new_id(prefix: str, partition_key_hint: str | None = "") -> str:
        """Generate a new ID in the format ``{prefix}_{partitionKey}{entropy}``.

        :param prefix: The prefix segment for the ID (e.g. ``"caresp"``, ``"msg"``).
        :type prefix: str
        :param partition_key_hint: An existing ID from which to extract a partition key
            for co-location. Defaults to an empty string (generates a new partition key).
        :type partition_key_hint: str | None
        :returns: A new unique ID string.
        :rtype: str
        :raises TypeError: If *prefix* is None.
        :raises ValueError: If *prefix* is empty.
        """
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
        """Generate a new response ID with the ``caresp`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique response ID string.
        :rtype: str
        """
        return IdGenerator.new_id("caresp", partition_key_hint)

    @staticmethod
    def new_message_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new message item ID with the ``msg`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique message item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("msg", partition_key_hint)

    @staticmethod
    def new_function_call_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new function call item ID with the ``fc`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique function call item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("fc", partition_key_hint)

    @staticmethod
    def new_reasoning_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new reasoning item ID with the ``rs`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique reasoning item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("rs", partition_key_hint)

    @staticmethod
    def new_file_search_call_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new file search call item ID with the ``fs`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique file search call item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("fs", partition_key_hint)

    @staticmethod
    def new_web_search_call_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new web search call item ID with the ``ws`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique web search call item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("ws", partition_key_hint)

    @staticmethod
    def new_code_interpreter_call_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new code interpreter call item ID with the ``ci`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique code interpreter call item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("ci", partition_key_hint)

    @staticmethod
    def new_image_gen_call_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new image generation call item ID with the ``ig`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique image generation call item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("ig", partition_key_hint)

    @staticmethod
    def new_mcp_call_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new MCP call item ID with the ``mcp`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique MCP call item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("mcp", partition_key_hint)

    @staticmethod
    def new_mcp_list_tools_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new MCP list tools item ID with the ``mcpl`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique MCP list tools item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("mcpl", partition_key_hint)

    @staticmethod
    def new_custom_tool_call_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new custom tool call item ID with the ``ctc`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique custom tool call item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("ctc", partition_key_hint)

    @staticmethod
    def new_custom_tool_call_output_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new custom tool call output item ID with the ``ctco`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique custom tool call output item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("ctco", partition_key_hint)

    @staticmethod
    def new_function_call_output_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new function call output item ID with the ``fco`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique function call output item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("fco", partition_key_hint)

    @staticmethod
    def new_computer_call_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new computer call item ID with the ``cu`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique computer call item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("cu", partition_key_hint)

    @staticmethod
    def new_computer_call_output_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new computer call output item ID with the ``cuo`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique computer call output item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("cuo", partition_key_hint)

    @staticmethod
    def new_local_shell_call_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new local shell call item ID with the ``lsh`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique local shell call item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("lsh", partition_key_hint)

    @staticmethod
    def new_local_shell_call_output_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new local shell call output item ID with the ``lsho`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique local shell call output item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("lsho", partition_key_hint)

    @staticmethod
    def new_function_shell_call_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new function shell call item ID with the ``lsh`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique function shell call item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("lsh", partition_key_hint)

    @staticmethod
    def new_function_shell_call_output_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new function shell call output item ID with the ``lsho`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique function shell call output item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("lsho", partition_key_hint)

    @staticmethod
    def new_apply_patch_call_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new apply patch call item ID with the ``ap`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique apply patch call item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("ap", partition_key_hint)

    @staticmethod
    def new_apply_patch_call_output_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new apply patch call output item ID with the ``apo`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique apply patch call output item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("apo", partition_key_hint)

    @staticmethod
    def new_mcp_approval_request_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new MCP approval request item ID with the ``mcpr`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique MCP approval request item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("mcpr", partition_key_hint)

    @staticmethod
    def new_mcp_approval_response_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new MCP approval response item ID with the ``mcpa`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique MCP approval response item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("mcpa", partition_key_hint)

    @staticmethod
    def new_compaction_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new compaction item ID with the ``cmp`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique compaction item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("cmp", partition_key_hint)

    @staticmethod
    def new_workflow_action_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new workflow action item ID with the ``wfa`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique workflow action item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("wfa", partition_key_hint)

    @staticmethod
    def new_structured_output_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new structured output item ID with the ``fco`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique structured output item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("fco", partition_key_hint)

    @staticmethod
    def new_output_message_item_id(partition_key_hint: str | None = "") -> str:
        """Generate a new output message item ID with the ``om`` prefix.

        :param partition_key_hint: An existing ID to extract the partition key from for co-location.
        :type partition_key_hint: str | None
        :returns: A new unique output message item ID string.
        :rtype: str
        """
        return IdGenerator.new_id("om", partition_key_hint)

    @staticmethod
    def new_item_id(item: generated_models.Item, partition_key_hint: str | None = "") -> str | None:
        """Generate a type-specific ID for a generated Item subtype.

        Dispatches to the appropriate ``new_*_item_id`` factory method based on the
        runtime type of *item*. Returns None for ``ItemReferenceParam`` or unrecognized types.

        :param item: The generated Item instance to create an ID for.
        :type item: generated_models.Item
        :param partition_key_hint: An existing ID from which to extract the partition key
            for co-location. Defaults to an empty string.
        :type partition_key_hint: str | None
        :returns: A new unique ID string, or None if the item type is a reference or unrecognized.
        :rtype: str | None
        """
        dispatch_map: tuple[tuple[type[object], Callable[..., str]], ...] = (
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
            (generated_models.StructuredOutputsOutputItem, IdGenerator.new_structured_output_item_id),
        )

        for model_type, generator in dispatch_map:
            if isinstance(item, model_type):
                return generator(partition_key_hint)

        if isinstance(item, generated_models.ItemReferenceParam):
            return None
        return None

    @staticmethod
    def extract_partition_key(id_value: str) -> str:
        """Extract the partition key segment from an existing ID.

        :param id_value: The full ID string to extract the partition key from.
        :type id_value: str
        :returns: The partition key hex string.
        :rtype: str
        :raises ValueError: If the ID is null, empty, missing a delimiter, or has
            an unexpected body length.
        """
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
        """Validate whether an ID string conforms to the expected format.

        :param id_value: The ID string to validate.
        :type id_value: str | None
        :param allowed_prefixes: An optional sequence of allowed prefix strings.
            When provided, the ID's prefix must be in this set.
        :type allowed_prefixes: Sequence[str] | None
        :returns: A tuple of (is_valid, error_message). When valid, error_message is None.
        :rtype: tuple[bool, str | None]
        """
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
                f"ID '{id_value}' has unexpected body length {len(body)}"
                + f" (expected {IdGenerator._NEW_FORMAT_BODY_LENGTH} or"
                + f" {IdGenerator._LEGACY_BODY_LENGTH}).",
            )

        if allowed_prefixes is not None and prefix not in allowed_prefixes:
            return False, f"ID prefix '{prefix}' is not in the allowed set [{', '.join(allowed_prefixes)}]."

        return True, None

    @staticmethod
    def _generate_partition_key() -> str:
        """Generate a random partition key hex string with the standard suffix.

        :returns: An 18-character hex partition key string.
        :rtype: str
        """
        return f"{secrets.token_bytes(8).hex()}{IdGenerator._PARTITION_KEY_SUFFIX}"

    @staticmethod
    def _generate_entropy() -> str:
        """Generate a random alphanumeric entropy string.

        :returns: A 32-character alphanumeric entropy string.
        :rtype: str
        """
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
        """Attempt to extract the raw partition key from an ID string.

        Supports both the new format (18-char partition key at the start of the body)
        and the legacy format (16-char partition key at the end of the body).

        :param id_value: The full ID string to parse.
        :type id_value: str | None
        :returns: A tuple of (success, partition_key). On failure, partition_key is
            an empty string.
        :rtype: tuple[bool, str]
        """
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
