# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The backend layer: the object that actually sends an operation on the wire.

A backend is what a ``CosmosClient`` builds once and then hands every prepared
operation to so it can go on the wire.

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

``execute`` is wired for the point item operations and the feed-range / offer
operations; ``execute_pages`` is wired for ``query_items`` / ``read_all_items``.
``execute_batch`` is defined but raises ``NotImplementedError`` until the batch
operation is added.

Two backends exist. The rust backend forwards each operation to the compiled
Rust driver; it is the path going forward and the only one meant for production.
The core-python choice runs the SDK's legacy in-place code, kept for testing and
comparison. It is now an explicit backend -- ``LegacyBackend`` (see
``azure.cosmos._backend.legacy``) -- so every family coordinator (the item
helper, and the throughput / feed-range coordinators) holds one backend by
interface and never reads ``None`` as "call legacy": both backends run through
``CosmosBackend.run_operation`` and the legacy one just runs the original call.
The stored client selection is still ``Optional`` (the factory returns ``None``
for core-python); each coordinator coerces that ``None`` to ``LegacyBackend`` at
its own boundary (see ``azure.cosmos._backend.legacy.coerce_backend``).

The async versions of all of this live in ``azure.cosmos.aio._backend``.
"""

