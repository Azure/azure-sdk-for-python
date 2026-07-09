# Durable State Store Guide

`FoundryStateStore` is a durable, server-backed state-store client for agent
state. It gives your agent an explicit store resource plus single-item
operations over that store: create the store once, then create, replace, fetch,
delete, and list items inside it.

## Overview

`FoundryStateStore` is **bound to one caller-chosen store name**. That store
name is the main scoping tool for your data:

- Use one store per conversation/thread when you need conversation isolation.
- Use `user_isolation=True` when the store name is shared across many users and
  the platform should partition items per user.
- Set `item_ttl_seconds` once at store creation when you want idle items to
  age out automatically.

The SDK is the developer-facing layer over the internal `/storage/statestores/*`
protocol: it keeps the transport/auth pipeline in `FoundryStorageClient`, while
`FoundryStateStore` owns the ergonomic store-bound API.

## Getting Started

```python
from azure.ai.agentserver.core.storage import FoundryStateStore

async with FoundryStateStore(
    "checkpoints/thread-abc",
    user_isolation=True,
    item_ttl_seconds=3600,
    description="Checkpoint store for thread abc",
) as store:
    await store.get_or_create()
    await store.set("step-1", {"done": False})

    item = await store.get("step-1")
    print(item.value)  # {"done": False}
    print(item.etag)
```

By default, the client resolves:

- `FOUNDRY_PROJECT_ENDPOINT` for the project endpoint
- `DefaultAzureCredential` for authentication (requires `azure-identity`)

## Store Name = Scope

The protocol no longer has a built-in session-isolation knob. If you want
conversation or thread scoping, encode it directly into the store name:

```python
FoundryStateStore("checkpoints/thread-abc")
FoundryStateStore("workflow-state/run-42")
FoundryStateStore("user-prefs/defaults", user_isolation=True)
```

Because the store name is the logical identity, choose a stable naming scheme
up front. The raw name may contain `/`; the SDK handles the required base64url
path encoding on the wire.

## Store Lifecycle

Stores are **explicit resources**. Create or resolve them before writing items.

```python
info = await store.create()
print(info.id, info.name, info.item_ttl_seconds)

info = await store.create_or_get()
print(info.id, info.name, info.item_ttl_seconds)

info = await store.get_or_create()
print(info.id, info.name, info.item_ttl_seconds)

info = await store.get_properties()
info = await store.update_metadata(
    description="Checkpoint store for prod traffic",
    tags={"env": "prod", "team": "agents"},
)

deleted = await store.delete_store()
assert deleted.deleted is True
```

### Key points

- `create()` raises `FoundryStorageConflictError` if the store name already exists.
- `get_or_create()` fetches the store first, or creates it when it is absent.
- `create_or_get()` creates the store first, or fetches the existing descriptor on `409`.
- Neither helper updates existing `user_isolation`, `item_ttl_seconds`, `description`, or `tags`.
- `update_metadata()` only changes `description` and `tags`.
- `user_isolation` and `item_ttl_seconds` are fixed at create time.
- `delete_store()` cascades to every item under that store name.

## User Isolation and Delegated User IDs

Set `user_isolation=True` when the same store name should fan out per user.

```python
store = FoundryStateStore(
    "user-prefs/defaults",
    user_isolation=True,
    user_id="aad-user-42",
)
```

- For direct callers, the platform can derive user identity from the token.
- For trusted callers acting on behalf of an end user, pass `user_id` so the SDK
  sends the delegated `x-ms-user-id` header on item operations.
- Store-management calls (`create`, `get_properties`, `update_metadata`,
  `delete_store`) stay store-scoped and do not send the delegated user header.

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
store = FoundryStateStore("otp/user-42", item_ttl_seconds=300)
await store.get_or_create()
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
item = await store.get("step-1")
if item is not None:
    print(item.id, item.key, item.value, item.tags, item.etag)
```

`get()` returns `None` when the item is missing.

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
page = await store.list_keys(tags={"kind": "checkpoint"}, limit=50, order="asc")
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
| `FoundryStorageBadRequestError` | 400 / 409 | Invalid request or duplicate/conflict. |
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

## Best Practices

1. **Create stores deliberately.** Do not assume item writes will create the
   store for you.
2. **Encode conversation scope in the store name.** The store name replaces the
   old session-isolation knob.
3. **Use `user_isolation=True` only when needed.** Prefer a stable store naming
   scheme first, then add per-user partitioning when the store name is shared.
4. **Use `if_match` for read-modify-write flows.** Counters and checkpoints are
   race-prone without it.
5. **Keep values as JSON objects.** Serialize your own models explicitly.
6. **Reuse the client.** It owns an HTTP pipeline; construct it once and close it
   with `async with` or `await store.aclose()`.
