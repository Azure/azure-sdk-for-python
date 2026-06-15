# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The backend layer: the object that actually sends a point operation.

A backend is what a ``CosmosClient`` builds once and then hands every prepared
point operation (create, read, upsert, replace, delete, patch item) to so it
can go on the wire. Two exist. The rust backend forwards each operation to the
compiled Rust driver; it is the path going forward and the only one meant for
production. The core-python choice is represented by having no backend at all:
the factory returns ``None`` and the SDK runs its legacy in-place code instead,
kept only for testing and comparison.

The package is split by job. ``base`` holds the ``CosmosBackend`` abstract class
every backend implements -- its one method, ``execute``, takes a prepared
operation and sends it -- plus the frozen ``PreparedRequest`` and
``BackendResponse`` data classes and the operation-kind constants. ``factory``
picks the backend once when a client is built, preferring the ``_backend=``
constructor kwarg, then the ``COSMOS_BACKEND`` environment variable, then the
default of core-python. ``constants`` holds the backend names, and ``rust`` is
the Rust backend itself.

The async versions of all of this live in ``azure.cosmos.aio._backend``.
"""

