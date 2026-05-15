# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Query Advisor module for processing query optimization advice from Azure Cosmos DB."""

from ._query_advice import QueryAdvice, QueryAdviceEntry
from ._rule_directory import RuleDirectory
from ._get_query_advice_info import get_query_advice_info

__all__ = [
    "QueryAdvice",
    "QueryAdviceEntry",
    "RuleDirectory",
    "get_query_advice_info",
]
