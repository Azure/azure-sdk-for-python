"""Observability and identity header helpers."""

from __future__ import annotations


def build_platform_server_header(sdk_name: str, version: str, runtime: str, extra: str | None = None) -> str:
    """Build the platform server identity header value.

    :param sdk_name: SDK package name.
    :param version: SDK package version.
    :param runtime: Runtime marker, such as python/3.10.
    :param extra: Optional additional identity suffix.
    :returns: Formatted identity header value.
    """
    base_value = f"{sdk_name}/{version} ({runtime})"
    return f"{base_value} {extra}".strip() if extra else base_value
