# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Shared parsing for workload settings used by execution and reporting."""

import logging
import os


def manage_client_lifecycle(environ=None):
    """Resolve the positive setting and explicitly invert the legacy setting."""
    environ = os.environ if environ is None else environ
    current_name = "WORKLOAD_MANAGE_CLIENT_LIFECYCLE"
    legacy_name = "WORKLOAD_SKIP_CLOSE"

    def boolean(name):
        value = environ.get(name)
        if value is None:
            return None
        if value.lower() not in ("true", "false"):
            raise ValueError(f"{name} must be true or false")
        return value.lower() == "true"

    current = boolean(current_name)
    legacy = boolean(legacy_name)
    if legacy is not None:
        converted = not legacy
        if current is not None and current != converted:
            raise ValueError(f"{current_name} conflicts with {legacy_name}; their meanings are inverted")
        logging.getLogger(__name__).warning(
            "%s is deprecated; use %s=%s", legacy_name, current_name, str(converted).lower()
        )
        current = converted
    return True if current is None else current
