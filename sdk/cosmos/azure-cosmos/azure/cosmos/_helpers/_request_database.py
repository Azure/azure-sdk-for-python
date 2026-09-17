# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Build prepared requests for the database operations.

Covers create, read and delete of a database, plus the checks that decide
whether a given call can run on the Rust path at all. A database is
account-scoped, so these requests carry no partition key and no container link.

The eligibility predicates are here rather than beside the caller because they
encode the same knowledge the builders do: exactly which per-call arguments and
headers the Rust path can honour for these operations, and therefore when a call
must fail rather than silently dropping a setting or falling back to legacy.
"""
from __future__ import annotations

from .._backend.partition_key import PartitionKeyInput

from typing import Any, Dict, Mapping, Optional

from .._backend.contracts import PreparedRequest
from .._backend.operations import OP_CREATE_DATABASE, OP_DELETE_DATABASE, OP_READ_DATABASE
from .._base import _validate_resource
from .._constants import _Constants as Constants

from ._request_settings import (
    account_request_settings,
    _timeout_is_representable,
    is_supported_operation_timeout,
    overrides_driver_owned_header,
)
from ._wire_encoding import serialize_body_to_bytes


# The only per-call keyword arguments a database read can carry onto the Rust
# path. ``timeout`` becomes the normalized ``timeout_seconds`` request option;
# ``response_hook`` is invoked by the coordinator after the response is parsed,
# so it never has to reach the binding. Anything else -- ``connection_timeout``,
# ``raw_request_hook``, ``raw_response_hook`` -- is consumed by the legacy
# azure-core pipeline, which the Rust path does not run, so its presence rejects
# the Rust read instead of dropping it (see
# ``is_read_database_rust_eligible``).
_RUST_READ_DATABASE_SUPPORTED_KWARGS = frozenset({
    Constants.Kwargs.TIMEOUT,
    "response_hook",
})


def build_create_database_prepared(
    database: Dict[str, Any],
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build the account-level create-database request consumed by the Rust backend."""
    _validate_resource(database)
    headers, settings = account_request_settings(request_options, kwargs)
    return PreparedRequest(
        op=OP_CREATE_DATABASE,
        container_link="",
        body_bytes=serialize_body_to_bytes(database),
        partition_key=PartitionKeyInput("cross_partition"),
        headers=headers,
        settings=settings,
        item_id=database["id"],
    )


def build_read_database_prepared(
    database_id: Any,
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build the account-level read-database request consumed by the Rust backend.

    Two callers: ``DatabaseProxy.read`` and the existence check inside
    ``create_database_if_not_exists``. Without it a Rust-backed client has to
    run both of those on the legacy transport, because there is no Rust request
    to send.
    """
    read_options = dict(request_options)
    # Database reads are master-resource requests. The legacy session layer never
    # attaches a session token to them (``_base._is_session_token_request`` returns
    # False for a master resource), and ``_base.GetHeaders`` suppresses
    # x-ms-cosmos-intended-collection-rid when resource_type == 'dbs'. Drop both so
    # the Rust request carries the same headers the legacy request would.
    read_options.pop("sessionToken", None)
    read_options.pop(Constants.ContainerRID, None)
    normalized_database_id = str(database_id).rstrip("/")
    if not normalized_database_id:
        # Match the legacy link parser instead of sending an account-level
        # ``/dbs/`` request that fails later with a different service error.
        raise ValueError("Failed Parsing ResourceID from link: /dbs/")
    headers, settings = account_request_settings(read_options, kwargs)
    return PreparedRequest(
        op=OP_READ_DATABASE,
        container_link="",
        body_bytes=b"",
        partition_key=PartitionKeyInput("cross_partition"),
        headers=headers,
        settings=settings,
        # The legacy path routes the id through ``base.GetPathFromLink`` /
        # ``GetResourceIdOrFullNameFromLink``, which tolerate a trailing slash
        # ("dbs/mydb/" reads database "mydb"). The binding takes the bare name and
        # builds the path itself, so strip the slash here to keep the two paths
        # reading the same database.
        item_id=normalized_database_id,
    )


def is_read_database_rust_eligible(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> bool:
    """Return whether Rust can honor every per-call option on a database read.

    The single definition of "representable" for a database read, shared by
    ``DatabaseProxy.read`` and the existence check in
    ``create_database_if_not_exists``. Both ask the same question, so they must
    not answer it differently: the same call would otherwise run on Rust in one
    method and on legacy Python in the other, honoring a different set of the
    caller's options each time.

    Returns ``False`` when the caller asked for
    something the Rust path would drop without saying so:

    * ``read_timeout`` -- a socket-level timeout. The Rust path has no
      per-request equivalent; the driver takes its read timeout from the client
      configuration.
    * any operation kwarg outside ``_RUST_READ_DATABASE_SUPPORTED_KWARGS`` --
      for example ``connection_timeout`` or ``raw_request_hook``, which the
      legacy azure-core pipeline consumes and the Rust path never sees.
    * a ``timeout`` that is not a finite, non-boolean numeric duration of at least
      one second within Rust's duration range.
    * ``initial_headers`` containing a standard header the driver always
      overwrites. The legacy pipeline preserves those caller overrides.

    Without this check the read would run on Rust regardless, and these options
    would be accepted and then quietly not applied. A customer who
    sets ``timeout=0.5`` to fail fast would wait a full second and have no way to
    tell from logs that their number was replaced.

    :param request_options: The internal options dict for this read.
    :type request_options: Mapping[str, Any]
    :param operation_kwargs: The kwargs left over after ``build_options``.
    :type operation_kwargs: Mapping[str, Any]
    :returns: ``True`` when the Rust path preserves every option the caller set.
    :rtype: bool
    """
    timeout = operation_kwargs.get(Constants.Kwargs.TIMEOUT)
    option_timeout = request_options.get(Constants.Kwargs.TIMEOUT)
    # The prepared request forwards kwargs, not a timeout supplied only in options.
    if option_timeout is not None and option_timeout != timeout:
        return False
    return _database_request_options_are_supported(request_options, operation_kwargs) and (
        is_supported_operation_timeout(timeout)
    )


def _database_request_options_are_supported(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> bool:
    if (
        request_options.get(Constants.Kwargs.READ_TIMEOUT) is not None
        or operation_kwargs.get(Constants.Kwargs.READ_TIMEOUT) is not None
    ):
        return False
    if set(operation_kwargs).difference(_RUST_READ_DATABASE_SUPPORTED_KWARGS):
        return False
    if overrides_driver_owned_header(request_options):
        return False
    return True


def build_delete_database_prepared(
    database_link: Any,
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build the Rust request that deletes a database."""
    delete_options = dict(request_options)
    # Same suppression as the read: a database is a master resource, so the legacy
    # session layer attaches no session token and ``_base.GetHeaders`` drops
    # x-ms-cosmos-intended-collection-rid when resource_type == 'dbs'.
    delete_options.pop("sessionToken", None)
    delete_options.pop(Constants.ContainerRID, None)
    database_id = _database_id_from_link(database_link)
    headers, settings = account_request_settings(delete_options, kwargs)
    return PreparedRequest(
        op=OP_DELETE_DATABASE,
        container_link="",
        body_bytes=b"",
        partition_key=PartitionKeyInput("cross_partition"),
        headers=headers,
        settings=settings,
        item_id=database_id,
    )


def _database_id_from_link(database_link: Any) -> str:
    """Return the database name from a ``dbs/{id}`` link."""
    normalized = str(database_link).strip("/")
    if not normalized.startswith("dbs/"):
        # Every caller reaches this through ``_get_database_link``, which always
        # emits ``dbs/{id}``. Anything else -- including a bare ``dbs`` -- means the
        # id is missing, so refuse rather than deleting a database named "dbs".
        raise ValueError("Failed Parsing ResourceID from link: /{}/".format(normalized))
    normalized = normalized[len("dbs/"):].strip("/")
    if not normalized:
        raise ValueError("Failed Parsing ResourceID from link: /dbs/")
    return normalized


def is_delete_database_rust_eligible(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> bool:
    """Keep deletion's existing deadline policy while sharing option checks."""
    return _database_request_options_are_supported(request_options, operation_kwargs) and (
        _timeout_is_representable(operation_kwargs)
    )
