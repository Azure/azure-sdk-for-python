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

Today only ``execute`` is wired, and only for the point item operations;
``execute_pages`` and ``execute_batch`` are defined but raise
``NotImplementedError`` until the feed and batch operations are added.

Two backends exist. The rust backend forwards each operation to the compiled
Rust driver, running that blocking call on a worker thread so the event loop
stays free; it is the path going forward and the only one meant for production.
The core-python choice is represented by having no backend at all, which falls
back to the legacy in-place code and is kept only for testing and comparison.

The package is split by job. ``base`` holds the ``AsyncCosmosBackend`` abstract
class every async backend implements -- ``execute`` is awaited (the one
implemented today), while the reserved ``execute_pages`` (an async iterator of
pages) and ``execute_batch`` raise ``NotImplementedError`` until the feed and
batch operations are added -- and re-exports the ``PreparedRequest`` /
``BackendResponse`` data classes (plus the reserved ``PreparedQuery`` /
``QueryPage`` / ``PreparedBatch`` / ``BatchResponse``).
``factory`` picks the backend once when a client is built, and ``rust`` is the
async Rust backend itself.

The operation-kind constants, the backend names, and the selection rules are
shared with the sync package ``azure.cosmos._backend`` and imported from it;
this package only adds the async-specific pieces.
"""

