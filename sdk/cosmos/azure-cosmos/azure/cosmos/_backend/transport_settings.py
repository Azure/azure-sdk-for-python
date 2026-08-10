# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Network and TLS settings: what the Rust path rejects, and the timeouts it reads.

The Rust driver brings its own HTTP and TLS stack, so the transport knobs the
legacy pipeline honors -- a custom proxy object, a CA bundle, a client
certificate, disabled certificate verification, a stand-in transport -- have
nowhere to go on the Rust path. Silently ignoring them is the dangerous option:
a customer would believe their proxy or certificate was in effect when it was
not. :func:`reject_unsupported_transport_settings` therefore raises at client
construction if any of them were passed.

Two transport settings *do* carry across, because they are plain numbers rather
than objects: the connection and read timeouts.
:func:`resolve_client_transport_timeouts` reads that pair from the constructor
keyword arguments without consuming them, so the legacy client still receives the
same values it always did.

It reports only the timeouts the customer actually asked for, and ``None`` for the
ones they left alone. That distinction matters because these two timeouts are not
per-client on the Rust path: they configure the process-wide driver runtime, which
is built once by whichever client operates first and then frozen. Reporting the
legacy default as though the customer had chosen it would pin the whole process to
it, so a perfectly ordinary program -- one untuned client plus one client that asks
for a shorter connect timeout -- would fail to construct its second client. ``None``
means "no opinion": the driver keeps its own default and never conflicts with a
client that does express one.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Tuple

from ..documents import ConnectionPolicy

# Transport / TLS knobs the legacy pipeline honors but the Rust path still cannot
# accept as explicit objects -- it owns its own HTTP stack. Each maps to a
# constructor kwarg the legacy path
# consumes (``proxy_config`` / ``ssl_config`` via ``_build_connection_policy``;
# ``proxies`` / ``transport`` via the connection; ``connection_verify`` /
# ``connection_cert`` for TLS). On the Rust path they are rejected at construction
# rather than silently ignored and left to fail later with opaque certificate or
# connection errors far from the call site.
def reject_unsupported_transport_settings(
    *,
    proxy_config: Any = None,
    proxies: Any = None,
    connection_verify: Any = None,
    connection_cert: Any = None,
    ssl_config: Any = None,
    transport: Any = None,
) -> None:
    """Raise ``ValueError`` if any transport/TLS setting the Rust path can't honor
    was passed; do nothing when none were (the common case).

    The Rust driver owns its own network/TLS stack, so it can't accept custom
    proxy objects, a custom CA bundle, a client certificate, disabled TLS
    verification, or a stand-in transport. Without this: those settings would be
    silently ignored, and the customer would think their proxy/cert was in effect
    when it wasn't -- a security-relevant surprise. So it raises if any were
    passed.

    It is careful to let the defaults through so a normal client isn't wrongly
    rejected: ``connection_verify`` defaults to ``True``/absent (ordinary
    verification, which the driver already does) and only a custom CA bundle path
    (a ``str``) or an explicit ``False`` (disable verification) is unsupported;
    an empty ``proxies`` dict is "no proxy". Every other setting is rejected when it
    is present (non-``None``).
    """
    def _fail(setting: str, detail: str) -> None:
        """Raise a customer-facing error for one unsupported setting."""
        raise ValueError(
            "_backend='rust' cannot honor {setting}= yet: {detail}. The Rust "
            "driver owns its own HTTP/TLS stack. Remove the setting (for proxy, "
            "use proxy_allowed= with environment variables), or use the "
            "core-python backend.".format(
                setting=setting, detail=detail
            )
        )

    if proxy_config is not None:
        _fail("proxy_config", "the Rust driver has no explicit proxy-config object hook")
    if proxies:
        _fail("proxies", "the Rust driver has no explicit proxy-config object hook")
    # connection_verify defaults to True/None (verify) -- only a custom CA path or
    # an explicit disable is unsupported.
    if connection_verify is False:
        _fail(
            "connection_verify",
            "disabling TLS verification is not supported on the Rust path",
        )
    if isinstance(connection_verify, str):
        _fail(
            "connection_verify",
            "a custom CA bundle path is not supported on the Rust path",
        )
    if connection_cert is not None:
        _fail(
            "connection_cert",
            "presenting a client certificate is not supported on the Rust path",
        )
    if ssl_config is not None:
        _fail("ssl_config", "custom SSL configuration is not supported on the Rust path")
    if transport is not None:
        _fail(
            "transport",
            "a custom/stand-in transport is not supported on the Rust path",
        )


def resolve_client_transport_timeouts(kwargs: Mapping[str, Any]) -> Tuple[Any, Any]:
    """Return the connection and read timeouts the customer explicitly chose, using
    ``None`` for either one they did not.

    Reads ``kwargs`` without consuming it, so the legacy client still receives the
    same values it always did. ``request_timeout`` is the older millisecond alias
    for ``connection_timeout`` and therefore keeps precedence. A ``connection_policy``
    counts as an explicit choice only where it actually differs from a stock
    :class:`ConnectionPolicy`, since the public clients construct a default policy
    for every client whether or not the customer asked for one.

    Returning ``None`` for an untouched timeout is the whole point: these two values
    configure the process-wide Rust driver runtime, so any value reported here is
    pinned for every later client in the process. Only a value the customer actually
    asked for should carry that weight.
    """
    stock_policy = ConnectionPolicy()
    policy = kwargs.get("connection_policy") or stock_policy
    if "request_timeout" in kwargs:
        connection_timeout = kwargs["request_timeout"] / 1000.0
    elif "connection_timeout" in kwargs:
        connection_timeout = kwargs["connection_timeout"]
    elif policy.RequestTimeout != stock_policy.RequestTimeout:
        connection_timeout = policy.RequestTimeout
    else:
        connection_timeout = None
    if "read_timeout" in kwargs:
        read_timeout = kwargs["read_timeout"]
    elif policy.ReadTimeout != stock_policy.ReadTimeout:
        read_timeout = policy.ReadTimeout
    else:
        read_timeout = None
    return connection_timeout, read_timeout
