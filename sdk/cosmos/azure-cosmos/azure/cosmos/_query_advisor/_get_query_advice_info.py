# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Function for processing query advice response headers."""

from typing import Optional

from ._query_advice import QueryAdvice

def get_query_advice_info(header_value: Optional[str]) -> str:
    """Process a query advice response header into a formatted human-readable string.

    Takes the raw ``x-ms-cosmos-query-advice`` response header (URL-encoded JSON),
    decodes it, parses the query advice entries, enriches them with human-readable
    messages from the rule directory, and returns a formatted multi-line string.

    :param str header_value: The raw query advice response header value (URL-encoded JSON).
    :returns: Formatted string with query advice entries, or empty string if parsing fails.
    :rtype: str
    """
    if header_value is None:
        return ""

    # Parse the query advice from the header
    query_advice = QueryAdvice.try_create_from_string(header_value)

    if query_advice is None:
        return ""

    # Format as string
    return str(query_advice)
