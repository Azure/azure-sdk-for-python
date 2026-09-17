# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Connection-string parsing shared by the sync and async clients."""


def parse_connection_string(conn_str: str) -> dict[str, str]:
    """Read account settings without creating a client or exposing key values in errors."""
    if not isinstance(conn_str, str):
        raise TypeError("Connection string must be a string.")

    settings: dict[str, str] = {}
    for setting in conn_str.rstrip(";").split(";"):
        name, separator, value = setting.partition("=")
        if not separator:
            raise ValueError(
                "Connection string settings must use 'name=value' format, separated by semicolons."
            )
        # Keep the last occurrence of a setting, matching existing parsing behavior.
        settings[name] = value

    for name in ("AccountEndpoint", "AccountKey"):
        if name not in settings:
            raise ValueError(f"Connection string missing setting '{name}'.")
    for name in ("AccountEndpoint", "AccountKey"):
        if not settings[name].strip():
            raise ValueError(f"Connection string setting '{name}' must not be empty.")
    return settings
