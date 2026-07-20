# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""ID generation utilities for deterministic response and item IDs."""

from __future__ import annotations

import base64
import secrets
from collections.abc import Mapping
from typing import Any, Sequence


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

        extracted, partition_key = IdGenerator._try_extract_partition_key_raw(
            partition_key_hint
        )
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
    def new_function_shell_call_output_item_id(
        partition_key_hint: str | None = "",
    ) -> str:
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
    def new_item_id(
        item: Mapping[str, Any], partition_key_hint: str | None = ""
    ) -> str | None:
        """Generate a type-specific ID for an item wire payload.

        Dispatches to the appropriate ``new_*_item_id`` factory method based on
        the item ``type`` discriminator. Returns ``None`` for item references or
        unrecognized payloads.

        :param item: The item wire payload to create an ID for.
        :type item: Mapping[str, Any]
        :param partition_key_hint: An existing ID from which to extract the partition key
            for co-location. Defaults to an empty string.
        :type partition_key_hint: str | None
        :returns: A new unique ID string, or None if the item type is a reference or unrecognized.
        :rtype: str | None
        """
        discriminator_dispatch = {
            "message": IdGenerator.new_message_item_id,
            "output_message": IdGenerator.new_output_message_item_id,
            "function_call": IdGenerator.new_function_call_item_id,
            "function_call_output": IdGenerator.new_function_call_output_item_id,
            "custom_tool_call": IdGenerator.new_custom_tool_call_item_id,
            "custom_tool_call_output": IdGenerator.new_custom_tool_call_output_item_id,
            "computer_call": IdGenerator.new_computer_call_item_id,
            "computer_call_output": IdGenerator.new_computer_call_output_item_id,
            "file_search_call": IdGenerator.new_file_search_call_item_id,
            "web_search_call": IdGenerator.new_web_search_call_item_id,
            "image_generation_call": IdGenerator.new_image_gen_call_item_id,
            "code_interpreter_call": IdGenerator.new_code_interpreter_call_item_id,
            "local_shell_call": IdGenerator.new_local_shell_call_item_id,
            "local_shell_call_output": IdGenerator.new_local_shell_call_output_item_id,
            "shell_call": IdGenerator.new_function_shell_call_item_id,
            "shell_call_output": IdGenerator.new_function_shell_call_output_item_id,
            "apply_patch_call": IdGenerator.new_apply_patch_call_item_id,
            "apply_patch_call_output": IdGenerator.new_apply_patch_call_output_item_id,
            "mcp_list_tools": IdGenerator.new_mcp_list_tools_item_id,
            "mcp_call": IdGenerator.new_mcp_call_item_id,
            "mcp_approval_request": IdGenerator.new_mcp_approval_request_item_id,
            "mcp_approval_response": IdGenerator.new_mcp_approval_response_item_id,
            "reasoning": IdGenerator.new_reasoning_item_id,
            "compaction": IdGenerator.new_compaction_item_id,
            "compaction_summary": IdGenerator.new_compaction_item_id,
            "structured_outputs": IdGenerator.new_structured_output_item_id,
            "tool_search_call": lambda hint: IdGenerator.new_id("ts", hint),
            "tool_search_output": lambda hint: IdGenerator.new_id("tso", hint),
            "additional_tools": lambda hint: IdGenerator.new_id("adt", hint),
            "oauth_consent_request": lambda hint: IdGenerator.new_id("oauth", hint),
            "memory_search_call": lambda hint: IdGenerator.new_id("mem", hint),
            "workflow_action": IdGenerator.new_workflow_action_item_id,
            "a2a_preview_call": lambda hint: IdGenerator.new_id("a2a", hint),
            "a2a_preview_call_output": lambda hint: IdGenerator.new_id("a2ao", hint),
            "bing_grounding_call": lambda hint: IdGenerator.new_id("bg", hint),
            "bing_grounding_call_output": lambda hint: IdGenerator.new_id("bgo", hint),
            "sharepoint_grounding_preview_call": lambda hint: IdGenerator.new_id(
                "sp", hint
            ),
            "sharepoint_grounding_preview_call_output": lambda hint: IdGenerator.new_id(
                "spo", hint
            ),
            "azure_ai_search_call": lambda hint: IdGenerator.new_id("ais", hint),
            "azure_ai_search_call_output": lambda hint: IdGenerator.new_id(
                "aiso", hint
            ),
            "bing_custom_search_preview_call": lambda hint: IdGenerator.new_id(
                "bcs", hint
            ),
            "bing_custom_search_preview_call_output": lambda hint: IdGenerator.new_id(
                "bcso", hint
            ),
            "openapi_call": lambda hint: IdGenerator.new_id("oa", hint),
            "openapi_call_output": lambda hint: IdGenerator.new_id("oao", hint),
            "browser_automation_preview_call": lambda hint: IdGenerator.new_id(
                "ba", hint
            ),
            "browser_automation_preview_call_output": lambda hint: IdGenerator.new_id(
                "bao", hint
            ),
            "fabric_dataagent_preview_call": lambda hint: IdGenerator.new_id(
                "fda", hint
            ),
            "fabric_dataagent_preview_call_output": lambda hint: IdGenerator.new_id(
                "fdao", hint
            ),
            "azure_function_call": lambda hint: IdGenerator.new_id("azf", hint),
            "azure_function_call_output": lambda hint: IdGenerator.new_id("azfo", hint),
        }
        if not isinstance(item, Mapping):
            return None
        item_type = item.get("type")
        if item_type is None and ("role" in item or "content" in item):
            item_type = "message"
        generator = discriminator_dispatch.get(str(item_type or ""))
        return generator(partition_key_hint) if generator else None

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
    def is_valid(
        id_value: str | None, allowed_prefixes: Sequence[str] | None = None
    ) -> tuple[bool, str | None]:
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
        if (
            len(body) != IdGenerator._NEW_FORMAT_BODY_LENGTH
            and len(body) != IdGenerator._LEGACY_BODY_LENGTH
        ):
            return (
                False,
                f"ID '{id_value}' has unexpected body length {len(body)}"
                + f" (expected {IdGenerator._NEW_FORMAT_BODY_LENGTH} or"
                + f" {IdGenerator._LEGACY_BODY_LENGTH}).",
            )

        if allowed_prefixes is not None and prefix not in allowed_prefixes:
            return (
                False,
                f"ID prefix '{prefix}' is not in the allowed set [{', '.join(allowed_prefixes)}].",
            )

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
