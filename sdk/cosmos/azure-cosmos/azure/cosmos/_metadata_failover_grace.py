# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Caller-cancellation-shielded grace execution for cold control-plane metadata reads.

When a cold collection-metadata read (container cache warm-up) is routed at an
unhealthy preferred region, the SDK escalates through internal HTTP timeouts. If the
caller's request-level timeout / cancellation fires during that escalation, the retry
loop exits before the cross-region failover policy can route the next attempt to a
healthy region, so the customer surfaces a cancellation instead of a successful
failover.

This module provides the primitives used by the sync/async retry loops to grant ONE
bounded, cancellation-shielded cross-region attempt for such metadata reads, mirroring
the .NET ``MetadataDetachedExecutor`` (Azure/azure-cosmos-dotnet-v3#5844) and the
direction in Azure/azure-sdk-for-python#46471. The attempt runs detached from the
caller's cancellation; on success the caller receives the failover result, otherwise
the original cancellation is surfaced.
"""
import logging
import os
import threading
from typing import Any, Callable, Optional, Sequence, Tuple

from ._constants import _Constants
from .documents import _OperationType
from ._request_object import RequestObject
from .http_constants import ResourceType

logger = logging.getLogger("azure.cosmos._metadata_failover_grace")


def get_grace_seconds() -> float:
    """Resolve the bounded grace window for a metadata cross-region failover attempt.

    Reads ``AZURE_COSMOS_METADATA_FAILOVER_GRACE_SECONDS`` (default
    :attr:`_Constants.METADATA_FAILOVER_GRACE_SECONDS_DEFAULT`). A value ``<= 0``
    disables the grace window (restores the prior preempted behavior). Values are
    clamped to ``[0, METADATA_FAILOVER_GRACE_SECONDS_MAX]``. Malformed values fall
    back to the default.

    :returns: the grace window in seconds (``0`` means disabled).
    :rtype: float
    """
    raw = os.environ.get(_Constants.METADATA_FAILOVER_GRACE_SECONDS)
    if raw is None:
        value = _Constants.METADATA_FAILOVER_GRACE_SECONDS_DEFAULT
    else:
        try:
            value = float(raw)
        except (TypeError, ValueError):
            value = _Constants.METADATA_FAILOVER_GRACE_SECONDS_DEFAULT
    value = max(value, 0.0)
    value = min(value, _Constants.METADATA_FAILOVER_GRACE_SECONDS_MAX)
    return value


def is_metadata_failover_candidate(args: Sequence[Any]) -> bool:
    """Return True if the current request is a cold collection-metadata read.

    The grace attempt is intentionally scoped to read-only collection
    (``ResourceType.Collection``) reads, matching .NET which wires the detached
    executor only into the collection-cache path. Data-plane operations keep their
    existing cancellation semantics.

    :param args: the positional args passed to the retry loop; ``args[0]`` is the
        :class:`~azure.cosmos._request_object.RequestObject` when present.
    :type args: Sequence[Any]
    :returns: whether a metadata cross-region grace attempt is applicable.
    :rtype: bool
    """
    if not args:
        return False
    request = args[0]
    if not isinstance(request, RequestObject):
        return False
    resource_type = getattr(request, "resource_type", None)
    operation_type = getattr(request, "operation_type", None)
    if resource_type != ResourceType.Collection:
        return False
    if operation_type is None:
        return False
    return _OperationType.IsReadOnlyOperation(operation_type)


def run_grace_attempt_sync(
    attempt: Callable[[], Any],
    grace_seconds: float,
) -> Tuple[bool, Optional[Any], Optional[BaseException]]:
    """Run a single cross-region metadata attempt detached from caller cancellation.

    The attempt executes on a daemon thread bounded by ``grace_seconds`` so that the
    caller's cancellation cannot preempt the cross-region failover decision. The
    attempt performs exactly one request against the next preferred region (the
    request was routed synchronously by the caller before this is invoked); it does
    not re-enter the retry loop. If the grace window expires the thread is left
    running in the background (its single in-flight request completes and its
    retry-policy side-effects still benefit subsequent callers) and the caller
    surfaces the original cancellation.

    .. note::
        On grace expiry the abandoned daemon thread may still be reading the shared
        :class:`~azure.cosmos._request_object.RequestObject` while it completes its
        single in-flight send. Callers must not mutate or reuse that request object
        after the cancellation is surfaced; in practice the request belongs to the
        failed operation and is discarded once it raises.

    :param attempt: zero-arg callable performing exactly one cross-region attempt.
    :type attempt: Callable
    :param float grace_seconds: maximum time to wait for the attempt to complete.
    :returns: ``(succeeded, result, exception)``. ``succeeded`` is True only when the
        attempt completed within the grace window without raising.
    :rtype: tuple[bool, object, BaseException]
    """
    box: dict = {}

    def _runner() -> None:
        try:
            box["result"] = attempt()
            box["ok"] = True
        except BaseException as exc:  # pylint: disable=broad-except
            box["exception"] = exc
            box["ok"] = False

    thread = threading.Thread(
        target=_runner, name="cosmos-metadata-failover-grace", daemon=True)
    thread.start()
    thread.join(grace_seconds)

    if thread.is_alive():
        # Grace window expired; leave the detached attempt running in the background.
        return False, None, None
    if box.get("ok"):
        return True, box.get("result"), None
    return False, None, box.get("exception")
