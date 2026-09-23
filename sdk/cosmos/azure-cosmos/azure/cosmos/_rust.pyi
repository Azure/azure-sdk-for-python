# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Describe selected binding exports for Python type checking.

The compiled extension supplies the implementation; these declarations do not
run the operations. _ItemFeedCursor is the binding's feed cursor, not a Python
page iterator. Other binding exports remain typed as Any through __getattr__.
"""

from typing import Any

def _validate_runtime_configuration(config: Any = None) -> None:
    """Check requested CosmosDriverRuntime settings without initializing it.

    A completed initialization failure is raised. Successful validation does
    not reserve settings; driver acquisition checks them again.
    """
    ...

class _ItemFeedCursor:
    """Retain progress between page fetches made through the binding."""

    def __init__(self) -> None:
        """Create an empty feed cursor without acquiring a driver handle or fetching a page."""
        ...
    @property
    def has_more(self) -> bool:
        """Report whether the cursor's recorded progress indicates more results.

        A new cursor starts with False; that does not establish that the feed
        is empty before its first fetch.
        """
        ...
    @property
    def continuation_supported(self) -> bool:
        """Return False if the cursor has marked continuation tokens as unsupported.

        False does not mean iteration is finished. A new cursor starts with
        True, before a query plan has established whether a token is available.
        """
        ...
    @property
    def can_retry_setup(self) -> bool:
        """Report whether setup has not started execution and the cursor is not busy.

        The Python wrapper also checks the error before allowing a later retry;
        this flag alone does not make timeouts or cancellation retryable.
        """
        ...

def __getattr__(name: str) -> Any:
    """Allow other export names during type checking, not guarantee their runtime presence."""
    ...
