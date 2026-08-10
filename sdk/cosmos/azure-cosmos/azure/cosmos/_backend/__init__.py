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

Two backends exist, and both are concrete ``CosmosBackend`` objects that run
through ``CosmosBackend.run_operation``. The rust backend forwards each operation
to the compiled Rust driver; it is the path going forward and the only one meant
for production. The core-python backend (``LegacyBackend``, see
``azure.cosmos._backend.legacy``) runs the SDK's original in-place code and is
kept for testing and comparison; its ``run_operation`` just runs that original
call.

The backend a client stores is ``Optional``: the factory returns a ``RustBackend``
for rust and ``None`` for core-python. Each family coordinator (``DatabaseHelper``,
``ItemHelper``, the throughput functions, the feed-range functions) turns that selection
into a concrete backend at its own boundary -- ``None`` becomes ``LegacyBackend``
-- and then holds that one backend by interface, so no coordinator branches on
``None`` (see ``azure.cosmos._backend.legacy.coerce_backend``).

The modules here are arranged so that a caller depends only on what it actually
uses. In dependency order, lowest first:

* ``operations`` -- the ``OP_*`` operation names and the binding lookups keyed by
  them. Pure data, no imports, so a request builder or routing predicate can name
  an operation without pulling in any backend machinery.
* ``errors`` -- the errors this layer raises, and the guards that raise them.
* ``contracts`` -- the frozen request and reply objects backends exchange with
  the layer above. Shared by the sync and async backends, which is why they live
  here rather than beside either one.
* ``_binding_conversions`` -- conversions between the Rust binding's plain tuples
  and dicts and those typed objects.
* ``_fallback_metrics`` -- the process-wide count of Rust attempts that retried
  on the legacy path.
* ``base`` -- the ``CosmosBackend`` ABC itself.
* ``credentials``, ``transport_settings``, ``client_config`` -- the three
  argument-checking steps a client goes through before a Rust backend is built:
  sorting the credential, rejecting network settings the driver cannot honor,
  and gathering the tuning options into one config object. They are separate
  from ``factory`` because the async factory reuses all three. ``credentials``
  also exposes ``resolved_credential``, the context manager both factories build
  inside so a construction that fails later cannot strand the background thread
  that wrapping an async credential starts.
* ``factory``, ``rust``, ``legacy``, ``_shared``, ``_driver_registry`` -- backend
  selection and the two concrete implementations. ``_shared`` holds the state and
  the open/close steps the sync and async Rust backends have in common, so a
  lifecycle rule cannot end up enforced on only one of them.

The async versions of all of this live in ``azure.cosmos.aio._backend``, which
defines only what genuinely differs (the ``AsyncCosmosBackend`` ABC and the two
async implementations) and imports ``operations``, ``errors``, ``contracts``,
``_binding_conversions`` and ``_fallback_metrics`` from here, so the two engines
cannot drift apart on the shared vocabulary.
"""
