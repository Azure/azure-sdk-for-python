# Durable State Store Guide

`FoundryStateStore` is a durable, server-backed state-store client for agent
state. It gives your agent an explicit store resource plus single-item
operations over that store.

## Overview

`FoundryStateStore` is **bound to one caller-chosen store name**. That store
name is the main scoping tool for your data:

- Use one store per conversation/thread when you need conversation isolation.
- Use `user_isolation=True` when the store name is shared across many users and
  the platform should partition items per user.
- Set `item_ttl_seconds` once at store creation when you want idle items to
  age out automatically.

The SDK is the developer-facing layer over the internal `/storage/state_stores/*`
protocol: it keeps the transport/auth pipeline in `FoundryStorageClient`, while
`FoundryStateStore` owns the ergonomic store-bound API.

## Typed Models

Every request and response body is a real, typed model class -- generated
from a formal TypeSpec contract (`type_spec/main.tsp`), not a raw `dict`.
Import them from `azure.ai.agentserver.core.storage` when you want explicit
type annotations or IDE/type-checker support:

| Returned by | Model |
|---|---|
| `get_or_create()`, `get()` (no `key`), `update()` | `StateStore` |
| `delete()` (no `key`) | `DeletedStateStore` |
| `create_item()`, `set()` | `StateStoreItemMetadata` |
| `get(key)` | `StateStoreItem` |
| `delete(key)` | `DeletedStateStoreItem` |
| `list_keys()` | `KeyPage` (of `StateStoreKey`) |

The one deliberately **untyped** field is `StateStoreItem.value` /
`CreateItemRequest.value` / `PutItemRequest.value` -- your item payload is
opaque application JSON, so the SDK does not (and cannot) impose a schema on
it beyond "JSON object". Serialize your own models to a plain `dict` before
writing, and deserialize the returned `dict` back into your own model on
read.

```python
from azure.ai.agentserver.core.storage import StateStore, StateStoreItem

store_info: StateStore | None = await store.get()
item: StateStoreItem | None = await store.get("step-1")
```

### Accepted request options

Every write method that takes more than one optional keyword also accepts an
`options` keyword: a typed request model bundling those keywords into one
object, as an alternative to passing them individually. The two are mutually
exclusive per call.

| Method | Scattered keywords | `options=` |
|---|---|---|
| `get_or_create()` / constructor | `user_isolation`, `item_ttl_seconds`, `description`, `tags` | `CreateStateStoreRequest` |
| `update()` | `description`, `tags` | `UpdateStateStoreRequest` |
| `create_item()` | `tags` | `CreateItemRequest` (only `.tags` is read; `key`/`value` always come from `create_item()`'s own parameters) |
| `set()` | `tags` | `PutItemRequest` (only `.tags` is read; `key`/`value` always come from `set()`'s own parameters) |

```python
from azure.ai.agentserver.core.storage import CreateStateStoreRequest

store = await FoundryStateStore.get_or_create(
    "checkpoints/thread-abc",
    options=CreateStateStoreRequest(
        user_isolation=True,
        item_ttl_seconds=3600,
        description="Checkpoint store for thread abc",
    ),
)
```

For `update()`, build `options` via `UpdateStateStoreRequest`'s *mapping*
constructor (a `dict`), not its keyword constructor, if you need to clear a
field: a key's *absence* means "leave unchanged", a key present with a
`None` value means "clear it" -- the same distinction the `description` /
`tags` keywords make via omission vs. an explicit `None`.

```python
from azure.ai.agentserver.core.storage import UpdateStateStoreRequest

# Clears tags, leaves description unchanged (it is absent from the mapping).
await store.update(options=UpdateStateStoreRequest({"tags": None}))
```

## Getting Started

`get_or_create()` is the recommended entry point: it resolves (or creates) the
store's server-side resource in one call, so there is no separate lifecycle
step before reading or writing items.

```python
from azure.ai.agentserver.core.storage import FoundryStateStore, StateStoreItem

store = await FoundryStateStore.get_or_create(
    "checkpoints/thread-abc",
    user_isolation=True,
    item_ttl_seconds=3600,
    description="Checkpoint store for thread abc",
)
async with store:
    await store.set("step-1", {"done": False})

    item: StateStoreItem | None = await store.get("step-1")
    assert item is not None
    print(item.value)  # {"done": False}
    print(item.etag)
```

By default, the client resolves:

- `FOUNDRY_PROJECT_ENDPOINT` for the project endpoint
- `DefaultAzureCredential` for authentication (requires `azure-identity`)

## Store Name = Scope

The protocol has no built-in session-isolation knob. If you want conversation
or thread scoping, encode it directly into the store name:

```python
await FoundryStateStore.get_or_create("checkpoints/thread-abc")
await FoundryStateStore.get_or_create("workflow-state/run-42")
await FoundryStateStore.get_or_create("user-prefs/defaults", user_isolation=True)
```

Because the store name is the logical identity, choose a stable naming scheme
up front. The raw name may contain `/`; the SDK handles the required base64url
path encoding on the wire.

## Store Lifecycle

Stores are **explicit resources**, but `get_or_create()` is the only lifecycle
call you need for the common case:

```python
store = await FoundryStateStore.get_or_create(
    "checkpoints/thread-abc",
    user_isolation=True,
    item_ttl_seconds=3600,
)
print(store.name)
```

`get()` and `delete()` are overloaded on whether you pass a `key`: with no
`key` they act on the bound store itself; with a `key` they act on one item.

```python
info: StateStore | None = await store.get()          # the store's own descriptor, or None if absent
info = await store.update(
    description="Checkpoint store for prod traffic",
    tags={"env": "prod", "team": "agents"},
)

deleted = await store.delete()    # deletes the store, cascading to every item
assert deleted.deleted is True
```

### Key points

- `get_or_create()` fetches the store first, or creates it when it is absent
  (falling back to a fetch if another caller created it in the meantime). It
  does not update `user_isolation`, `item_ttl_seconds`, `description`, or
  `tags` on a store that already exists -- those are only applied on first
  creation.
- `update()` only changes `description` and `tags`.
- `user_isolation` and `item_ttl_seconds` are fixed at create time.
- `delete()` with no `key` cascades to every item under that store name.

## User Isolation and the Delegated User Header

Set `user_isolation=True` when the same store name should fan out per user.

```python
store = await FoundryStateStore.get_or_create("user-prefs/defaults", user_isolation=True)
```

- For direct callers, the platform derives user identity from the token.
- For trusted callers acting on behalf of an end user, the SDK sends the
  delegated `x-ms-user-id` header on item operations automatically, resolved
  **per request** from `azure.ai.agentserver.core.get_request_context().user_id`
  -- the same request-scoped platform context every protocol host already
  populates from the inbound `x-agent-user-id` header. There is nothing to
  configure on `FoundryStateStore` itself: a client instance can safely serve
  requests for different users over its lifetime.
- Store-management calls (`get_or_create`, `get()` with no key, `update()`,
  `delete()` with no key) stay store-scoped and never send the delegated user
  header.

## Values, Tags, and TTL

Each item value is a JSON **object**. Store plain JSON, not Python objects.

```python
await store.create_item(
    "step-1",
    {"done": False, "attempt": 1},
    tags={"kind": "checkpoint"},
)
```

Tags are simple string labels used only for filtering `list_keys()`.

TTL is **store-level**, not per-item:

```python
store = await FoundryStateStore.get_or_create("otp/user-42", item_ttl_seconds=300)
```

- Default: `30 days`
- `-1`: never expire
- Any item write renews the TTL window for that item
- Reads do **not** renew the TTL window

## Single-Item Operations

### Create a new item

```python
created = await store.create_item(
    "step-1",
    {"done": False},
    tags={"kind": "checkpoint"},
)
print(created.etag)
```

Use `create_item()` when duplicate keys should fail with `409`.

### Create-or-replace

```python
updated = await store.set(
    "step-1",
    {"done": True},
    tags={"kind": "checkpoint"},
)
print(updated.etag)
```

`set()` maps to the protocol's single-item `PUT`: create-or-replace by key.

### Fetch one item

```python
item: StateStoreItem | None = await store.get("step-1")
if item is not None:
    print(item.id, item.key, item.value, item.tags, item.etag)
```

`get(key)` returns `None` when the item is missing; `get()` with no `key`
returns the store's own descriptor instead (or `None` if the store is absent).

### Delete one item

```python
deleted = await store.delete("step-1")
assert deleted.deleted is True
```

Deletes are idempotent.

## Optimistic Concurrency

Use `if_match` when you want a guarded update or delete:

```python
from azure.ai.agentserver.core.storage import FoundryStoragePreconditionError

item = await store.get("counter")
assert item is not None

try:
    await store.set("counter", {"value": item.value["value"] + 1}, if_match=item.etag)
except FoundryStoragePreconditionError as err:
    print("Current etag:", err.current_etag)
```

If you want a strict update that only succeeds when the item already exists, use
`require_exists=True`:

```python
await store.set("counter", {"value": 2}, require_exists=True)
```

## Listing Keys

`list_keys()` returns a keys-only page within the bound store.

```python
from azure.ai.agentserver.core.storage import KeyPage

page: KeyPage = await store.list_keys(tags={"kind": "checkpoint"}, limit=50, order="asc")
for key in page.keys:
    print(key.id, key.key, key.tags, key.etag)

while page.has_more and page.last_id is not None:
    page = await store.list_keys(
        tags={"kind": "checkpoint"},
        after=page.last_id,
        limit=50,
        order="asc",
    )
```

Use:

- `tags={...}` for AND-filtered tag matching
- `limit` for page size
- `after` / `before` for cursor paging by item id
- `order="desc"` (default) or `"asc"`

## Error Handling

All storage errors derive from `FoundryStorageError`.

| Exception | HTTP | Meaning |
|---|---|---|
| `FoundryStoragePreconditionError` | 412 | `If-Match` failed; `current_etag` may be populated. |
| `FoundryStorageNotFoundError` | 404 | Store or resource path not found. |
| `FoundryStorageConflictError` | 409 | A `create`/`create_item` duplicated an existing name/key. |
| `FoundryStorageBadRequestError` | 400 | Invalid request; `param` names the offending field. |
| `FoundryStorageApiError` | other 4xx/5xx | Server-side failure. |

```python
from azure.ai.agentserver.core.storage import (
    FoundryStorageError,
    FoundryStoragePreconditionError,
)

try:
    await store.set("step-1", {"done": True}, if_match='"stale"')
except FoundryStoragePreconditionError as err:
    print(err.current_etag)
except FoundryStorageError as err:
    print(err.message, err.response_body)
```

## Limits

All request-body and query fields are bounded server-side; a violating request
is rejected with `400 Bad Request` (`error.param` names the offending field).

**Store (`get_or_create`, `update`):**

| Field | Constraints | Mutability |
|-------|-------------|------------|
| `name` | 1-128 chars. Unicode; may contain `/` as a hierarchy separator. Unique within the project + agent. | Immutable |
| `user_isolation` | Boolean. Omitted -> `false` (agent-level, shared). | Immutable (fixed at first creation) |
| `item_ttl_seconds` | Default `2592000` (30 days); `-1` = never expire; else `1`-`2147483647`. Write-sliding per item (renews on write, not read). | Immutable (fixed at first creation) |
| `description` | <= 1024 chars. Free-form. | Mutable via `update()` |
| `tags` | <= 16 entries. Key: 1-64 chars, `[a-zA-Z0-9_.-]`. Value: <= 256 chars. Replaced wholesale. | Mutable via `update()` |

**Item (`create_item`, `set`):**

| Field | Constraints | Mutability |
|-------|-------------|------------|
| `key` | 1-128 chars. Unicode; may contain `/`. Unique within the store. | Immutable |
| `value` | Opaque JSON object, <= 1 MB serialized inline. | Mutable via `set()` (replace) |
| `tags` | <= 16 entries, same shape as store tags. | Mutable via `set()` (replace) |

Items carry no TTL of their own -- expiry is inherited from the store's
`item_ttl_seconds`.

**Query parameters (`list_keys`):**

| Parameter | Constraints |
|-----------|-------------|
| `limit` | 1-100. Default `20`. |
| `order` | `"asc"` or `"desc"`. Default `"desc"`. |
| `after` / `before` | Opaque cursor; mutually exclusive. |

## Best Practices

1. **Prefer `get_or_create()`.** It is the only lifecycle call you need for the
   common case; do not assume item writes will create the store for you.
2. **Encode conversation scope in the store name.** There is no separate
   session-isolation knob.
3. **Use `user_isolation=True` only when needed.** Prefer a stable store naming
   scheme first, then add per-user partitioning when the store name is shared.
4. **Use `if_match` for read-modify-write flows.** Counters and checkpoints are
   race-prone without it.
5. **Keep values as JSON objects.** Serialize your own models explicitly.
6. **Reuse the client.** It owns an HTTP pipeline; construct it once (via
   `get_or_create()`) and close it with `async with` or `await store.aclose()`.

