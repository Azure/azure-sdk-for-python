# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The backend layer for the async client -- the async twin of ``azure.cosmos._backend``.

A backend is what an async ``CosmosClient`` builds once and then hands every
prepared operation to so it can go on the wire. Today that means the six point
operations (create, read, upsert, replace, delete, patch item); the backend also
reserves seams for the query/read-many and transactional-batch operations
(``execute_pages``, ``execute_batch``), defined but raising
``NotImplementedError`` until they are wired. Two exist. The rust
backend forwards each operation to the compiled Rust driver, running that
blocking call on a worker thread so the event loop stays free; it is the path
going forward and the only one meant for production. The core-python choice is
represented by having no backend at all, which falls back to the legacy in-place
code and is kept only for testing and comparison.

The package is split by job. ``base`` holds the ``AsyncCosmosBackend`` abstract
class every async backend implements -- ``execute`` is awaited (the one
implemented today), while the reserved ``execute_pages`` (an async iterator of
pages) and ``execute_batch`` raise ``NotImplementedError`` until the query and
batch operations are added -- and re-exports the ``PreparedRequest`` /
``BackendResponse`` data classes (plus the reserved ``PreparedQuery`` /
``QueryPage`` / ``PreparedBatch`` / ``BatchResponse``).
``factory`` picks the backend once when a client is built, and ``rust`` is the
async Rust backend itself.

The operation-kind constants, the backend names, and the selection rules are
shared with the sync package ``azure.cosmos._backend`` and imported from it;
this package only adds the async-specific pieces.
"""

