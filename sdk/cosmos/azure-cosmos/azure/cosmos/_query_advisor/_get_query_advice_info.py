# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Function for processing query advice response headers."""

from typing import Optional

from ._query_advice import QueryAdvice


def get_query_advice_info(header_value: Optional[str]) -> str:
    """Process a query advice response header into a formatted string.
    
    This function takes the raw query advice response header (URL-encoded JSON),
    decodes it, parses the query advice entries, enriches them with human-readable
    messages from the rule directory, and returns a formatted multi-line string.
    
    Args:
        header_value: The raw query advice response header value (URL-encoded JSON)
        
    Returns:
        Formatted string with query advice entries, or empty string if parsing fails
        
    Example:
        >>> header = "QA1002%3A%20Instead%20of%20CONTAINS..."
        >>> advice = get_query_advice_info(header)
        >>> print(advice)
        QA1002: Instead of CONTAINS, consider using STARTSWTIH or computed properties...
    """
    if header_value is None:
        return ""
    
    # Parse the query advice from the header
    query_advice = QueryAdvice.try_create_from_string(header_value)
    
    if query_advice is None:
        return ""
    
    # Format as string
    return query_advice.to_string()
