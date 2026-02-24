# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Query advice classes for parsing and formatting query optimization recommendations."""

import json
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from ._rule_directory import RuleDirectory


class QueryAdviceEntry:
    """Represents a single query advice entry.
    
    Each entry contains a rule ID and optional parameters that provide
    specific guidance for query optimization.
    """
    
    def __init__(self, rule_id: str, parameters: Optional[List[str]] = None) -> None:
        """Initialize a query advice entry.
        
        Args:
            rule_id: The rule identifier (e.g., "QA1000")
            parameters: Optional list of parameters for the rule message
        """
        self.id = rule_id
        self.parameters = parameters or []
    
    def to_string(self, rule_directory: RuleDirectory) -> Optional[str]:
        """Format the query advice entry as a human-readable string.
        
        Args:
            rule_directory: Rule directory instance for looking up messages
            
        Returns:
            Formatted string with rule ID, message, and documentation link,
            or None if the rule message cannot be found
        """
        if self.id is None:
            return None
        
        message = rule_directory.get_rule_message(self.id)
        if message is None:
            return None
        
        # Format: {id}: {message}. For more information, please visit {url_prefix}{id}
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
        
        Args:
            data: Dictionary with "Id" and optional "Params" keys
            
        Returns:
            QueryAdviceEntry instance
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
        
        Args:
            entries: List of QueryAdviceEntry objects
        """
        self.entries = [e for e in (entries or []) if e is not None]
    
    def to_string(self) -> str:
        """Format all query advice entries as a multi-line string.
        
        Returns:
            Formatted string with each entry on a separate line
        """
        if not self.entries:
            return ""
        
        rule_directory = RuleDirectory()
        lines = []
        
        for entry in self.entries:
            formatted = entry.to_string(rule_directory)
            if formatted:
                lines.append(formatted)
        
        return "\n".join(lines)
    
    @classmethod
    def try_create_from_string(cls, response_header: Optional[str]) -> Optional["QueryAdvice"]:
        """Parse query advice from a URL-encoded JSON response header.
        
        Args:
            response_header: URL-encoded JSON string from the response header
            
        Returns:
            QueryAdvice instance if parsing succeeds, None otherwise
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
        except (json.JSONDecodeError, ValueError, AttributeError):
            return None
