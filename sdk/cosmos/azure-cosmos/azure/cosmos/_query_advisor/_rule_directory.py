# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Rule directory singleton for loading and accessing query advice rules."""

import json
import logging
from importlib.resources import files
from typing import Any, Dict, Optional

_LOGGER = logging.getLogger(__name__)


class RuleDirectory:
    """Singleton for loading and accessing query advice rules.

    The rule directory lazy-loads the query_advice_rules.json file
    and provides access to rule messages and URL prefix.
    Uses importlib.resources so it works correctly in all packaging
    scenarios including zip-safe wheels.
    """

    _instance: Optional["RuleDirectory"] = None

    def __new__(cls) -> "RuleDirectory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Guard so the singleton body only runs once.
        if getattr(self, "_initialized", False):
            return

        self._initialized: bool = True
        self._rules: Dict[str, Dict[str, Any]] = {}
        self._url_prefix: str = ""
        self._load_rules()

    def _load_rules(self) -> None:
        """Load rules from the bundled JSON resource."""
        try:
            resource_text = (
                files(__package__)
                .joinpath("query_advice_rules.json")
                .read_text(encoding="utf-8")
            )
            data = json.loads(resource_text)
            self._url_prefix = data.get("url_prefix", "")
            self._rules = data.get("rules", {})
        except Exception:  # pylint: disable=broad-except
            # Fall back to empty rules so query execution
            # is never blocked by an inability to load advice text.
            _LOGGER.warning("Failed to load query_advice_rules.json, falling back to empty rules", exc_info=True)
            self._url_prefix = (
                "https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/query/queryadvisor/"
            )
            self._rules = {}

    @property
    def url_prefix(self) -> str:
        """Get the URL prefix for documentation links.

        :rtype: str
        """
        return self._url_prefix

    def get_rule_message(self, rule_id: str) -> Optional[str]:
        """Get the message for a given rule ID.

        :param str rule_id: The rule identifier (e.g., ``QA1000``).
        :returns: The rule message, or ``None`` if the rule is not found.
        :rtype: str or None
        """
        rule = self._rules.get(rule_id)
        if rule:
            return rule.get("message")
        return None
