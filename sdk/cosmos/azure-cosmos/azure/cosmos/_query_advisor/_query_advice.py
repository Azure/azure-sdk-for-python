# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Query advice classes for parsing and formatting query optimization recommendations."""

import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from ._rule_directory import RuleDirectory

_LOGGER = logging.getLogger(__name__)


class QueryAdviceEntry:
    """Represents a single query advice entry.
    
    Each entry contains a rule ID and optional parameters that provide
    specific guidance for query optimization.
    """

    def __init__(self, rule_id: str, parameters: Optional[List[str]] = None) -> None:
        """Initialize a query advice entry.

        :param str rule_id: The rule identifier (e.g., ``QA1000``).
        :param parameters: Optional list of parameters for the rule message.
        :type parameters: list[str] or None
        """
        self.id = rule_id
        self.parameters = parameters or []

    def __str__(self) -> str:
        """Format the query advice entry as a human-readable string.

        :returns: Formatted string with rule ID, message, and documentation link,
            or empty string if the rule identifier is missing.
        :rtype: str
        """
        if self.id is None:
            return ""

        rule_directory = RuleDirectory()
        message = rule_directory.get_rule_message(self.id)
        if message is None:
            # Unknown rule — log it and return the public doc link as the fallback.
            fallback_url = f"{rule_directory.url_prefix}{self.id}"
            _LOGGER.warning(
                "Unknown Query Advisor rule '%s'. For more information, please visit %s",
                self.id,
                fallback_url,
            )
            return f"{self.id}: For more information, please visit {fallback_url}"

        # Format: {id}: {message} For more information, please visit {url_prefix}{id}
        result = f"{self.id}: "

        # Format message with parameters if available
        if self.parameters:
            try:
                result += message.format(*self.parameters)
            except (IndexError, KeyError):
                # If formatting fails, use message as-is
                result += message
        else:
            result += message

        # Add documentation link
        result += f" For more information, please visit {rule_directory.url_prefix}{self.id}"

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QueryAdviceEntry":
        """Create a QueryAdviceEntry from a dictionary.

        :param data: Dictionary with "Id" and optional "Params" keys.
        :type data: dict[str, any]
        :returns: QueryAdviceEntry instance.
        :rtype: ~azure.cosmos._query_advisor._query_advice.QueryAdviceEntry
        """
        rule_id = data.get("Id", "")
        parameters = data.get("Params", [])
        return cls(rule_id, parameters)


class QueryAdvice:
    """Collection of query advice entries.
    
    Represents the complete query advice response from Azure Cosmos DB,
    containing one or more optimization recommendations.
    """

    def __init__(self, entries: Optional[List[QueryAdviceEntry]] = None) -> None:
        """Initialize query advice with a list of entries.

        :param entries: List of QueryAdviceEntry objects.
        :type entries: list[~azure.cosmos._query_advisor._query_advice.QueryAdviceEntry] or None
        """
        self.entries = [e for e in (entries or []) if e is not None]

    def __str__(self) -> str:
        """Format all query advice entries as a multi-line string.

        :returns: Formatted string with each entry on a separate line.
        :rtype: str
        """
        if not self.entries:
            return ""

        lines = []

        for entry in self.entries:
            formatted = str(entry)
            if formatted:
                lines.append(formatted)

        return "\n".join(lines)

    @classmethod
    def try_create_from_string(cls, response_header: Optional[str]) -> Optional["QueryAdvice"]:
        """Parse query advice from a URL-encoded JSON response header.

        :param response_header: URL-encoded JSON string from the response header.
        :type response_header: str or None
        :returns: QueryAdvice instance if parsing succeeds, None otherwise.
        :rtype: ~azure.cosmos._query_advisor._query_advice.QueryAdvice or None
        """
        if response_header is None:
            return None

        try:
            # URL-decode the header value
            decoded_string = unquote(response_header)

            # Parse JSON into list of entry dictionaries
            data = json.loads(decoded_string)

            if not isinstance(data, list):
                return None

            # Convert dictionaries to QueryAdviceEntry objects
            entries = [QueryAdviceEntry.from_dict(item) for item in data if isinstance(item, dict)]

            return cls(entries)
        except (json.JSONDecodeError, ValueError, AttributeError) as e:
            _LOGGER.warning("Failed to parse query advice from response header: %s", e)
            return None
