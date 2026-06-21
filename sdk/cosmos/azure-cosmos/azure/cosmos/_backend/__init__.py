# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The backend layer: the object that actually sends an operation on the wire.

A backend is what a ``CosmosClient`` builds once and then hands every prepared
operation to so it can go on the wire. Today that means the six point operations
(create, read, upsert, replace, delete, patch item) via ``execute``; the backend
also reserves seams for the query/read-many and transactional-batch operations
(``execute_pages``, ``execute_batch``), which are defined but raise
``NotImplementedError`` until they are wired. Two exist. The rust backend forwards each operation to the
compiled Rust driver; it is the path going forward and the only one meant for
production. The core-python choice is represented by having no backend at all:
the factory returns ``None`` and the SDK runs its legacy in-place code instead,
kept only for testing and comparison.

The package is split by job. ``base`` holds the ``CosmosBackend`` abstract class
every backend implements -- its three dispatch methods are ``execute`` (the one
implemented today) plus the reserved ``execute_pages`` and ``execute_batch``,
which raise ``NotImplementedError`` until the query and batch operations are
added -- plus the frozen ``PreparedRequest`` / ``BackendResponse`` data classes
(and the reserved ``PreparedQuery`` / ``QueryPage`` / ``PreparedBatch`` /
``BatchResponse``) and the operation-kind constants. ``factory``
picks the backend once when a client is built, preferring the ``_backend=``
constructor kwarg, then the ``COSMOS_BACKEND`` environment variable, then the
default of core-python. ``constants`` holds the backend names, and ``rust`` is
the Rust backend itself.

The async versions of all of this live in ``azure.cosmos.aio._backend``.
"""

