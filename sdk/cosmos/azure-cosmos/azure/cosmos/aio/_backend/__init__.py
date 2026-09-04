# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The backend layer for the async client -- the async twin of ``azure.cosmos._backend``.

A backend is what an async ``CosmosClient`` builds once and then hands every
prepared operation to so it can go on the wire.

It has three dispatch methods, split by the shape of the reply rather than by
which resource the operation touches: ``execute`` (one request, one reply -- a
single resource, or nothing for a delete), ``execute_pages`` (one request, a
feed that comes back a page at a time), and ``execute_batch`` (one request, a
set of operations the service applies all-or-nothing). The operation kind is a
value carried on the request, not a method of its own, so the three methods
cover the whole public surface: every create/read/replace/delete of an item,
database, container, user, permission, or script is a single-reply ``execute``;
every ``list_*`` / ``query_*`` (and read-many) is an ``execute_pages`` feed; and
a transactional batch is ``execute_batch``. Adding an operation is a new
operation-kind value and a branch, not a new method.

``execute`` and ``execute_pages`` are wired according to the shared operation
tables in ``azure.cosmos._backend.operations``. ``execute_batch`` is defined but
raises ``NotImplementedError`` until transactional batch is migrated.

Two backends exist, and both are concrete ``AsyncCosmosBackend`` objects that run
through ``AsyncCosmosBackend.run_operation``. The rust backend forwards each
operation to the compiled Rust driver. Normal operations run as Rust futures on
the binding's Tokio runtime and return Python awaitables, so they do not occupy a
Python worker thread while waiting; only lazy driver initialization is moved to
a background worker. The core-python backend (``AsyncLegacyBackend``, see
``azure.cosmos.aio._backend.legacy``) awaits the SDK's original in-place code and
is still selectable on the current branch. On a Rust-selected client it also
provides temporary fallback for unmigrated request shapes. The intended final
architecture keeps only the Rust execution path.

The backend a client stores is always concrete: the factory returns an async
rust backend for rust or the shared ``AsyncLegacyBackend`` for core-python.

The package is split by job. ``base`` holds the ``AsyncCosmosBackend`` abstract
class every async backend implements. ``execute`` handles single-response
operations, ``AsyncRustBackend.execute_pages`` handles the migrated feed and
query operations, and ``execute_batch`` remains reserved until transactional
batch is migrated. The shared request and response contracts live in
``azure.cosmos._backend.contracts``.
``factory`` picks the backend once when a client is built, and ``rust`` is the
async Rust backend itself.

The operation-kind constants, the backend names, and the selection rules are
shared with the sync package ``azure.cosmos._backend`` and imported from it;
this package only adds the async-specific pieces.
"""
