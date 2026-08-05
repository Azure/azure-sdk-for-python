# Durable State Store Guide

`FoundryStateStore` is a durable, server-backed store for agent state. Each
store holds JSON items that you read, write, and list by key.

## Overview

`FoundryStateStore` is **bound to one caller-chosen store name**. That store
name is the main scoping tool for your data:

- Use one store per conversation/thread when you need conversation isolation.
- Use `user_isolation=True` when the store name is shared across many users and
  the platform should partition items per user.
- Set `item_ttl_seconds` once at store creation when you want idle items to
  age out automatically.

## Typed Models

Every request and response is a typed model class, so you get IDE completion
and type-checker support. Import them from
`azure.ai.agentserver.core.storage`:

| Returned by | Model |
|---|---|
| `get_or_create()` | `FoundryStateStore` (bound client) |
| `get()`, `update()` | `StateStore` |
| `delete()` | `DeletedStateStore` |
| `create_item()`, `set_item()` | `StateStoreItemRef` |
| `get_item(key)` | `StateStoreItem` |
| `delete_item(key)` | `DeletedStateStoreItem` |
| `list_keys()` | `StateStoreItemKeyPage` (of `StateStoreItemKey`) |

Item values (`StateStoreItem.value`) are your own application JSON. Pass a
plain `dict` when writing and read one back on `get_item()`; the SDK stores and
returns the value as-is.

```python
from azure.ai.agentserver.core.storage import StateStore, StateStoreItem

store_info: StateStore = await store.get()
item: StateStoreItem | None = await store.get_item("step-1")
```

## Getting Started

`get_or_create()` is the recommended entry point: it fetches the store, or
creates it if it does not exist, in a single call -- so you can read and write
items right away.

```python
from azure.ai.agentserver.core.storage import FoundryStateStore, StateStoreItem

store = await FoundryStateStore.get_or_create(
    "checkpoints/thread-abc",
    user_isolation=True,
    item_ttl_seconds=3600,
    description="Checkpoint store for thread abc",
)
async with store:
    await store.set_item("step-1", {"done": False})

    item: StateStoreItem | None = await store.get_item("step-1")
    assert item is not None
    print(item.value)  # {"done": False}
    print(item.etag)
```

By default, the client resolves:

- `FOUNDRY_PROJECT_ENDPOINT` for the project endpoint
- `DefaultAzureCredential` for authentication (requires `azure-identity`)

## Store Name = Scope

To scope data to a conversation or thread, encode it directly into the store
name:

```python
await FoundryStateStore.get_or_create("checkpoints/thread-abc")
await FoundryStateStore.get_or_create("workflow-state/run-42")
await FoundryStateStore.get_or_create("user-prefs/defaults", user_isolation=True)
```

Because the store name is its identity, choose a stable naming scheme up
front. Names may contain `/`, so you can use it as a hierarchy separator.

## Store Lifecycle

`get_or_create()` is the only lifecycle call you need for the common case:

```python
store = await FoundryStateStore.get_or_create(
    "checkpoints/thread-abc",
    user_isolation=True,
    item_ttl_seconds=3600,
)
print(store.name)
```

Store-level operations (`get()`, `update()`, `delete()`) act on the bound
store itself; the explicit `*_item` methods act on individual items within it.

```python
info: StateStore = await store.get()                 # the store's metadata; raises if absent
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
- `delete()` cascades to every item under that store name.

## User Isolation and Delegated User IDs

Set `user_isolation=True` when the same store name should fan out per user.

```python
store = await FoundryStateStore.get_or_create(
    "user-prefs/defaults",
    user_isolation=True,
    user_id="aad-user-42",
)
```

- For direct callers, the platform can derive user identity from the token.
- For trusted callers acting on behalf of an end user, pass `user_id` so the SDK
  sends the delegated `x-ms-user-id` header on item operations.
- Store-management calls (`get_or_create`, `get()`, `update()`, `delete()`)
  stay store-scoped and do not send the delegated user
  header.

## Values, Tags, and TTL

Each item value is a JSON object -- pass a `dict`.

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
updated = await store.set_item(
    "step-1",
    {"done": True},
    tags={"kind": "checkpoint"},
)
print(updated.etag)
```

`set_item()` creates the item, or replaces it if the key already exists.

### Fetch one item

```python
item: StateStoreItem | None = await store.get_item("step-1")
if item is not None:
    print(item.id, item.key, item.value, item.tags, item.etag)
```

`get_item(key)` returns `None` when the item is missing; `get()` fetches the
store's metadata instead, raising `FoundryStorageNotFoundError` if the store is
absent.

### Delete one item

```python
deleted = await store.delete_item("step-1")
assert deleted.deleted is True
```

Deletes are idempotent.

## Optimistic Concurrency

Use `if_match` when you want a guarded update or delete:

```python
from azure.ai.agentserver.core.storage import FoundryStoragePreconditionError

item = await store.get_item("counter")
assert item is not None

try:
    await store.set_item("counter", {"value": item.value["value"] + 1}, if_match=item.etag)
except FoundryStoragePreconditionError as err:
    print("Current etag:", err.current_etag)
```

If you want a strict update that only succeeds when the item already exists, use
`require_exists=True`:

```python
await store.set_item("counter", {"value": 2}, require_exists=True)
```

## Listing Keys

`list_keys()` returns a keys-only page within the bound store.

```python
from azure.ai.agentserver.core.storage import StateStoreItemKeyPage

page: StateStoreItemKeyPage = await store.list_keys(tags={"kind": "checkpoint"}, limit=50, order="asc")
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
    await store.set_item("step-1", {"done": True}, if_match='"stale"')
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

**Item (`create_item`, `set_item`):**

| Field | Constraints | Mutability |
|-------|-------------|------------|
| `key` | 1-128 chars. Unicode; may contain `/`. Unique within the store. | Immutable |
| `value` | Opaque JSON object, <= 1 MB serialized inline. | Mutable via `set_item()` (replace) |
| `tags` | <= 16 entries, same shape as store tags. | Mutable via `set_item()` (replace) |

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
