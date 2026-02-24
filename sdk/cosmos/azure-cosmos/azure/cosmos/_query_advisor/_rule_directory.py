# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Rule directory singleton for loading and accessing query advice rules."""

import json
import os
from typing import Any, Dict, Optional


class RuleDirectory:
    """Singleton for loading and accessing query advice rules.
    
    The rule directory lazy-loads the query_advice_rules.json file
    and provides access to rule messages and URL prefix.
    """
    
    _instance: Optional["RuleDirectory"] = None
    
    def __new__(cls) -> "RuleDirectory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
            
        self._initialized = True
        self._rules: Dict[str, Dict[str, Any]] = {}
        self._url_prefix: str = ""
        self._load_rules()
    
    def _load_rules(self) -> None:
        """Load rules from the JSON file."""
        try:
            rules_file = os.path.join(os.path.dirname(__file__), "query_advice_rules.json")
            with open(rules_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._url_prefix = data.get("url_prefix", "")
                self._rules = data.get("rules", {})
        except (IOError, json.JSONDecodeError):
            # If we can't load rules, use empty defaults
            self._url_prefix = "https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/query/queryadvisor/"
            self._rules = {}
    
    @property
    def url_prefix(self) -> str:
        """Get the URL prefix for documentation links."""
        return self._url_prefix
    
    def get_rule_message(self, rule_id: str) -> Optional[str]:
        """Get the message for a given rule ID.
        
        Args:
            rule_id: The rule identifier (e.g., "QA1000")
            
        Returns:
            The rule message, or None if the rule is not found
        """
        rule = self._rules.get(rule_id)
        if rule:
            return rule.get("message")
        return None
