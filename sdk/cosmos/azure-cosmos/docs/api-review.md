# Python Cosmos DB SDK - Public API changes for review

## Contents

- [Client setup and navigation](#client-setup-and-navigation)
  - [`CosmosClient(...)` - Creating a Cosmos client](#cosmosclient-construction)
  - [`CosmosClient.from_connection_string` - Connection-string client creation](#cosmosclientfrom_connection_string)
  - [`CosmosClient.get_database_client` - Getting a database client from properties](#cosmosclientget_database_client)
  - [`CosmosClient.close` - Releasing client-owned resources](#cosmosclientclose)
- [Account and database operations](#account-and-database-operations)
  - [`CosmosClient.create_database` - Creating a database](#cosmosclientcreate_database)
  - [`CosmosClient.create_database_if_not_exists` - Creating a database if it does not exist](#cosmosclientcreate_database_if_not_exists)
  - [`CosmosClient.list_databases` - Listing databases](#cosmosclientlist_databases)
  - [`CosmosClient.query_databases` - Querying databases](#cosmosclientquery_databases)
  - [`CosmosClient.delete_database` - Deleting a database](#cosmosclientdelete_database)
  - [`DatabaseProxy.read` - Reading database properties](#databaseproxyread)
- [Container operations](#container-operations)
  - [`DatabaseProxy.create_container` - Creating a container](#databaseproxycreate_container)
  - [`DatabaseProxy.create_container_if_not_exists` - Creating a container if it does not exist](#databaseproxycreate_container_if_not_exists)
  - [`DatabaseProxy.delete_container` - Deleting a container](#databaseproxydelete_container)
  - [`DatabaseProxy.list_containers` - Listing containers](#databaseproxylist_containers)
  - [`DatabaseProxy.query_containers` - Querying containers](#databaseproxyquery_containers)
  - [`DatabaseProxy.replace_container` - Replacing container settings](#databaseproxyreplace_container)
  - [`ContainerProxy.read` - Reading container properties](#containerproxyread)
  - [`ContainerProxy.scripts` - Omitted script navigation](#containerproxyscripts)
  - [`ContainerProxy.is_system_key` - Excluding the public system-key property](#containerproxyis_system_key)
- [Item operations and queries](#item-operations-and-queries)
  - [`ContainerProxy.create_item` - Creating an item](#containerproxycreate_item)
  - [`ContainerProxy.read_item` - Reading an item](#containerproxyread_item)
  - [`ContainerProxy.read_items` - Reading known items](#containerproxyread_items)
  - [`ContainerProxy.read_all_items` - Reading every item](#containerproxyread_all_items)
  - [`ContainerProxy.query_items` - Query execution defaults and unordered DISTINCT compatibility](#containerproxyquery_items)
  - [`ContainerProxy.query_items_change_feed` - Polling item changes](#containerproxyquery_items_change_feed)
  - [`ContainerProxy.replace_item` - Replacing an existing order](#containerproxyreplace_item)
  - [`ContainerProxy.patch_item` - Patch compatibility decisions](#containerproxypatch_item)
  - [`ContainerProxy.execute_item_batch` - Sending transactional batches through Rust](#containerproxyexecute_item_batch)
- [Throughput management](#throughput-management)
  - [`DatabaseProxy.get_throughput` - Keeping database throughput results independent of response hooks](#databaseproxyget_throughput)
  - [`DatabaseProxy.read_offer` - Omitted throughput alias](#databaseproxyread_offer)
  - [`ContainerProxy.get_throughput` - Reading container throughput without changing the result or execution path](#containerproxyget_throughput)
  - [`ContainerProxy.read_offer` - Omitted throughput alias](#containerproxyread_offer)
- [Feed ranges and session consistency](#feed-ranges-and-session-consistency)
  - [`ContainerProxy.read_feed_ranges` - Discovering ranges for parallel order reads](#containerproxyread_feed_ranges)
  - [`ContainerProxy.is_feed_range_subset` - Rejecting unsupported subset inputs without legacy fallback](#containerproxyis_feed_range_subset)
- [Cosmos database users](#cosmos-database-users)
  - [`DatabaseProxy.list_users` - Omitted](#databaseproxylist_users)
  - [`DatabaseProxy.query_users` - Omitted](#databaseproxyquery_users)
  - [`DatabaseProxy.get_user_client` - Omitted](#databaseproxyget_user_client)
  - [`DatabaseProxy.create_user` - Omitted](#databaseproxycreate_user)
  - [`DatabaseProxy.upsert_user` - Omitted](#databaseproxyupsert_user)
  - [`DatabaseProxy.replace_user` - Omitted](#databaseproxyreplace_user)
  - [`DatabaseProxy.delete_user` - Omitted](#databaseproxydelete_user)
  - [`UserProxy.read` - Omitted](#userproxyread)
- [Cosmos resource permissions](#cosmos-resource-permissions)
  - [`UserProxy.list_permissions` - Omitted](#userproxylist_permissions)
  - [`UserProxy.query_permissions` - Omitted](#userproxyquery_permissions)
  - [`UserProxy.get_permission` - Omitted](#userproxyget_permission)
  - [`UserProxy.create_permission` - Omitted](#userproxycreate_permission)
  - [`UserProxy.upsert_permission` - Omitted](#userproxyupsert_permission)
  - [`UserProxy.replace_permission` - Omitted](#userproxyreplace_permission)
  - [`UserProxy.delete_permission` - Omitted](#userproxydelete_permission)
- [Conflicts](#conflicts)
  - [`ContainerProxy.list_conflicts` - Listing unresolved conflicts](#containerproxylist_conflicts)
  - [`ContainerProxy.query_conflicts` - Querying unresolved conflicts](#containerproxyquery_conflicts)
  - [`ContainerProxy.get_conflict` - Reading an unresolved conflict](#containerproxyget_conflict)
  - [`ContainerProxy.delete_conflict` - Deleting a handled conflict](#containerproxydelete_conflict)
- [Stored procedures](#stored-procedures)
  - [`ScriptsProxy.list_stored_procedures` - Omitted](#scriptsproxylist_stored_procedures)
  - [`ScriptsProxy.query_stored_procedures` - Omitted](#scriptsproxyquery_stored_procedures)
  - [`ScriptsProxy.get_stored_procedure` - Omitted](#scriptsproxyget_stored_procedure)
  - [`ScriptsProxy.create_stored_procedure` - Omitted](#scriptsproxycreate_stored_procedure)
  - [`ScriptsProxy.replace_stored_procedure` - Omitted](#scriptsproxyreplace_stored_procedure)
  - [`ScriptsProxy.delete_stored_procedure` - Omitted](#scriptsproxydelete_stored_procedure)
  - [`ScriptsProxy.execute_stored_procedure` - Omitted](#scriptsproxyexecute_stored_procedure)
- [Triggers](#triggers)
  - [`ScriptsProxy.list_triggers` - Omitted](#scriptsproxylist_triggers)
  - [`ScriptsProxy.query_triggers` - Omitted](#scriptsproxyquery_triggers)
  - [`ScriptsProxy.get_trigger` - Omitted](#scriptsproxyget_trigger)
  - [`ScriptsProxy.create_trigger` - Omitted](#scriptsproxycreate_trigger)
  - [`ScriptsProxy.replace_trigger` - Omitted](#scriptsproxyreplace_trigger)
  - [`ScriptsProxy.delete_trigger` - Omitted](#scriptsproxydelete_trigger)
- [User-defined functions](#user-defined-functions)
  - [`ScriptsProxy.list_user_defined_functions` - Omitted](#scriptsproxylist_user_defined_functions)
  - [`ScriptsProxy.query_user_defined_functions` - Omitted](#scriptsproxyquery_user_defined_functions)
  - [`ScriptsProxy.get_user_defined_function` - Omitted](#scriptsproxyget_user_defined_function)
  - [`ScriptsProxy.create_user_defined_function` - Omitted](#scriptsproxycreate_user_defined_function)
  - [`ScriptsProxy.replace_user_defined_function` - Omitted](#scriptsproxyreplace_user_defined_function)
  - [`ScriptsProxy.delete_user_defined_function` - Omitted](#scriptsproxydelete_user_defined_function)
- [Shared customer-visible changes](#shared-customer-visible-changes)

## Client setup and navigation

<a id="22---excluding-resource-tokens-and-cosmos-user-and-permission-apis"></a>
<a id="cosmosclient-construction"></a>

### `CosmosClient(...)`

Creates a client for a Cosmos DB account and supplies default settings for later
operations. Both synchronous and asynchronous clients support account keys and
Microsoft Entra credentials. Constructing a client does not create an account,
database, or container, or establish permission to access every resource.

```python
client = CosmosClient(
    endpoint,
    credential=key,
    consistency_level="Session",
    preferred_locations=["East US"],
)
```

**Supported credentials:** An account-key string, `{"masterKey": key}`, or a
Microsoft Entra token credential. Reuse the client for later operations and
close it when finished. The async client uses `async with` for its lifetime.

**Resource-token authentication is omitted.** The Rust driver supports account
keys and Entra, not Cosmos resource tokens. Both backends reject resource-token
maps, permission feeds, and `resourceTokens` or `permissionFeed` fields with
`ValueError` during construction, including when supplied alongside `masterKey`.
An empty or otherwise unsupported credential also fails during construction.

Account keys and Entra credentials remain supported. Cosmos resource permissions
are not Entra role assignments; changing the credential does not automatically
preserve a resource-token application's access rules. Cosmos user and permission
APIs are listed individually in their own groups below.

**Client-level networking options are removed.** Suppose Alpha Bank passes
`connection_verify="alpha-bank-ca.pem"` to trust a private certificate
authority. The SDK raises `TypeError` during construction; it does not accept
the file and then send the request without using it.

The same rule applies to `proxy_config`, `proxies`, `ssl_config`,
`connection_cert`, and `transport`, including values such as `None`, `True`,
or `{}`. The sync/async constructors and connection-string factories reject
these options on both backends. `ProxyConfiguration` and `SSLConfiguration`
are no longer public classes. Adding either field, or
`DisableSSLVerification`, to a `ConnectionPolicy` is rejected too.
Selecting the legacy backend does not restore these features; no parity
implementation is required. Runtime-controlled environment proxy use is
separate and unchanged.

**Regional routing switches are excluded on Rust-backed clients.** Alpha Bank
configures the account's regions and multi-write capability. Rust discovers
the endpoints and selects eligible destinations for requests; the client does
not offer separate switches to disable that discovery or multi-write routing.
Neither the Rust SDK nor its driver exposes equivalent Boolean opt-outs.

The synchronous and asynchronous constructors raise `TypeError` for explicit
`enable_endpoint_discovery` or `multiple_write_locations`, including `True`,
`False`, and `None`, before constructing the backend or connection. The same
rule applies through `from_connection_string` and when explicitly assigning
`ConnectionPolicy.EnableEndpointDiscovery` or
`ConnectionPolicy.UseMultipleWriteLocations`, even to a legacy default value.

Omit these switches and leave those policy fields unset. An untouched policy
can still group supported settings. Preferred and excluded regions remain
supported, but are not replacements for the excluded switches. The retained
`core-python` comparison backend continues to honor them; its code is not
retired by this decision.

<a id="1---connection-string-client-creation"></a>
<a id="connection-string-client-creation"></a>
<a id="cosmosclientfrom_connection_string"></a>

### `CosmosClient.from_connection_string`

**Why the customer calls this API**

The customer app needs a Cosmos DB client before it can store or read orders
in the existing `orders` container. The customer's configuration supplies a
**connection string**: one string containing the account endpoint (the service
backend's address) and an account key (the credential used to authenticate).
This API creates the client from that string, so the customer app does not
have to split the endpoint and key into separate constructor arguments.


Creating the client does not create the `sales` database or the `orders`
container, and it does not itself store or read `order-42`. Those are separate
operations.

**Why this needs a public decision**

The previous sync and async methods accepted a separate `credential` argument
but did not use it consistently. Given a connection string containing account
key A and `credential=account_key_B`:

| Previous API | Credential used |
|---|---|
| Synchronous | Key B, overriding the connection string's key. |
| Asynchronous | Key A, ignoring the separate credential for authentication. |

The synchronous method also accepted a Microsoft Entra token credential with
an endpoint-only connection string. The asynchronous method did not use that
credential and could raise `KeyError` when the string omitted `AccountKey`.

We removed the separate credential option from both methods to establish one
consistent contract: the connection string supplies both the endpoint and
the account key. We chose this rule rather than extend credential overrides
to the async method. This is a breaking change for synchronous callers that
used a separate key or Entra credential, not just a validation fix.

This is a Python wrapper contract decision, not a missing Rust-driver capability.

**Current decision; approval is not recorded**

Both sync and async methods use the embedded key. A separate `credential` keyword raises
`TypeError` whenever it is supplied, even as `None`, `False`, or an empty
string.
The normal constructor remains the route for a separate key or Microsoft
Entra credential; Entra authentication itself remains supported.

```python
# Choose the embedded key.
client = CosmosClient.from_connection_string(
    connection_string, consistency_level="Session"
)

# Alternative: choose a separate credential without a connection string.
client = CosmosClient(endpoint, credential=other_key)
```

These are alternative ways to construct the application client, not two clients
needed for one database. Its later navigation can use
`client.get_database_client("sales")`.

**Why customer calls may need changing**

Besides choosing one credential source, the Python SDK cleanup gives
synchronous and asynchronous callers the same argument and validation rules.
The first two rows below describe the calling rules customers must follow.
The remaining rows explain explicit errors for invalid connection strings;
they do not mean that those invalid values previously created a usable client.

| Kind of change | Customer input | Required action or error |
|---|---|---|
| Credential-source decision | A separate `credential` is supplied | Omit it to use the embedded key, or use `CosmosClient(endpoint, credential=...)` for a separate credential. |
| Sync/async argument alignment | Optional values are passed without names | Name the setting, for example `consistency_level="Session"`. Only `conn_str` may be positional. |
| Consistent validation | The endpoint or key is missing or empty | Correct the connection string. The SDK raises `ValueError` before client construction; a separate credential cannot replace a missing key. |
| Clear error for an invalid type | The connection string is not a string | Supply a string. The SDK raises an explicit `TypeError` instead of failing while trying to use a string operation on that value. |
| Clear error for malformed text | A setting does not use `name=value` | Separate valid settings with semicolons. The SDK raises `ValueError` without including the supplied key or connection string in the error. |


**Signature on both client classes**

```python
@classmethod
def from_connection_string(
    cls,
    conn_str: str,
    *,
    consistency_level: Optional[str] = None,
    **kwargs: Any
) -> "CosmosClient":
    ...
```

<a id="21---getting-a-database-client-from-properties"></a>
<a id="database-client-from-properties"></a>
<a id="cosmosclientget_database_client"></a>

### `CosmosClient.get_database_client`

**Why the customer calls this API**

The customer has selected `sales` from a database listing and wants a
`DatabaseProxy`, the Python object used to access that database's containers.
For example, the customer can pass the listed properties containing
`{"id": "sales"}` and then obtain a client for `orders`.

This API constructs a local object. It does not create `sales` or contact
the service backend to verify that the database exists.

**Why this needs a public decision**

Properties can be supplied as a **mapping**, an object supporting lookup
by key, such as a dictionary. A read-only mapping supports that same lookup
without allowing its entries to be changed. Both forms should work here.
The review also needs one rule for the ID's Python type: if the supplied
mapping contains `{"id": 123}`, should `database.id` be the number `123`
or the string `"123"`? Sync and async callers should get the same answer.

**Current decision; approval is not recorded**

Both methods look up the mapping's `id` and convert it to a string.
Their annotations describe that input as `Mapping[str, Any]`.
They still accept a plain database-name string or
an existing proxy of the matching sync/async type. This is Python SDK input
and result-type alignment, not a missing Rust-driver capability.

```python
from types import MappingProxyType

properties = MappingProxyType({"id": "sales", "_rid": "unused-here"})
database = client.get_database_client(properties)
assert database.id == "sales"

numeric_name = client.get_database_client({"id": 123})
assert numeric_name.id == "123"
```

Only the supplied ID is reused. The method creates a fresh proxy attached to
the calling client; it does not adopt another proxy's connection or cache the
mapping's other properties. It sends no request and does not verify existence,
permissions, or the name. A missing `id` still raises `KeyError`.

Passing a proxy from another client also supplies only its ID.
The newly returned object belongs to the client on which this method was
called, not to the other client's account or connection.

**What customer code must change**

String-ID callers keep their existing behavior. Code that relies on an integer
`database.id` must compare with `"123"` rather than `123`, use string dictionary
keys where appropriate, and account for string output when serializing that
attribute. The address represented by this example is still `dbs/123`; the
change concerns the Python value's type, not selecting another database.

**Current signature on both client classes**

```python
def get_database_client(
    self,
    database: Union[str, DatabaseProxy, Mapping[str, Any]]
) -> DatabaseProxy:
    ...
```

<a id="cosmosclientclose"></a>

### `CosmosClient.close`

**Current contract; no public API change is needed.**

Alpha Bank has finished using `alpha-bank-db` / `alpha-bank-container`.
`client.close()` releases the synchronous client's local resources;
`await client.close()` does so for the asynchronous client. Both return
`None` on normal completion, accept no request options, and use the same
cleanup path as leaving their corresponding context manager.

Finish operations before closing. Close does not delete service data, drain
in-flight work, or close the application's credential. Repeated calls do not
release another client's driver acquisition. A client or runtime still owned
elsewhere remains usable; close is not process-wide runtime shutdown.

<a id="first-use-initialization-deadlines"></a>

**First-use initialization and close:** Synchronous operations now wait for
shared background driver acquisition within their own remaining timeout.
For example, a first read with `timeout=1` can stop waiting while a second read
with `timeout=5` continues waiting for the same acquisition. The expired read
is not dispatched when the handle later arrives. Callers still waiting receive
the same result or failure; after failure, a later call can retry acquisition.

Close does not wait for that worker to finish. If the client remains open, the
worker retains a late handle for later calls; if close wins, the worker releases
it instead. The worker retains its original credential and runtime inputs even
if close clears the adapter's fields. This bounds the customer's acquisition
wait, not the lifetime of a synchronous credential callback or native setup.

Cancelling an async caller's wait does not cancel backend cleanup that has
already started. A later close waits for that same completion, and the
client's Python routing-cache share is released in `finally`. This does not
make every cleanup step cancellation-proof. Backend cleanup failures are
logged; Python HTTP cleanup errors can still propagate.

## Account and database operations

<a id="2---creating-a-database"></a>
<a id="cosmosclientcreate_database"></a>

### `CosmosClient.create_database`

**Why the customer calls this API**

The customer needs a `sales` database to hold its `orders` container.

```python
database = client.create_database("sales")
```

The call creates the database and returns a `DatabaseProxy`, the Python
object used for later database operations. Creating the `orders` container
and storing `order-42` are separate calls.

If `sales` already exists, this API raises `CosmosResourceExistsError`.
It does not return the existing database.

**Why this needs a public decision**

The basic creation operation is not changing. The review concerns existing
customer code that supplies arguments or a response hook. These are Python
wrapper cleanup and compatibility decisions, not changes required by a
missing Rust-driver capability.

For example, the customer app may pass a session token because it reuses
settings across several SDK operations:

```python
database = client.create_database("sales", session_token=None)
```

A session token does not provide a consistency requirement for database
creation. Previously, supplying this value was accepted without providing
that behavior. The current implementation rejects the keyword with
`TypeError`, including when its value is `None`.

The decision is whether to stop accepting arguments that do not apply to
this API. This can require customer code changes even though the arguments
never provided the requested behavior.

A separate decision concerns `response_hook`: the customer function called
after successful creation. Its arguments and its ability to affect the
returned result need one clear contract across synchronous and asynchronous
clients.

**Current proposal; approval is not recorded**

| Proposed change | Why | Customer impact |
|---|---|---|
| Allow only `id` as a positional argument | Give both clients the same calling rules and remove the obsolete positional query-metrics argument | Existing synchronous calls using additional positional arguments must name their settings. The asynchronous API already rejected those extra positional arguments. |
| Reject `populate_query_metrics`, `session_token`, `etag`, and `match_condition` when supplied | These arguments do not provide their corresponding query or item-operation behavior for database creation | Remove the keywords, including entries containing `None` or `False` in dictionaries passed with `**settings`. |
| Reject conflicting or incomplete throughput settings before creation | The request must specify one capacity mode rather than leave conflicting instructions for the service backend | Choose manual throughput or autoscale. Mixed modes, an empty `ThroughputProperties`, or an autoscale increment without a maximum raise `ValueError`. |

For the positional-argument change:

```python
# Previously accepted by the synchronous client.
database = client.create_database("sales", None, 4000)

# Proposed calling convention for both clients.
database = client.create_database("sales", offer_throughput=4000)
```

Here, `4000` requests database capacity of 4,000 request units per second
(RU/s). It is not the charge for this one creation request. The examples in
this section are alternatives, not a sequence of creations to run against
the same database.

**Choose one throughput mode**

The remaining call examples use the asynchronous client and `await`.
The customer must choose how the `sales` database's capacity is managed:

- **Manual throughput:** request a fixed capacity, such as 4,000 RU/s.
- **Autoscale:** let the service backend adjust capacity within its supported
  range, up to a configured maximum, such as 10,000 RU/s.

These are different capacity modes, not two values to combine.
`ThroughputProperties` describes the requested capacity settings:

```python
throughput = ThroughputProperties(
    offer_throughput=4000,
    auto_scale_max_throughput=10000,
)

await client.create_database("sales", offer_throughput=throughput)
```

This asks for both fixed capacity and automatically adjusted capacity.
The Python wrapper now raises `ValueError` before sending the creation
request rather than choosing a mode or passing conflicting instructions
to the service backend.

The customer must choose one of these alternatives:

```python
# Manual throughput: fixed capacity of 4,000 RU/s.
await client.create_database("sales", offer_throughput=4000)

# Alternative: autoscale with a maximum of 10,000 RU/s.
await client.create_database(
    "sales",
    offer_throughput=ThroughputProperties(
        auto_scale_max_throughput=10000,
    ),
)
```

The values are illustrative, not capacity recommendations. This change makes
conflicting inputs fail earlier; it does not mean the previous implementation
successfully created a database with both modes.

**One response-hook contract for both clients**

The synchronous implementation already calls the response hook with two
arguments: the creation response headers and database properties. The
asynchronous implementation previously supplied only the headers.

The proposed contract is `response_hook(headers, properties)`.
An existing asynchronous hook therefore needs this change:

```python
# Previous asynchronous hook.
def on_created(headers):
    print(headers.get("x-ms-request-charge"))

# Hook matching the proposed common contract.
def on_created(headers, properties):
    print(properties["id"], headers.get("x-ms-request-charge"))
```

A hook that does not need the properties must still accept the second
argument. The hook remains an ordinary synchronous function, including
when supplied to the asynchronous client.

The Python wrapper must be able to call the supplied `response_hook`.
Use `None` when no hook is needed. Supplying a value it cannot call, such as
a string, raises `TypeError` before creation is attempted:

```python
# Incorrect: this supplies text, not a function.
await client.create_database("sales", response_hook="on_created")

# Correct: this supplies the function defined above.
await client.create_database("sales", response_hook=on_created)
```

**The response hook observes the result; it does not change it**

The proposed contract gives the hook its own copies of the creation
headers and database properties, including nested values.

```text
Service backend creates sales
    -> Python wrapper receives the creation response
    -> response hook receives separate copies of its headers and properties
    -> customer app receives the database result
```

For example, assigning `properties["id"] = "local-note"` inside the hook
does not change `database.id` or the properties separately returned by
`create_database`.

This matters to customer code that previously edited the hook's arguments
to influence the returned result. Such code must instead perform its own
transformation after the call.

If the hook raises while running, the database has already been created.
Its exception reaches the customer app, but the SDK does not repeat or
undo creation.

**Decision requested**

Approve or revise the stricter argument rules, early throughput validation,
and common response-hook contract.

Customer migration consists of naming optional arguments, removing
inapplicable keywords, choosing one throughput mode, updating one-argument
asynchronous hooks, and moving any intended result transformation out of
the hook.

**Async signature for review**

```python
async def create_database(
    self,
    id: str,
    *,
    offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
    initial_headers: Optional[dict[str, str]] = None,
    response_hook: Optional[
        Callable[[Mapping[str, Any], Mapping[str, Any]], None]
    ] = None,
    throughput_bucket: Optional[int] = None,
    return_properties: bool = False,
    **kwargs: Any,
) -> Union[DatabaseProxy, tuple[DatabaseProxy, CosmosDict]]:
    ...
```

The synchronous client accepts the same arguments but uses `def`; its call
is not awaited. Each client returns its corresponding `DatabaseProxy`.

By default, the result is the database object. With `return_properties=True`,
the result also includes a `CosmosDict`: the database properties with access
to the creation-response headers. These return forms already exist.

This presentation makes the supported named options visible for review.
The current implementation receives several of them through `**kwargs`;
listing them here does not introduce new options.

<a id="3---creating-a-database-if-it-does-not-exist"></a>
<a id="cosmosclientcreate_database_if_not_exists"></a>

### `CosmosClient.create_database_if_not_exists`

**Why the customer calls this API**

The customer reruns setup and needs the `sales` database to be available
before accessing its `orders` container.

```python
database = await client.create_database_if_not_exists(
    "sales",
    offer_throughput=4000,
)
```

The call returns the existing database or creates it if missing.

The throughput setting applies only when this call creates the database.
If `sales` already has 10,000 RU/s, the call returns that database without
changing its capacity to 4,000 RU/s. This behavior is unchanged.

The examples below use the asynchronous client. The synchronous client
follows the same rules without `await`.

**Why this needs a public decision**

The customer expects the same setup call to work predictably whether:

- `sales` already exists;
- `sales` is missing; or
- another caller creates `sales` while this call is running.

Previously, those circumstances could change whether an invalid argument
was detected or whether the customer received a conflict instead of a database.

The proposed changes make argument validation independent of database
existence and handle another caller creating the database between the
initial read and creation attempt. These are Python wrapper validation and
recovery changes, not missing Rust-driver capabilities.

The argument rules and response-hook contract explained in `CosmosClient.create_database` also
apply here. They are not repeated below.

**Concurrent creation: return the database instead of reporting a conflict**

Consider two callers trying to make `sales` available:

```text
This call reads sales
    -> service backend reports that sales does not exist

Another caller creates sales with 10,000 RU/s

This call attempts to create sales with 4,000 RU/s
    -> service backend reports that sales already exists
```

Previously, this call raised `CosmosResourceExistsError`.

The proposed behavior adds a follow-up read:

```text
Creation reports that sales already exists
    -> Python wrapper reads sales again
    -> returns the database created by the other caller
    -> leaves its 10,000 RU/s unchanged
```

**Why:** the customer's requirement is that the database exists, not that
this particular call created it.

This recovery does not suppress every failure. If the follow-up read fails,
that error reaches the customer app. The Python wrapper does not start
another creation attempt.

**Invalid creation settings: reject them even when the database exists**

Suppose the customer accidentally supplies text instead of an integer:

```python
database = await client.create_database_if_not_exists(
    "sales",
    offer_throughput="4000",
)
```

Previously, whether this failed depended on the database's state:

| Database state | Previous behavior | Proposed behavior |
|---|---|---|
| `sales` already exists | The call could return the database without checking the invalid creation setting. | Raise `TypeError` before any database request. |
| `sales` is missing | The call checked existence, then raised `TypeError` when preparing creation. | Raise the same `TypeError` before any database request. |

**Customer impact:** setup code that previously succeeded because `sales`
already existed must now correct the argument:

```python
database = await client.create_database_if_not_exists(
    "sales",
    offer_throughput=4000,
)
```

The same early validation applies to conflicting or incomplete throughput
settings, as explained in `CosmosClient.create_database`.

**Why:** valid arguments should not depend on what happens to exist in the
account. These local checks do not guarantee that the service backend will
accept every correctly typed capacity value.

**Conditional headers: reject requests that conflict with returning the database**

A conditional header asks the service backend to make its response depend
on a condition. For example:

```python
database = await client.create_database_if_not_exists(
    "sales",
    initial_headers={"If-None-Match": "*"},
)
```

That condition can prevent an existence read from returning the database
properties needed by this operation.

Previously, the API did not reject the header at this boundary. The proposed
contract raises `TypeError` before any database request, whether `sales`
exists or not. The same restriction applies to other supplied access
conditions, including `If-Match`.

**Why:** this API must return the existing or newly created database.
It is not a conditional-read API. Customer code needing a conditional read
should perform that separately through `DatabaseProxy.read`.

**One timeout covers the complete operation**

This API can perform an existence read, a creation attempt, and a follow-up
read after a creation conflict. Those steps must not each receive a fresh
timeout.

For example:

```text
Customer supplies timeout=5
    -> setup and the existence read consume approximately two seconds
    -> approximately three seconds remain for creation and any follow-up read
```

The response hook runs outside the timed work. A timeout or cancellation
does not undo creation already accepted by the service backend.

**The response hook describes the final successful result**

As explained in `CosmosClient.create_database`, both clients use `response_hook(headers, properties)`
and give the hook independent response data.

For this API, the hook runs once after the complete operation succeeds:

| How the operation succeeds | Response supplied to the hook |
|---|---|
| `sales` exists on the first read | That read's headers and properties |
| This call creates `sales` | The creation response's headers and properties |
| Another caller creates `sales` first | The successful follow-up read's headers and properties |

The hook does not report every internal request. In particular, its
`x-ms-request-charge` describes the final successful response, not the sum
of all requests in the operation.

A hook exception is not treated as a missing database or a creation conflict.

**Decision requested; approval is not recorded**

Approve or revise the early argument validation, rejection of conditional
headers, recovery from concurrent creation, and single operation timeout.

Together with the shared changes in `CosmosClient.create_database`, these rules require customers
to correct invalid setup arguments and remove conditions that do not fit
this API. A concurrent creation that previously raised a conflict can now
return the existing database successfully.

**Async signature for review**

```python
async def create_database_if_not_exists(
    self,
    id: str,
    *,
    offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
    initial_headers: Optional[dict[str, str]] = None,
    response_hook: Optional[
        Callable[[Mapping[str, Any], Mapping[str, Any]], None]
    ] = None,
    throughput_bucket: Optional[int] = None,
    return_properties: bool = False,
    **kwargs: Any,
) -> Union[DatabaseProxy, tuple[DatabaseProxy, CosmosDict]]:
    ...
```

As in `CosmosClient.create_database`, the signature shows supported named options explicitly
for review. The synchronous client accepts the same arguments and returns
its corresponding `DatabaseProxy`.

Returning only the database object remains the default.
`return_properties=True` already exists; it is not a new return form.
Its properties and headers come from the final successful response
described above.

<a id="4---listing-databases"></a>
<a id="cosmosclientlist_databases"></a>

### `CosmosClient.list_databases`

**Why the customer calls this API**

The customer app needs the database names available in the account so the
customer can select `sales` before accessing its `orders` container.

```python
databases = client.list_databases(max_item_count=2)

async for database_properties in databases:
    print(database_properties["id"])
```

`list_databases` returns a database iterator: an object the customer app
iterates to receive one database-property dictionary at a time, not orders
stored inside those databases.

The service backend returns groups of results called pages.
`max_item_count=2` requests at most two databases per service page, not two
properties per database or two databases in total.

For example, an account containing `sales`, `inventory`, and `support`
could return:

```text
First page:
    {"id": "sales", ...}
    {"id": "inventory", ...}

Second page:
    {"id": "support", ...}
```

The examples use the asynchronous client. As before, iteration fetches
pages: use `async for`, not `await client.list_databases(...)`.

**Why this needs a public decision**

Previously, the response hook ran when the iterator was created, before
fetching a page. Its headers could describe an earlier operation: a
customer recording the charge for listing databases could record the
charge for creating `sales` instead.

The proposal runs the hook after each successful service page. It also
changes argument validation and how customers reuse settings. These are
Python wrapper changes, not missing Rust-driver capabilities.

**The response hook observes each fetched page**

The customer supplies a response-hook function named `on_databases` below;
the SDK invokes it. Its existing one-argument form, `headers`, is unchanged.
Previously the SDK invoked it before `list_databases()` returned. Now the
customer receives the iterator first, and the hook runs only when iteration
fetches a successful service page.

```python
def on_databases(headers):
    print(headers.get("x-ms-request-charge"))

databases = client.list_databases(
    max_item_count=2,
    response_hook=on_databases,
)
async for database_properties in databases:
    print(database_properties["id"])
```

If the service backend returns five databases in pages containing two,
two, and one result:

```text
Fetch first page  -> hook receives first page's headers  -> return two results
Fetch second page -> hook receives second page's headers -> return two results
Fetch third page  -> hook receives third page's headers  -> return one result
```

The hook runs three times, not once; successful empty service pages also
invoke it. Code expecting an immediate hook call must now iterate. Code
recording one event per method call must account for multiple page responses.
The hook remains an ordinary `def` function on both clients.

`DatabaseProxy.list_containers` consolidates this timing change across database and container
listing/query APIs. Database hooks do not gain a results-iterator argument;
container hooks retain theirs.

An ordinary exception raised by the hook reaches the customer app without
repeating the page request. Hook exceptions `StopIteration` and
`StopAsyncIteration`, which normally signal finished iteration, become
`RuntimeError` so a hook failure cannot silently end the results.

Use `None` to disable the hook. A callable object whose boolean value is
`False` is now invoked rather than skipped.

**Argument changes and customer migration**

| Proposed change | Previous behavior | Customer action |
|---|---|---|
| Require all settings to be named | The synchronous API accepted a positional page size and query-metrics flag. The asynchronous API already required named settings. | Replace `client.list_databases(2)` with `client.list_databases(max_item_count=2)`. |
| Reject invalid page sizes before iteration | Page sizes did not receive the same upfront range checks. | Use a positive integer below `2**63`, `-1` for a service-selected size, or `None`. Zero, other negative values, booleans and invalid types raise `ValueError`. |

The page-size range also applies to the `x-ms-max-item-count` request header.
A directly supplied, non-`None` `max_item_count` takes precedence.

The current wrapper rejects `populate_query_metrics`, `session_token`,
`availability_strategy`, `no_response` and `content_type`, including `None`,
`False` and corresponding entries in the selected settings dictionary.
Removal approval is limited to argument forms confirmed to have been ignored.
In particular, legacy `content_type` could set a request header; its rejection
is not included in the ignored-option cleanup.

**Use `request_options` for a settings dictionary**

The customer can name settings directly or supply them in a dictionary:

```python
# Current call using feed_options.
databases = client.list_databases(feed_options={"maxItemCount": 2})

# Proposed preferred dictionary argument.
databases = client.list_databases(request_options={"maxItemCount": 2})
```

Both dictionary names configure the same operation, not different kinds of
requests. The dictionary key remains `maxItemCount`; the direct argument is
`max_item_count`.

**Proposal:** standardize on `request_options` across APIs that currently
accept both names, and deprecate `feed_options`. Existing calls would
continue to work during the deprecation period. Warning policy and release
timing remain undecided; deprecation is not yet implemented.

Currently, if both dictionaries are supplied, the Python wrapper selects
`request_options`, even when it is empty or `None`. It does not merge the
dictionaries. This precedence remains unchanged during deprecation. A direct,
non-`None` `max_item_count` overrides the selected dictionary's page size.

Customers using only `feed_options` can rename that argument to
`request_options` without changing its dictionary keys. Customers supplying
both names must first reconcile their settings rather than mechanically
rename one.

**Settings are fixed when the database iterator is created**

A customer app may reuse a settings dictionary:

```python
options = {"maxItemCount": 2}
databases = client.list_databases(request_options=options)

options["maxItemCount"] = 10
```

The iterator keeps a page size of two. To use ten, create a new iterator.
Previously, preparing the iterator could modify the customer's dictionary;
the proposed behavior leaves it unchanged, including nested headers.

**A timeout applies to fetching results, not processing all databases**

By default, `timeout=5` gives each fetch of the next results a five-second
budget, shared by setup and any empty service pages consumed along the way:

```text
Start fetching the next results with five seconds
    -> setup takes two seconds
    -> an empty service page takes two seconds
    -> one second remains to fetch results
```

Customer processing of delivered results does not consume the next fetch's
budget. Invalid initial timeouts raise `ValueError` when the iterator is
created; use `None` or finite, non-boolean seconds with `1 <= timeout < 2**64`.

**Decision requested; approval is not recorded**

Approve or revise the per-page response-hook timing, explicit handling of
hook failures, named arguments, validation and fixed iterator settings.
Agree on the shared `request_options` proposal and its deprecation schedule.
The current blanket option rejection is not an approved removal decision.

**Asynchronous-client signature for review**

```python
def list_databases(
    self,
    *,
    max_item_count: Optional[int] = None,
    initial_headers: Optional[dict[str, str]] = None,
    response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
    throughput_bucket: Optional[int] = None,
    **kwargs: Any,
) -> AsyncItemPaged[dict[str, Any]]:
    ...
```

The method uses `def` because it returns the iterator immediately. The
synchronous client accepts the same arguments and returns
`ItemPaged[dict[str, Any]]`, consumed with `for`.

<a id="5---querying-databases"></a>
<a id="cosmosclientquery_databases"></a>

### `CosmosClient.query_databases`

**Why the customer calls this API**

The customer app needs to find databases matching a condition, rather than
retrieve every database as in `CosmosClient.list_databases`. For example, it wants the properties
of the database named `sales` before accessing its `orders` container.

```python
databases = client.query_databases(
    "SELECT * FROM db WHERE db.id = @id",
    parameters=[{"name": "@id", "value": "sales"}],
)

async for database_properties in databases:
    print(database_properties["id"])
```

`@id` is a query parameter: a named value supplied separately from the SQL
text. Here, its value is `"sales"`.

This API queries database properties, not orders inside their containers.
`SELECT *` returns a property dictionary for each matching database.

As in `CosmosClient.list_databases`, results are fetched during iteration. The example uses the
asynchronous client: use `async for`, not `await client.query_databases(...)`.

**Why this needs a public decision**

Previously, the synchronous API could interpret an empty query as a request
to list every database. A customer app that accidentally supplied `""` could
therefore receive an unfiltered result instead of an error.

The proposed changes reject invalid query inputs, align both clients'
arguments and fix query parameters when the iterator is created. These are
Python wrapper compatibility decisions, not missing Rust-driver capabilities.

**Require the query and name optional settings**

Both clients must receive `query`, either positionally or by name. All
optional settings must be named.

Previously, synchronous code could supply query parameters positionally:

```python
sql = "SELECT * FROM db WHERE db.id = @id"
parameters = [{"name": "@id", "value": "sales"}]
databases = client.query_databases(sql, parameters)
```

The proposed call names them:

```python
databases = client.query_databases(sql, parameters=parameters)
```

**Distinguish an invalid query from a request for all databases**

| Customer input | Proposed behavior | Customer action |
|---|---|---|
| `client.query_databases()` | Raise `TypeError` because `query` is missing. Legacy synchronous code could omit it. | Supply a query, or use `list_databases()` to retrieve all databases. |
| `client.query_databases("")` or whitespace-only SQL | Raise `ValueError` when the iterator is created. | Correct the missing SQL instead of accidentally requesting an unfiltered result. |
| `client.query_databases(None)` | Retrieve all databases without a SQL filter; ignore any accompanying parameters. | Prefer `list_databases()` for new code because it states the intention clearly. |

Passing `None` remains accepted so existing calls requesting all databases
continue to work.

**Supply query parameters in one place**

The customer can supply SQL and parameters separately, as in the first
example, or together in a query dictionary:

```python
query = {
    "query": "SELECT * FROM db WHERE db.id = @id",
    "parameters": [{"name": "@id", "value": "sales"}],
}

databases = client.query_databases(query)
```

Supplying that dictionary together with a separate `parameters` value now
raises `ValueError` when the iterator is created. Supply parameters in only
one place. Each parameter must contain exactly `name` and `value`, with a
name beginning with `@`; malformed entries are also rejected before fetching.

**Query parameters are fixed when the iterator is created**

Previously, changing the customer's parameter objects could change a
pending query. The proposed behavior fixes their values when the iterator
is created:

```python
parameters = [{"name": "@id", "value": "sales"}]

databases = client.query_databases(
    "SELECT * FROM db WHERE db.id = @id",
    parameters=parameters,
)

parameters[0]["value"] = "archive"
```

The existing iterator still queries `sales`, including on later pages.
To query `archive`, create a new iterator with the changed parameter.

**Cross-partition option: removal remains unresolved**

Legacy synchronous calls accepted `enable_cross_partition_query=True` and
forwarded its request header. The current Python wrapper instead raises
`TypeError`, including for `False` or `None`. For example:

```python
databases = client.query_databases(
    "SELECT * FROM db WHERE db.id = @id",
    parameters=[{"name": "@id", "value": "sales"}],
    enable_cross_partition_query=True,
)
```

This is a Python rejection, not an established Rust-driver gap. Because
legacy forwarded the flag, it is not included in the ignored-option cleanup.
Live verification remains pending to establish whether removing it changes
service behavior. Removing the argument avoids the local error, but is not
yet an established behavior-preserving migration.

**Shared changes from `CosmosClient.list_databases`**

The page-size, response-hook timing, timeout and settings-copying changes in
`CosmosClient.list_databases` also apply here, as does the proposal to use `request_options`
and deprecate the old dictionary name.

For `query_databases`, the SDK previously invoked the customer's
`response_hook(headers)` before returning the iterator. It now returns the
iterator first and invokes that same one-argument hook after each successful
service page, including empty pages. Customer code must start iteration before
expecting the hook to run and account for multiple invocations. `DatabaseProxy.list_containers`
consolidates the timing comparison; no results-iterator argument is added here.

The current wrapper also rejects `session_token`, `populate_query_metrics`,
`availability_strategy`, `no_response` and `content_type`, including explicit
`None` or `False` and their entries in the selected settings dictionary.
Removal approval remains limited to forms established to have been ignored;
the blanket rejection is not an approved compatibility decision.

**Decision requested; approval is not recorded**

Approve or revise the required query argument, named optional settings,
early query validation, fixed query-parameter values and shared changes from
`CosmosClient.list_databases`.

Keep the cross-partition option decision open until its legacy service
effect is established.

**Asynchronous-client signature for review**

```python
def query_databases(
    self,
    query: Optional[Union[str, dict[str, Any]]],
    *,
    parameters: Optional[list[dict[str, Any]]] = None,
    max_item_count: Optional[int] = None,
    initial_headers: Optional[dict[str, str]] = None,
    response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
    throughput_bucket: Optional[int] = None,
    **kwargs: Any,
) -> AsyncItemPaged[Any]:
    ...
```

The synchronous client accepts the same arguments and returns `ItemPaged[Any]`.

<a id="6---deleting-a-database"></a>
<a id="cosmosclientdelete_database"></a>

### `CosmosClient.delete_database`

**Why the customer calls this API**

The customer has finished using a test `sales` database and wants to remove
it, including its `orders` container and stored orders.

```python
await client.delete_database("sales")
```

Success returns `None`.

**Proposed breaking change: reject previously ignored arguments**

Legacy Python accepted certain arguments without using them to configure
database deletion. The proposal is to reject those arguments rather than
continue accepting them. These are Python wrapper cleanup decisions, not
Rust-driver limitations.

| Argument | Previous behavior | Proposed behavior |
|---|---|---|
| `session_token`, on both clients | Ignored for database deletion. A non-`None` value produced a warning. | Raise `TypeError` whenever supplied, including `None`. |
| `populate_query_metrics`, on the synchronous client | Accepted positionally or by name but did not enable query metrics for deletion. A non-`None` value produced a warning. | Raise `TypeError` whenever supplied, including `False` or `None`. |

**Customer impact and migration**

Previously, a customer could pass an ignored query-metrics argument:

```python
# Previous synchronous calls.
client.delete_database("sales", False)

client.delete_database(
    "sales",
    populate_query_metrics=False,
)
```

Both calls become:

```python
client.delete_database("sales")
```

Likewise, remove an ignored session-token argument:

```python
# Previous asynchronous call.
await client.delete_database("sales", session_token=token)

# Proposed call.
await client.delete_database("sales")
```

The deletion itself does not gain or lose functionality from removing an
ignored argument. The breaking change is that an existing call now raises
`TypeError` until the customer removes that argument. Calls that previously
supplied `None` without receiving a warning are also affected.

After removing the synchronous query-metrics argument, only the database
target may be positional. All remaining optional settings must be named.

**Decision requested; approval is not recorded**

Approve or revise removal of `session_token` from both clients and the
ignored `populate_query_metrics` argument from the synchronous client.

For the synchronous client, the proposal removes `populate_query_metrics`
both positionally and by name.

The asynchronous client never declared this parameter, but callers could
supply the keyword through `**kwargs`. The current implementation rejects
it; whether legacy async ignored or forwarded it remains unverified.
That rejection is not yet an approved removal decision.

**Asynchronous-client signature for review**

```python
async def delete_database(
    self,
    database: Union[str, DatabaseProxy, dict[str, Any]],
    *,
    initial_headers: Optional[dict[str, str]] = None,
    response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
    throughput_bucket: Optional[int] = None,
    **kwargs: Any,
) -> None:
    ...
```

The asynchronous signature is unchanged; the proposed rejection of
`session_token` changes which arguments are accepted through `**kwargs`.

<a id="7---reading-database-properties"></a>
<a id="databaseproxyread"></a>

### `DatabaseProxy.read`

**Why the customer calls this API**

The customer wants the properties of the `sales` database, such as its ID
and current version marker, before performing another operation on it.

```python
database = client.get_database_client("sales")
properties = await database.read()

print(properties["id"])
print(properties["_etag"])
```

This reads the database's own properties, not the orders stored in its
containers.

**Proposed breaking change: reject previously ignored arguments**

As with deletion in `CosmosClient.delete_database`, the proposal removes arguments that legacy
Python accepted but ignored for this operation. These are Python wrapper
cleanup decisions, not Rust-driver limitations.

| Argument | Previous behavior | Proposed behavior |
|---|---|---|
| `session_token`, on both clients | Ignored for reading database properties. A non-`None` value produced a warning. | Raise `TypeError` whenever supplied, including `None`. |
| `populate_query_metrics`, on the synchronous client | Accepted positionally or by name but did not enable query metrics for this read. A non-`None` value produced a warning. | Remove the parameter and raise `TypeError` whenever supplied, including `False` or `None`. |

**Customer impact and migration**

The proposal removes `populate_query_metrics` from the synchronous API in
both forms:

```python
# Previous synchronous calls; both are rejected under the proposal.
properties = database.read(False)
properties = database.read(populate_query_metrics=False)

# Use this instead.
properties = database.read()
```

Likewise, remove an ignored session-token argument:

```python
# Previous asynchronous call.
properties = await database.read(session_token=token)

# Proposed call.
properties = await database.read()
```

The returned database properties do not change because an ignored argument
was removed. The breaking change is that the existing call now raises
`TypeError` until the customer removes that argument. This includes calls
that previously supplied `None` without receiving a warning.

After removing the synchronous query-metrics argument, `read()` accepts no
positional arguments. Supported optional settings must be named.

**Decision requested; approval is not recorded**

Approve or revise removal of `session_token` from both clients and
`populate_query_metrics` from the synchronous client, both positionally
and by name.

The asynchronous client never declared `populate_query_metrics`, but callers
could supply the keyword through `**kwargs`. The current implementation
rejects it; whether legacy async ignored or forwarded it remains unverified.
That rejection is not yet an approved removal decision.

**Asynchronous-client signature for review**

```python
async def read(
    self,
    *,
    initial_headers: Optional[dict[str, str]] = None,
    **kwargs: Any,
) -> CosmosDict:
    ...
```

`CosmosDict` is the dictionary-like result containing database properties
and exposing response headers through `get_response_headers()`.

The asynchronous signature is unchanged; the proposed rejection of
`session_token` changes which arguments are accepted through `**kwargs`.

## Container operations

<a id="8---creating-a-container"></a>
<a id="databaseproxycreate_container"></a>

### `DatabaseProxy.create_container`

**Why the customer calls this API**

The customer has a `sales` database and needs an `orders` container before
storing orders.

```python
from azure.cosmos import PartitionKey

container = await database.create_container(
    "orders",
    partition_key=PartitionKey(path="/tenant"),
)
```

The partition-key path `/tenant` identifies the order property used to
group orders by tenant.

The changes below are Python wrapper argument cleanup, not changes required
by a missing Rust-driver capability.

**Proposed breaking change: name optional settings**

Previously, the synchronous API accepted these optional settings
positionally after `id` and `partition_key`:

```text
indexing_policy, default_ttl, populate_query_metrics,
offer_throughput, unique_key_policy, conflict_resolution_policy
```

The asynchronous API already required optional settings to be named.

The proposal allows only `id` and `partition_key` positionally on both
clients. Customers may also supply those two arguments by name.

For example, this legacy synchronous call sets a default item lifetime of
86,400 seconds:

```python
container = database.create_container(
    "orders",
    PartitionKey(path="/tenant"),
    None,
    86400,
)
```

It becomes:

```python
container = database.create_container(
    "orders",
    PartitionKey(path="/tenant"),
    default_ttl=86400,
)
```

**Customer impact:** calls passing optional settings positionally now raise
`TypeError`. Naming those settings preserves the requested configuration;
the proposal does not remove the supported policies or throughput settings.

**Proposed breaking change: reject previously ignored arguments**

| Argument | Previous behavior | Proposed behavior |
|---|---|---|
| `session_token`, on both clients | Accepted by name through `**kwargs` but ignored for container creation. A non-`None` value produced a warning. | Raise `TypeError` whenever supplied, including `None`. |
| `populate_query_metrics`, on the synchronous client | Accepted positionally or by name but did not enable query metrics for creation. A non-`None` value produced a warning. | Raise `TypeError` whether supplied positionally or by name, including `False` or `None`. |

Both arguments are rejected under the proposal. Removing the argument is
the customer's migration step; raising `TypeError` is what the SDK does if
the customer continues to supply it.

For example:

```python
# Previous synchronous call.
container = database.create_container(
    "orders",
    PartitionKey(path="/tenant"),
    populate_query_metrics=False,
)

# Proposed call.
container = database.create_container(
    "orders",
    PartitionKey(path="/tenant"),
)
```

As with `CosmosClient.delete_database` and `DatabaseProxy.read`, legacy asynchronous handling of
`populate_query_metrics` through `**kwargs` remains unverified. The current
implementation rejects it, but that rejection is not yet an approved
removal decision.

**Missing or duplicate required arguments raise `TypeError`**

Both clients require `id` and `partition_key`. Previously, omitting one
could produce `KeyError`; the proposed behavior raises `TypeError`.

Supplying a required argument both positionally and by name is also
rejected before creation:

```python
container = await database.create_container(
    "orders",
    PartitionKey(path="/tenant"),
    id="archived-orders",
)
```

The customer must supply one container ID, not two. Code that catches
`KeyError` for missing arguments must instead catch `TypeError`.

**Decision requested; approval is not recorded**

Approve or revise the named-optional-argument requirement, rejection of
the verified ignored arguments, and consistent `TypeError` handling for
missing or duplicate required arguments.

**Asynchronous-client signature for review**

The expanded calling contract is shown below; the implementation currently
accepts `*args` and `**kwargs` and enforces these argument rules.

```python
async def create_container(
    self,
    id: str,
    partition_key: PartitionKey,
    *,
    indexing_policy: Optional[dict[str, str]] = None,
    default_ttl: Optional[int] = None,
    offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
    unique_key_policy: Optional[dict[str, str]] = None,
    conflict_resolution_policy: Optional[dict[str, str]] = None,
    initial_headers: Optional[dict[str, str]] = None,
    computed_properties: Optional[list[dict[str, str]]] = None,
    analytical_storage_ttl: Optional[int] = None,
    vector_embedding_policy: Optional[dict[str, Any]] = None,
    change_feed_policy: Optional[dict[str, Any]] = None,
    full_text_policy: Optional[dict[str, Any]] = None,
    global_secondary_index: Optional[
        Union[GlobalSecondaryIndexDefinition, dict[str, Any]]
    ] = None,
    return_properties: bool = False,
    **kwargs: Any,
) -> Union[ContainerProxy, tuple[ContainerProxy, CosmosDict]]:
    ...
```

The return remains a `ContainerProxy`, or a container client plus creation
properties when `return_properties=True`. The synchronous client follows
the same argument rules and is called without `await`.

<a id="9---creating-a-container-if-it-does-not-exist"></a>
<a id="databaseproxycreate_container_if_not_exists"></a>

### `DatabaseProxy.create_container_if_not_exists`

**Why the customer calls this API**

The customer's setup may run more than once. It needs an `orders` container
client whether the container already exists or must be created.

```python
from azure.cosmos import PartitionKey

container = await database.create_container_if_not_exists(
    "orders",
    PartitionKey(path="/tenant"),
    default_ttl=86400,
)
```

If `orders` is missing, the call creates it with the supplied settings. If
it exists, the call returns its container client without updating its
settings. For example, an existing default item lifetime of 3,600 seconds
remains unchanged; this call does not replace it with 86,400 seconds.

The changes below are Python wrapper argument cleanup, not changes required
by a missing Rust-driver capability.

**Proposed breaking change: use the argument rules from `DatabaseProxy.create_container`**

Both clients require `id` and `partition_key`. Only those two arguments may
be positional; optional settings must be named.

Previously, synchronous callers could write:

```python
container = database.create_container_if_not_exists(
    "orders",
    PartitionKey(path="/tenant"),
    None,
    86400,
)
```

The proposed call is:

```python
container = database.create_container_if_not_exists(
    "orders",
    PartitionKey(path="/tenant"),
    default_ttl=86400,
)
```

The asynchronous client already required named optional settings.

Missing required arguments now raise `TypeError` rather than `KeyError`.
Supplying either required argument both positionally and by name also
raises `TypeError`, as explained in `DatabaseProxy.create_container`.

**Proposed breaking change: reject previously ignored arguments**

| Argument | Previous behavior | Proposed behavior |
|---|---|---|
| `session_token`, on both clients | Ignored for the container-property read and creation. | Raise `TypeError` whenever supplied, including `None`. |
| `populate_query_metrics`, on the synchronous client | Accepted positionally or by name but did not enable query metrics for either the preliminary read or creation. | Raise `TypeError` whether supplied positionally or by name, including `False` or `None`. |

For example:

```python
# Previous synchronous call.
container = database.create_container_if_not_exists(
    "orders",
    PartitionKey(path="/tenant"),
    populate_query_metrics=False,
)

# Proposed call.
container = database.create_container_if_not_exists(
    "orders",
    PartitionKey(path="/tenant"),
)
```

**These argument checks happen before checking whether the container
exists.** Customers must remove the ignored arguments even when `orders`
already exists and no creation is needed.

The asynchronous `populate_query_metrics` question remains the same as in
`DatabaseProxy.create_container`: the current implementation rejects the keyword, but its legacy
handling through `**kwargs` remains unverified. That rejection is not yet
an approved removal decision.

**Decision requested; approval is not recorded**

Approve or revise applying `DatabaseProxy.create_container`'s argument rules and verified
ignored-argument removals to this API, including when the container already
exists.

**Asynchronous-client signature for review**

The expanded calling contract matches `DatabaseProxy.create_container`. The implementation
currently accepts `*args` and `**kwargs` and enforces the positional-argument
rules.

```python
async def create_container_if_not_exists(
    self,
    id: str,
    partition_key: PartitionKey,
    *,
    indexing_policy: Optional[dict[str, str]] = None,
    default_ttl: Optional[int] = None,
    offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
    unique_key_policy: Optional[dict[str, str]] = None,
    conflict_resolution_policy: Optional[dict[str, str]] = None,
    initial_headers: Optional[dict[str, str]] = None,
    computed_properties: Optional[list[dict[str, str]]] = None,
    analytical_storage_ttl: Optional[int] = None,
    vector_embedding_policy: Optional[dict[str, Any]] = None,
    change_feed_policy: Optional[dict[str, Any]] = None,
    full_text_policy: Optional[dict[str, Any]] = None,
    global_secondary_index: Optional[
        Union[GlobalSecondaryIndexDefinition, dict[str, Any]]
    ] = None,
    return_properties: bool = False,
    **kwargs: Any,
) -> Union[ContainerProxy, tuple[ContainerProxy, CosmosDict]]:
    ...
```

The return remains a `ContainerProxy`, or a container client plus the
existing or newly created container's properties when
`return_properties=True`. The synchronous client follows the same argument
rules and is called without `await`.

<a id="10---deleting-a-container"></a>
<a id="databaseproxydelete_container"></a>

### `DatabaseProxy.delete_container`

**Why the customer calls this API**

The customer wants to remove a test `orders` container and its stored orders
while keeping the `sales` database and its other containers.

```python
await database.delete_container("orders")
```

Success returns `None`. Unlike database deletion in `CosmosClient.delete_database`, this operation
removes only the selected container.

The changes below are Python wrapper argument cleanup, not changes required
by a missing Rust-driver capability.

**Proposed breaking change: reject previously ignored arguments**

| Argument | Previous behavior | Proposed behavior |
|---|---|---|
| `session_token`, on both clients | Accepted by name but ignored for container deletion. A non-`None` value produced a warning. | Raise `TypeError` whenever supplied, including `None`. |
| `populate_query_metrics`, on the synchronous client | Accepted positionally or by name but did not enable query metrics for deletion. A non-`None` value produced a warning. | Raise `TypeError` whether supplied positionally or by name, including `False` or `None`. |

**Customer impact and migration**

Previously, synchronous callers could supply an ignored query-metrics argument:

```python
database.delete_container("orders", False)

database.delete_container(
    "orders",
    populate_query_metrics=False,
)
```

Both calls become:

```python
database.delete_container("orders")
```

Likewise, remove the ignored session-token argument:

```python
# Previous asynchronous call.
await database.delete_container("orders", session_token=token)

# Proposed call.
await database.delete_container("orders")
```

The deletion does not change because an ignored argument was removed. The
breaking change is that an existing call now raises `TypeError` until the
customer removes that argument. Calls that previously supplied `None`
without receiving a warning are also affected.

Only the container target may be positional. Supported optional settings
must be named.

**Decision requested; approval is not recorded**

Approve or revise rejection of `session_token` on both clients and
`populate_query_metrics` on the synchronous client, whether supplied
positionally or by name.

The asynchronous client never declared `populate_query_metrics`, but
callers could supply it through `**kwargs`. As in `CosmosClient.delete_database`, the current
implementation rejects it, while its legacy handling remains unverified.
That rejection is not yet an approved removal decision.

**Asynchronous-client signature for review**

```python
async def delete_container(
    self,
    container: Union[str, ContainerProxy, Mapping[str, Any]],
    *,
    initial_headers: Optional[dict[str, str]] = None,
    **kwargs: Any,
) -> None:
    ...
```

The asynchronous signature is unchanged; the proposed rejection of
`session_token` changes which arguments are accepted through `**kwargs`.
The synchronous signature removes its positional-or-named
`populate_query_metrics` parameter.

<a id="12---listing-containers"></a>
<a id="databaseproxylist_containers"></a>

### `DatabaseProxy.list_containers`

**Why the customer calls this API**

The customer wants to see the containers in `sales`, such as `orders` and
`receipts`, and record the request charge for retrieving them.

The customer supplies a response hook: a function the SDK calls with response
information. The customer names that function `on_containers` in every example
below. These examples use the synchronous client.

```python
def on_containers(headers, results_iterator):
    print(headers.get("x-ms-request-charge"))

containers = database.list_containers(
    max_item_count=1,
    response_hook=on_containers,
)

for properties in containers:
    print(properties["id"])
```

`containers` is the results iterator. The loop fetches container properties,
not orders stored inside them. A service page is a group of returned results;
`max_item_count=1` requests one container per page, not one container in total.

**Shared timing change: report each successful service page**

These are Python wrapper response-hook timing and argument-contract changes,
not changes required by a missing Rust-driver capability.

This timing decision covers both clients for these four APIs only:

| API | Preserved response-hook arguments |
|---|---|
| `list_databases` and `query_databases` | `headers` |
| `list_containers` and `query_containers` | `headers, results_iterator` |

For container operations, `results_iterator` is the same iterator returned by
the method, not a list of the current page's results.

Assume `orders` and `receipts` arrive on separate pages. Previously:

```text
Customer app calls list_containers.
    SDK creates the results iterator.
    SDK calls on_containers before fetching any listing page.
        Headers may describe an earlier operation.
    on_containers returns.
SDK returns the iterator; customer app assigns it to containers.

Customer app starts the for loop.
    Iterator fetches page 1 -> delivers properties for orders.
    Iterator fetches page 2 -> delivers properties for receipts.
```

The proposed order is:

```text
Customer app calls list_containers.
SDK creates and returns the iterator; customer app assigns it to containers.
    No listing request has been sent and no hook has run.

Customer app starts the for loop.
    SDK receives page 1.
    SDK calls on_containers with page 1's headers and containers.
    on_containers returns.
    Iterator delivers properties for orders.

    SDK receives page 2.
    SDK calls on_containers with page 2's headers and containers.
    on_containers returns.
    Iterator delivers properties for receipts.
```

Each successful service page invokes the hook, including empty pages. Clearing
the old headers before an immediate invocation would avoid unrelated information,
but could not supply the listing's actual request charge or activity ID.
Per-page timing supplies that response information when available.

**Customer impact: start iteration outside the hook**

Previously, this customer hook could fetch and consume the results itself:

```python
def on_containers(headers, results_iterator):
    for properties in results_iterator:
        print(properties["id"])

containers = database.list_containers(response_hook=on_containers)
```

The loop inside the hook fetched `orders` and `receipts`. Only after the hook
finished did `list_containers()` return that same, already-consumed iterator.
Those results could be correct even though the initial headers were stale.

With per-page timing, the SDK has received a page when it calls the hook, but
has not yet finished updating the results iterator to deliver it. Starting
another loop over that iterator inside the hook can repeat requests and disrupt
the original iteration. Move result consumption outside the hook:

```python
def on_containers(headers, results_iterator):
    print(headers.get("x-ms-request-charge"))

containers = database.list_containers(response_hook=on_containers)

for properties in containers:
    print(properties["id"])
```

Both arguments remain, but that previous use of the iterator requires migration.
For all four APIs, customers must start iteration before expecting a hook
invocation and account for multiple invocations instead of one per method call.
On asynchronous clients the hook remains an ordinary `def` function; consume
results outside it with `async for`.

**Proposed argument changes**

| Argument | Previous behavior | Proposed behavior and migration |
|---|---|---|
| `max_item_count`, on the synchronous client | Accepted positionally or by name. | Require it by name: replace `list_containers(2)` with `list_containers(max_item_count=2)`. |
| `session_token`, on both clients | Ignored for container listing. A non-`None` value produced a warning. | Raise `TypeError` whenever supplied, including `None`; remove the argument. |
| `populate_query_metrics`, on the synchronous client | Accepted positionally or by name but did not enable query metrics for listing. | Raise `TypeError` whenever supplied, including `False` or `None`; remove the argument. |

The asynchronous client already required settings by name. The shared
`request_options` proposal in `CosmosClient.list_databases` also applies here.

**Decision requested; approval is not recorded**

Approve or revise the per-page hook timing and its customer migration across
the four APIs above, plus the argument changes for this API.
The current wrapper also rejects asynchronous `populate_query_metrics` and
`availability_strategy` on both clients; their removal remains unresolved
until their legacy behavior is established.

**Asynchronous-client signature for review:**

```python
def list_containers(
    self,
    *,
    max_item_count: Optional[int] = None,
    initial_headers: Optional[dict[str, str]] = None,
    response_hook: Optional[
        Callable[[Mapping[str, Any], AsyncItemPaged[dict[str, Any]]], None]
    ] = None,
    **kwargs: Any,
) -> AsyncItemPaged[dict[str, Any]]:
    ...
```

<a id="13---querying-containers"></a>
<a id="databaseproxyquery_containers"></a>

### `DatabaseProxy.query_containers`

**Why the customer calls this API**

The customer wants the properties of containers matching a condition,
rather than every container in `sales`. For example, it wants the container
named `orders`:

```python
containers = database.query_containers(
    "SELECT * FROM c WHERE c.id = @id",
    parameters=[{"name": "@id", "value": "orders"}],
)

async for properties in containers:
    print(properties["id"])
```

As explained in `CosmosClient.query_databases`, `@id` supplies a value separately from the SQL
text. This query returns container properties, not orders stored inside
the container. If `orders` exists, the loop prints `orders` once; otherwise,
it prints nothing. The query returns the matching container's properties;
the example prints only its `id` property.

**Why this needs API review**

These changes are Python wrapper cleanup and response-hook timing
corrections, not changes required by a missing Rust-driver capability.
They affect which arguments customer code may supply and when its
response hook runs. The separately listed unresolved option rejections
are not approved removals.

**Proposed breaking change: require the query and name optional settings**

Previously, the synchronous API allowed the query to be omitted and
accepted optional settings positionally. The asynchronous API already
required a query and named optional settings.

Both clients now require `query`, supplied positionally or by name. All
optional settings must be named.

```python
# Previous synchronous call.
containers = database.query_containers(sql, parameters, 2)

# Proposed call.
containers = database.query_containers(
    sql,
    parameters=parameters,
    max_item_count=2,
)
```

The page size still limits results per service page, not the total results.

**Requesting all containers remains available**

Previously, a synchronous customer could omit the query:

```python
containers = database.query_containers()
```

That call now raises `TypeError`. Use the API that directly expresses the
intention:

```python
containers = database.list_containers()
```

Explicitly passing `None`, without parameters, remains accepted:

```python
containers = database.query_containers(None)
```

This retrieves all containers without a SQL filter. It does not search for
a container whose ID is null.

**Response-hook timing follows `DatabaseProxy.list_containers`**

The SDK preserves both arguments:

```python
def on_containers(headers, results_iterator):
    print(headers.get("x-ms-request-charge"))

containers = database.query_containers(
    "SELECT * FROM c WHERE c.id = @id",
    parameters=[{"name": "@id", "value": "orders"}],
    response_hook=on_containers,
)

async for properties in containers:
    print(properties["id"])
```

The SDK calls the customer's `on_containers` function after each successful
service page, including empty pages, not before `query_containers()` returns.

`results_iterator` remains the same iterator returned by the method. Keep
both arguments and consume results outside the hook. `DatabaseProxy.list_containers` explains
the execution order and migration for customer code that previously consumed
results inside the hook.

**Proposed breaking change: reject previously ignored arguments**

| Argument | Previous behavior | Proposed behavior |
|---|---|---|
| `session_token`, on both clients | Ignored for container queries. A non-`None` value produced a warning. | Raise `TypeError` whenever supplied, including `None`. |
| `populate_query_metrics`, on the synchronous client | Accepted positionally or by name but did not enable query metrics for this operation. A non-`None` value produced a warning. | Raise `TypeError` whenever supplied, including `False` or `None`. |

```python
# Previous synchronous call.
containers = database.query_containers(
    sql,
    populate_query_metrics=False,
)

# Proposed call.
containers = database.query_containers(sql)
```

The current wrapper also rejects asynchronous `populate_query_metrics`,
plus `availability_strategy` and `enable_cross_partition_query` on both
clients. Their removal is not included in the ignored-option proposal
until their legacy behavior is established.

**Decision requested; approval is not recorded**

Approve or revise the required query argument, named optional settings,
and verified ignored-argument removals. The shared response-hook timing
decision in `DatabaseProxy.list_containers` and `request_options` proposal in `CosmosClient.list_databases` also
apply here.

**Asynchronous-client signature for review**

```python
def query_containers(
    self,
    query: Optional[Union[str, dict[str, Any]]],
    *,
    parameters: Optional[list[dict[str, Any]]] = None,
    max_item_count: Optional[int] = None,
    initial_headers: Optional[dict[str, str]] = None,
    response_hook: Optional[
        Callable[[Mapping[str, Any], AsyncItemPaged[dict[str, Any]]], None]
    ] = None,
    **kwargs: Any,
) -> AsyncItemPaged[dict[str, Any]]:
    ...
```

Use `async for`, without awaiting `query_containers()` itself. The synchronous
client follows the same argument rules and returns, and supplies to the hook,
an `ItemPaged[dict[str, Any]]`.

<a id="14---replacing-container-settings"></a>
<a id="databaseproxyreplace_container"></a>

### `DatabaseProxy.replace_container`

**Why the customer calls this API**

The customer wants to change settings on the existing `orders` container,
such as changing its default item lifetime from 3,600 to 86,400 seconds.
This API submits replacement container settings; it does not replace the
JSON contents of `order-42`.

The customer must identify the target separately from supplying its
replacement settings. For example, a target dictionary containing
`{"id": "orders", "defaultTtl": 3600}` selects `orders`; it does not automatically
carry that lifetime into the replacement. This distinction motivates explicit
named settings and the migration guidance below.

**Why the Python contract changes:** After `container` and `partition_key`, sync accepted
`indexing_policy`, `default_ttl`, `conflict_resolution_policy`, and
`populate_query_metrics` positionally, in that order. Async accepted only
`container` and `partition_key` positionally and required optional arguments
by keyword. Missing arguments could raise `KeyError`, duplicate arguments
were not rejected consistently, and metrics/session options could be accepted
with warnings rather than clear argument errors.

**Decision and reasoning:** Allow only `container` and `partition_key`
positionally on both clients; they may also be supplied by keyword.
All optional arguments must be passed by keyword (`name=value`). Raise
`TypeError` for missing or duplicate required arguments or extra positional
arguments. Reject `session_token` and `populate_query_metrics` whenever supplied,
including `None` or `False`. Both clients should have the same calling rules
and reject inapplicable settings before changing a resource.

**Customer migration:** Pass optional arguments by keyword, such as
`default_ttl=3600`, and remove retired keywords. Keep `etag`, `match_condition`,
and the existing two-argument response hook. The proxy result and `return_properties=True`
tuple remain unchanged. Include the policies the application wants to retain;
passing a properties dictionary as the target still supplies only its ID.

**Other public changes:** Removed `read_timeout` raises `TypeError` on both
execution paths, including `None`. Runtime HTTP-attempt limits are distinct.
`response_hook(headers, properties)` receives its own copies of the headers
and properties, including nested values. Editing those copies no longer
changes the returned properties or the SDK's saved headers. Valid response hook
objects are no longer skipped because the object itself evaluates to `False`;
this is not about a response hook returning `False`. A response hook error does not
cause the SDK to repeat the replacement.

**Illustration - select the target separately from replacement settings:**

```python
container, properties = database.replace_container(
    {"id": "orders", "defaultTtl": 3600},
    PartitionKey(path="/tenant"),
    default_ttl=86400,
    return_properties=True,
)
```

The target mapping selects `orders`; its `defaultTtl` is not used as the
replacement policy. The named `default_ttl=86400` supplies that setting.
Include the other policies the application wants to retain; do not treat a
target dictionary as an automatic merge of old settings.
Refer to creating a container (`DatabaseProxy.create_container`) for named policy
arguments and database creation (`CosmosClient.create_database`) for independent
callback copies and proxy/properties return forms. Unlike database creation,
replacement keeps supported ETag conditions.

**New contract (async-client signature):**

```python
async def replace_container(
    self,
    *args: Any,
    **kwargs: Any
) -> Union[ContainerProxy, tuple[ContainerProxy, CosmosDict]]:
    ...
```

<a id="15---reading-container-properties"></a>
<a id="containerproxyread"></a>

### `ContainerProxy.read`

**Why the customer calls this API**

The customer wants to inspect the `orders` container's configuration or
resource usage. `container.read()` returns the container's properties, not
the contents of `order-42`. The customer can also request additional
partition-range statistics or quota and usage information.

For example, an administration tool can inspect the configured partition-key
path and record the response's usage headers. The review must preserve those
requests and ensure a response callback cannot accidentally change the
properties returned to the customer or cached by the SDK.

**Why the Python contract changes:** Sync accepted `populate_query_metrics`,
`populate_partition_key_range_statistics`, and `populate_quota_info` as its
first three positional arguments, in that order. Async required optional
arguments by keyword. Inapplicable metrics/session settings were handled
inconsistently. Supplying quota/statistics options or an unused ETag alongside
a wildcard condition could unnecessarily switch a Rust-selected read to legacy
Python. A response hook could edit the same nested properties subsequently
returned to the caller and saved in the SDK's partition-key cache.

**Decision and reasoning:** Require all optional arguments by keyword
(`name=value`) on both clients. Reject `populate_query_metrics` and
`session_token` whenever supplied, including `None` or `False`; neither belongs
on this metadata read. Honor quota/statistics requests through the Rust driver;
`None` and `False` request no extra data. Remove only an unused ETag after
constructing the condition: `IfMissing` still sends `If-None-Match: *`, and
version-specific conditions retain their supplied ETag. Give the response hook
independent deep copies so observing or annotating a response cannot change
the SDK's local view of the container.

**Customer migration:** Pass supported options by keyword, for example
`container.read(populate_quota_info=True)`, and remove retired keywords.
Read requested statistics from `properties["statistics"]` and quota/usage from
`properties.get_response_headers()`. Keep `response_hook(headers, properties)`,
but do not rely on edits to either argument changing returned properties,
cached partition-key metadata, or SDK-owned headers. Such local edits never
changed the actual Cosmos DB container.

**Other public changes:** Reject removed `read_timeout` on both execution
paths, including `None`. Runtime HTTP-attempt limits are distinct. Unsupported Rust
settings now raise rather than silently change backends. Response hooks still
run synchronously after success, including callable objects that evaluate to
`False`; this concerns the object itself, not its return value. Header
isolation and false-valued callable support already worked and are preserved.
A response-hook error does not replay the read or populate the cache.
The result remains a `CosmosDict`; a missing container still raises
`CosmosResourceNotFoundError`.

**Illustration - ask for extra metadata without changing request implementation:**

```python
properties = container.read(
    populate_partition_key_range_statistics=True,
    populate_quota_info=True,
)
statistics = properties["statistics"]
headers = properties.get_response_headers()
```

Partition-range statistics describe the storage ranges used by the container;
quota/usage headers describe limits and consumption. `False` or `None` asks for
no additional information, rather than selecting legacy Python.
For wildcard conditions, `IfMissing` means send `If-None-Match: *`; an unused
ETag must not replace the `*` or change the selected implementation.
For example, if a hook edits its copy of
`properties["partitionKey"]["paths"]`, neither the returned properties nor the
SDK's saved partition-key definition changes. The deep-copy example is in
database creation (`CosmosClient.create_database`). Argument naming and socket-setting
rules follow reading database properties (`DatabaseProxy.read`).

**New contract (async-client signature):**

```python
async def read(
    self,
    *,
    populate_partition_key_range_statistics: Optional[bool] = None,
    populate_quota_info: Optional[bool] = None,
    priority: Optional[Literal["High", "Low"]] = None,
    initial_headers: Optional[dict[str, str]] = None,
    response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
    **kwargs: Any
) -> CosmosDict:
    ...
```

<a id="containerproxyscripts"></a>

### `ContainerProxy.scripts`

**Removed from the synchronous and asynchronous public surface, including
the legacy comparison backend.** This is an intentional release exclusion,
not unfinished Rust integration.

For example, `container.scripts` now raises `AttributeError` without reading
container metadata. There is no `ScriptsProxy` to construct directly: its
exports, modules, legacy connection operations, dedicated tests and scripting
sample paths have been removed. `TriggerType` and `TriggerOperation` are
removed too.

Calling an already-deployed UDF remains a different operation:
`container.query_items("SELECT VALUE udf.reviewBand(c.total) FROM c")`
uses the ordinary query path. Removing script management does not delete
saved service definitions or provide a replacement for stored-procedure
execution. No scripting parity work is required for this release.

<a id="36---excluding-the-public-system-key-property"></a>
<a id="containerproxyis_system_key"></a>

### `ContainerProxy.is_system_key`

**Review disposition:** Removed from synchronous and asynchronous clients,
including the legacy comparison backend. No implementation or parity work
is required for this excluded property.

**Why are we excluding it?**

The property tells a customer whether a container uses a legacy
system-defined partition key. Legacy partitionless/system-key container
compatibility is outside this release's scope.
No driver implementation is planned for this excluded compatibility.

For customer operations within the supported scope, this property provides
no necessary capability. An administration tool could use it to identify
an unsupported container, but that possible diagnostic use is not an
established customer requirement for retaining a public API.

Internal checks needed to recognize unsupported containers or preserve
supported partition-key behavior do not require a public property. The
remaining private partition-key normalizer reads metadata directly; it no
longer calls this public API. Shared metadata and null/missing-key handling
remain for their other callers.

Both property implementations and the dedicated property/cache parity suite
have been removed, together with the API snapshot declarations. There are
no dedicated sample callers to retain. Removal checks cover both clients
and backends; they do not claim support for legacy system-key containers.

**What changes for the customer?**

Accessing `container.is_system_key` now raises `AttributeError` before any
metadata request, including when attempting to await it on the asynchronous
client. Customer code must remove or revise that compatibility check for
the new release. This decision does not migrate existing data, enable
operations on excluded containers, or introduce an automatic legacy fallback.

Reconsider the public API only if a concrete supported customer scenario requires it.
This is a release-scope decision, not a request for new Rust driver support.

## Item operations and queries

<a id="17---creating-an-item"></a>
<a id="containerproxycreate_item"></a>

### `ContainerProxy.create_item`

**Why the customer calls this API**

The customer has accepted a new order and needs to store it in `orders`.
This API sends the order's JSON document to the service backend for creation.
It is not a request to replace an existing order with the same ID and
partition key.

The customer normally supplies an ID such as `"order-42"`, or explicitly asks
the SDK to generate one. For a container partitioned by `/id`, that generated
value also determines the partition key. The review must ensure both values
agree, without changing the customer's input dictionary, before the write
is sent.

**Bounded lost-response verification:** On October 18, 2026 (UTC), the selected
isolated SDK snapshot cut a real create response after 20,000 forwarded bytes.
Sync and async recorded transport-generated `503/20003`, then duplicate
`409/0`, and raised `CosmosResourceExistsError`. Independent and subsequent
same-client reads returned the complete stored order. This demonstrates
an ambiguous create outcome, not matched legacy fault parity or validation
of concurrent SDK changes. The local testing guide records the exact setup
and retained evidence; broader retry and live-account requirements remain.

The test-harness review follow-up
repeated this outcome after fixing observation and process-cleanup races.
It strengthens the local evidence without changing the API decision.

**Why the Python contract changes:** Sync accepted optional positional arguments while async
required keywords. Query metrics and conditional options were inconsistently
warned about, validated, or forwarded. Automatic IDs could be generated after
partition-key extraction, producing an inconsistent request for `/id` partition
keys, and the Rust path could modify the caller's body. Response hooks could
modify SDK-owned data, and metadata lookup could escape the create timeout.

**Proposed contract, implemented for review:** Require all arguments except `body` by keyword.
Reject `populate_query_metrics`, `etag`, and `match_condition` whenever supplied,
including `None` or `False`. Copy and validate the body before metadata lookup:
require a mapping, apply the shared resource-ID rules, and reject non-JSON
values and non-finite numbers. Without automatic generation, an ID must be a
non-empty string. Automatic generation remains opt-in and replaces a missing
or false-valued ID on the copy before partition-key extraction. The partition
key and serialized body use the same nested snapshot.

**Response contract:** Return a `CosmosDict`; with `no_response=True`, it is
empty but retains response headers. Per-call `no_response=False` overrides a
client default that suppresses write bodies. Invoke success hooks once with
independent headers and a deep-copied `CosmosDict`, including an empty body for
suppressed responses. Reject a non-callable hook before metadata lookup or
writing, rather than saving the order and only then reporting a callback
error. Honor false-valued callable objects. Hook exceptions
propagate outside retries and do not replay the write. A service 409 remains
`CosmosResourceExistsError`.

**Timeout and encoding:** A supported explicit `timeout` is one budget for
metadata and create, including metadata-cache lock waits. Remaining durations
below one second are not rounded up. The
[first-use acquisition wait](#first-use-initialization-deadlines) uses that same
budget without forcibly stopping the shared worker. The client's
`enable_compact_utf8_item_writes` option is honored by Rust-backed create,
upsert, replace, and patch serialization; its default remains `False`, and
metadata/query encoding is unchanged.

**Shared request settings:** The customer may keep a reusable option mapping:

```python
settings = {"timeout": 2, "responsePayloadOnWriteDisabled": True}
created = orders.create_item(
    {"id": "order-42", "customerId": "customer-17"},
    feed_options=settings,
    no_response=False,
)
```

For this `/customerId` container, the call uses a two-second budget but
requests the returned order body. The mapping is not changed. A supplied
`request_options` takes precedence over `feed_options`, even when empty or
`None`; explicit `timeout=None` clears a nested timeout. Both clients now
preserve this selection instead of accidentally hiding `feed_options` behind
an empty mapping. This correction and early hook validation are Python wrapper
fixes, not missing Rust driver capabilities.

**Customer migration:** Remove trigger options; pass indexing directives by keyword;
remove retired metrics and condition arguments. Supply a valid ID or opt into
generation and obtain the generated ID from the returned item, not by expecting
the input dictionary to change. If the generated ID is needed, request a
response body rather than combining automatic generation with `no_response=True`.
Do not rely on hook edits to modify returned data or SDK state.

**Illustration - generate the ID before choosing the partition:**

```python
# Assume this container's partition key is /id.
body = {"description": "new order"}
created = container.create_item(body, enable_automatic_id_generation=True)
generated_id = created["id"]
assert "id" not in body  # The SDK modifies its own copy, not this dictionary.
```

If the generated ID is `"generated-123"` (an illustrative value), both the
stored body's ID and the extracted partition-key value must be
`"generated-123"`. Generating it after partition-key extraction could send
inconsistent values. Without generation enabled, provide a non-empty string
ID. A non-JSON value such as a Python `set`, or a number such as `float("nan")`,
fails validation before metadata lookup.

```python
result = container.create_item(
    {"id": "order-43", "tenant": "tenant-a"}, no_response=True
)
assert not result
headers = result.get_response_headers()  # Empty body does not mean no headers.
```

This second example assumes a `/tenant` container. The service backend still
receives the full order; only its returned body is suppressed. The available
headers can still supply the request charge and activity ID.

**Remaining compatibility requirements**

Behavior during partition splits and under different account configurations
remains an open compatibility question.

| Customer need | Difference and required decision or work |
|---|---|
| Continue writing to an older container created without a partition key | Excluded from the Rust-backed release. The driver team has no current implementation plans; reconsideration depends on customer need. Existing data is not migrated by changing SDKs; customers need an explicit compatibility plan. |
| Decide whether to retry after the result of a create is uncertain | Legacy exposes a write-retry opt-in for these failures. The driver can retry creates without the equivalent per-write control, while the Rust item path rejects non-`None` `retry_write`, including zero. The driver must provide the control or the changed retry contract needs approval. |
| Keep writing after a container is recreated under the same name | With `/customerId` cached, recreate the container with `/region` and submit `{"id":"order-42","region":"West US"}` without `customerId`. Legacy recovery re-extracts this undefined key; the Rust driver refreshes metadata but retains the old key. The request can fail with HTTP 400 rather than recover using the new key. Recovery after container recreation remains an open compatibility requirement. |
| Bound connection setup or response waiting for this create | Connection and complete HTTP-attempt limits belong to `CosmosRuntime`; supported `timeout` bounds the overall operation. Legacy per-call transport overrides and read-inactivity timers are excluded by design, not pending driver support. |
| Start another eligible regional write while the first remains slow | Legacy can hedge writes with write-retry opt-in and suitable writable regions. The Rust driver does not hedge document creates. Accepting `availability_strategy` in Python does not preserve that behavior; driver support or an approved availability change is needed. |
| Read all service response headers | The driver retains selected fields, not the original complete map. Neither `get_response_headers()` nor a copied success-hook argument can recover a discarded header, including when the response body is suppressed. |
| Inspect or modify the raw outgoing request | The Rust path rejects the raw request callback. The driver needs a supported interception capability before our binding can restore it. Static custom headers and parsed success hooks are not equivalents. |

**Illustration - a failed return does not prove the order was not saved**

```text
Service backend saves order-42.
Its success response is lost.
A repeated create uses the same ID and partition key.
The service backend returns 409 because that item now exists.
```

The customer sees `CosmosResourceExistsError`, even though the earlier attempt
may have saved the order. This does not mean there are two orders with the same ID
and partition key. Nor does any 409 prove that the existing order contains
this call's intended data. Timeout or async cancellation also cannot undo a
write already accepted by the service backend.

**Preliminary requests have their own consequences**

Before sending the order, the Rust driver defaults to obtaining the physical
partition map: the range information used to route requests within `orders`.
If it cannot obtain a usable map, create can fail before sending the order.
The original metadata error can be replaced by a generic topology-resolution
failure, losing the distinction between permission and temporary service
failures. The driver must preserve the cause and the binding must return it
to Python. The binding now explicitly selects lazy loading, so container
resolution does not take that eager path. Loading is deferred until an
operation needs the map; its cost and possible failure do not disappear.
This binding-wide policy preserves the previous resolution behavior and is
not a new per-call option. The eager error-loss gap remains in the driver.

The binding forwards create's exclusions and remaining timeout to container
resolution, but not the item's session token, triggers, custom headers,
response suppression or per-call availability strategy. In particular,
`availability_strategy=False` on the create is not a promise to disable
separately governed metadata hedging.

**Other differences must not be misclassified**

For create, legacy accepted `initial_headers` but did not forward that mapping
to the outgoing request. Rust forwards ordinary custom headers and rejects
overrides of `Accept`, `Cache-Control`, `User-Agent` and `x-ms-version`.
The rejection can break an existing call, but it does not remove a working
legacy create-header override.

Customers may need to preserve imported text in an order's `note`.
An **unpaired surrogate** is one half of a Unicode surrogate pair without its
matching half. Legacy Python can serialize it as a JSON escape:

```json
{"id":"order-44","customerId":"customer-17","note":"\ud800"}
```

The binding previously rejected this unrelated `note` while extracting
`customerId`. That binding defect is fixed: it validates the complete JSON
syntax, decodes only the values needed for the partition key and item ID,
and passes the original body bytes to the Rust driver.

```text
Partition-key value -> "customer-17"
Outgoing note       -> "\ud800", unchanged rather than replaced
```

The correction applies to synchronous and asynchronous create, upsert and
replacement. It does not accept malformed JSON or make an unpaired surrogate
representable in the actual item ID or selected partition-key string.
That narrower string restriction remains a compatibility boundary to resolve,
not approval to rewrite customer data. Live comparison with legacy is still
needed to establish service acceptance and returned content for the unrelated
escaped value. The fixed unrelated-field defect needs no breaking-change
approval.

`raw_response_hook` is removed from both backends; supplying it raises
`TypeError`, including when its value is `None`. It formerly received a raw pipeline
response object, rather than the parsed headers/body given to `response_hook`.
No equivalent raw hook is planned in Rust. Use supported results, response
headers, OpenTelemetry, and diagnostic strings for information, subject to
their documented coverage. The shared raw-hook decision below preserves
the ordinary `response_hook` contract.

**New contract (async-client signature):**

```python
async def create_item(
    self,
    body: dict[str, Any],
    *,
    indexing_directive: Optional[int] = None,
    enable_automatic_id_generation: bool = False,
    session_token: Optional[str] = None,
    initial_headers: Optional[dict[str, str]] = None,
    priority: Optional[Literal["High", "Low"]] = None,
    no_response: Optional[bool] = None,
    retry_write: Optional[int] = None,
    throughput_bucket: Optional[int] = None,
    availability_strategy: Optional[Union[bool, dict[str, Any]]] = None,
    response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
    **kwargs: Any
) -> CosmosDict:
    ...
```

**Review disposition:** Creation remains partially migrated. The shared driver
integration is complete; the compatibility requirements above and service-level checks
for account-dependent session behavior, uncertain write outcomes,
recreation and metadata failures remain open. This entry is self-contained
for board review; it does not record approval of the proposed changes or
removal of unsupported behavior beyond the explicitly excluded features.
Trigger invocation is excluded rather than waiting on a service-parity check.

<a id="16---reading-an-item"></a>
<a id="containerproxyread_item"></a>

### `ContainerProxy.read_item`

**Why the customer calls this API**

The customer wants to display `order-42` and already knows its ID and partition
key value, `"tenant-a"`. This API reads that specific item without asking the
customer to write a query. The ID and partition key together identify the
order. The examples use `container` for an `orders` container partitioned by
`/tenant`.

If the customer already has a copy, it can also ask for the body only when
the order has changed since its saved ETag, the service backend's version
marker. The review must distinguish that unchanged response from an ordinary
order body and keep the read's callback and timeout behavior consistent.

**Why the Python contract changes:** Sync accepted positional query metrics and post-trigger
arguments while async required optional arguments by keyword. Inapplicable
metrics were warned about or consumed inconsistently. Hook arguments could
refer to the same dictionaries as the returned item and saved response
headers, allowing the callback to change them. Looking up container properties
could also run outside the customer's requested read timeout budget.

**Proposed contract, implemented for review:** Keep only `item` and `partition_key` positional.
Reject `populate_query_metrics` by presence, including `None` and `False`, on
both clients. Validate conditions before metadata lookup,
copy caller options, and consume unused ETags only after preserving wildcard
conditions. Give the success hook independent headers and a deep-copied
`CosmosDict`, including an empty `CosmosDict` for 304. Invoke false-valued
callable objects normally; propagate callback errors without replaying the read.

**Corrections that preserve customer intent**

These are Python wrapper/binding fixes, not requests to remove a driver
capability:

| Problem | Corrected behavior |
|---|---|
| `feed_options` could be hidden behind an empty `request_options` mapping. | Use `feed_options` when `request_options` is absent. A supplied `request_options`, including `{}` or `None`, still wins. Recognized explicit options override nested settings; the required partition-key argument wins over a nested key. |
| An invalid response hook failed only after the read. | Reject non-callable hooks before metadata or item execution. `response_hook=False` raises `TypeError`; omit the hook or pass `None` instead. |
| A per-read consistency setting could be overwritten by the driver's client setting. | Typed read-strategy selection fixes precedence and cached-session-token selection for that strategy, but does not establish parity for all five ordinary consistency levels. The semantic correction remains open; see below. |
| Per-read `availability_strategy=True` replaced the client's configured hedge threshold with the default. | Preserve the client's first threshold, as legacy does. A client configured for 20 ms keeps 20 ms, not 500 ms. With no configured client strategy, `True` uses 500 ms; `False` disables the item strategy and an explicit dictionary supplies its own threshold. |

For example, with a client configured for Session consistency:

```python
order = container.read_item(
    "order-42", partition_key="tenant-a",
    request_options={"consistencyLevel": "Eventual"},
)
```

The binding selects the Eventual read strategy for this read without changing
the client or preliminary metadata settings. Omitting a per-read override
preserves the client's choice. That precedence correction is implemented;
preserving all five ordinary Cosmos consistency levels is not established.

**Open consistency gap:** Both clients translate ConsistentPrefix to the
Eventual strategy and BoundedStaleness to LatestCommitted. These strategies
override ordinary consistency rather than represent those levels directly.
The earlier parity claim is withdrawn. LatestCommitted behaves like the
account default on Strong or Bounded Staleness accounts, so this is not proof
that an existing account bound is removed. On weaker accounts it requests a
region-local quorum read, not a cross-region staleness bound.

Simply retaining `x-ms-consistency-level` and selecting the Default strategy
does not fix the pinned driver: Gateway V2 encoding and automatic session-token
selection still resolve from account settings. The driver needs a supported
ordinary-level path, and the binding must use it without substituting
strategies. Writes remain account-governed. No runtime fix is included in this
review; [Gap 8](V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-8) records ownership,
pinned evidence and required legacy-versus-Rust comparisons.

**Conditional results:** `IfModified` uses If-None-Match; an unchanged item
returns an empty `CosmosDict` on 304. If-Match on item GET is service-enforced,
not a client-side version comparison: preserve 200 if that is what the service
returns, and preserve a real service 412 as `CosmosAccessConditionFailedError`.
Do not promise that stale If-Match on GET always fails with 412.

**Customer migration:** Pass conditions by keyword and remove retired query
metrics and trigger arguments. Trigger inputs are rejected on the Rust-backed
path; they are not silently omitted. Do not rely on modifying hook arguments to
change returned items or SDK state. Hook bodies are always `CosmosDict` objects
on success, including the empty 304 result.

**Timeout scope:** An explicit supported per-call `timeout` covers metadata and
the point read together, including the legacy metadata-cache lock. Initial
durations must be finite non-boolean numbers of at least one second and less
than `2**64` seconds; the platform timer can further constrain extreme values.
A remaining sub-second budget is honored rather than restarted or rounded up.
Expiry raises `CosmosClientTimeoutError`.

**Illustration - an unchanged item is not an ordinary item body:**

```python
from azure.core import MatchConditions

item = container.read_item(
    "order-42",
    partition_key="tenant-a",
    etag=previously_read_etag,
    match_condition=MatchConditions.IfModified,
)
```

If the service reports HTTP 304 ("not modified"), `item` is an empty
`CosmosDict`, still able to expose headers. Do not immediately assume
`item["id"]` exists; keep the customer's cached order instead.

With `timeout=5`, spending 2 seconds obtaining container metadata leaves
approximately 3 for the item read, not a fresh 5. Waiting for the legacy
metadata-cache lock consumes time too. `timeout=None` inherits the client
default and overrides a nested timeout; separate transport settings still
apply. The [acquisition wait](#first-use-initialization-deadlines) is bounded;
Python parsing and synchronous callback code are not forcibly interrupted at
every instruction. The async client requests
cancellation of pending binding work, but cannot guarantee immediate
cancellation of work already received by the service backend.

**Verified response-stall behavior**

On October 17, 2026, sync and async Rust-backed reads with `timeout=3`
raised `CosmosClientTimeoutError` after approximately 3.016 seconds when
Toxiproxy stopped downstream traffic from the installed emulator. The test
identified the existing connection used by a successful warm read and
observed returning traffic on that connection within 4-6 milliseconds,
before later reconnects. After fault removal, a new read succeeded using
the same client, without legacy fallback.

This verifies the overall read budget and recovery for the isolated driver
`84e2bb66c9911fa730dc9756c8fc3f9612456344` snapshot. It does not establish
legacy-versus-Rust parity under the same network fault, per-call transport
timeout support, or response-inactivity timeout behavior. The worktree's
async binding adapter changed concurrently and is outside this evidence.
The API's partial migration status and unrelated requirements remain unchanged.

**Verified single-reset recovery**

A separate October 17, 2026 test on the same isolated snapshot reset the
established read connection, then removed the fault before replacement traffic
proceeded. Both sync and async interrupted calls returned the order within
their original three-second budget, with exactly two recorded attempts:
transport-generated `503/20003`, then successful `200/0`. This establishes
recovery within that read, not merely success on a later call. Subsequent
reads using the same client also passed.

This does not guarantee recovery from persistent resets, change retry
eligibility for writes, or close the remaining migration requirements.

**Verified controlled response delay**

On October 17, 2026, the same isolated snapshot returned the expected order
with 500 milliseconds of added downstream latency in about 0.508 seconds
for sync and 0.509 seconds for async. With five seconds of added delay,
both reads raised `CosmosClientTimeoutError` near their original three-second
budget. No-fault controls and subsequent same-client reads passed.

The measured delay distinguishes the wait after returning traffic on the warmed connection from
setup time and emulator processing. Fault removal runs after the measured
read and has a separate management timeout; it does not extend the customer's
budget. This remains local, Rust-only snapshot evidence, not verification of
concurrent SDK changes, matched legacy parity, bandwidth limits, or response
inactivity. The API's partial migration status is unchanged.

**Verified deadline despite response progress**

The bandwidth run completed on October 18, 2026 (UTC) using the same isolated
snapshot. With a 64,000-byte receipt and a 64,000-byte/second downstream limit,
sync and async reads returned the complete order in about 1.041 and 1.033
seconds. At 16,000 bytes/second, they raised `CosmosClientTimeoutError` in
3.017 and 3.016 seconds despite repeated forwarding towards the SDK.

The run recorded 30 encrypted forwarding events on each warmed read connection before
timeout, partial transferred bytes, and successful subsequent reads using
the same clients. This supports the overall operation budget under the
tested conditions, not a response-inactivity or streaming contract. It
does not validate concurrent SDK changes, establish matched legacy fault
parity, or close remaining migration requirements.

**Verified recovery after a response cutoff**

On October 18, 2026 (UTC), the same isolated snapshot recovered a read after
exactly 20,000 encrypted response bytes were forwarded and the established
connection closed. Controlled fault removal allowed the retry to proceed.
The original sync and async calls returned the complete order and receipt
in 0.092 and 0.115 seconds, with exactly two data-plane attempts:
transport-generated `503/20003`, then `200/0`.

The run recorded the byte count, end-of-stream, replacement ordering, controls, and
subsequent same-client success. It does not expose the underlying body-read
error or establish a particular HTTP/JSON parsing stage. This is bounded,
local, Rust-only evidence, not validation of concurrent SDK changes or
matched legacy parity; partial migration status remains unchanged.

**Verified failure while the response cutoff remains active**

On October 18, 2026 (UTC), the same isolated snapshot raised
`ServiceResponseError` in 0.271 seconds for sync and 0.188 seconds for async.
Each call retained eight transport-generated `503/20003` attempts. Separately,
the SDK-facing observer recorded 20,000 bytes and end-of-stream on the
warmed connection and seven replacements. Replacement forwarding was not
gated, and the fault remained configured until after the call ended.

The persistent-cutoff record
records controls, subsequent same-client success, and cleanup. This proves
bounded terminal transport failure, not expiration of the three-second
deadline or a public eight-attempt retry guarantee. Local, snapshot-only,
and no-matched-legacy-parity limits remain; migration status is unchanged.

**Execution and preliminary requests**

The synchronous read starts during the call; the asynchronous read starts when
its coroutine runs. There is no iterator or continuation token. The binding
resolves the container through the Rust driver before constructing the item
GET. Cached metadata can avoid a lookup; retries and eligible regional attempts
can add requests. The Python wrapper does not replay a failed Rust read
through legacy Python.

Starting another regional attempt before an earlier one finishes is called
hedging. It can shorten a slow read but can also consume additional service
work.

Read behavior during partition splits remains an open compatibility question.

The physical partition map is the range information used for routing.
Although the driver defaults to loading it during container resolution, the
binding explicitly selects lazy loading: obtain it when an operation needs it.
This preserves the previous resolution behavior but can defer loading cost
to the first operation needing the map. The driver's eager-path error-loss
requirement below is not a path selected by this binding.

The binding forwards the read's exclusions and remaining timeout to container
resolution, not its item conditions, session token, custom headers, cache-age
limit, triggers or per-call availability strategy. A per-read
`availability_strategy=False` is not a whole-call guarantee against separately
governed metadata hedging.

**Remaining compatibility requirements**

| Customer need | Difference and required work or decision |
|---|---|
| Read an order in an older partitionless/system-key container | Excluded from the Rust-backed release. The driver team has no current implementation plans; reconsideration depends on customer need. Null and undefined keys are not substitutes for the legacy empty-key representation. See the shared older-container decision below. |
| Limit connection setup or response inactivity for this read | Configure connection and complete HTTP-attempt limits on `CosmosRuntime`; supported `timeout` bounds the overall operation. Legacy per-call transport overrides and read-inactivity timers are excluded by design, not pending driver support. |
| Try additional regions while earlier read attempts remain slow | The release supports threshold-only hedging with one alternate. Explicit `threshold_steps_ms` is rejected rather than discarded; progressive third/later hedges are intentionally excluded. |
| Obtain every original service response header | A generic success-response header map is excluded by design. The wrapper preserves the available modeled fields; copying hook arguments cannot restore an omitted original header. This is not an outstanding request to preserve every success header. |
| Inspect throttle retry counts and accumulated waiting | The driver contract and binding mapping need clarification. These SDK-added values are not original service headers. |
| Inspect or modify the raw outgoing request | `raw_request_hook` is removed from both backends and raises `TypeError`. Use supported options/static headers for configuration and supported tracing/diagnostics for information. Arbitrary prepared-request mutation is not preserved. |
| Inspect the raw pipeline response object | `raw_response_hook` is removed from both backends and raises `TypeError`. Use supported results, headers, tracing, and diagnostics. These do not reproduce the pipeline response object. |
| Distinguish a permission failure from a temporary failure during physical-map loading | Eager container resolution can discard the underlying metadata error and return a generic topology-resolution failure. A generic error does not tell the customer whether to repair permissions or retry a temporary failure. Preserving that distinction remains required. |

For the hedging example, assume four eligible regions and unfinished earlier
attempts. Legacy can start attempts at 0, 20, 30 and 40 milliseconds with an
initial 20-ms threshold and a 10-ms step. Rust does not start a third attempt
merely because the first two remain slow. These are illustrative timings,
not a latency guarantee. Extra attempts can consume service work.

**Accepted input is not proof of working legacy behavior**

The retained legacy item-read path accepted `initial_headers` but did not
forward that mapping. Rust forwards ordinary custom headers and rejects
overrides of `Accept`, `Cache-Control`, `User-Agent` and `x-ms-version`.
That rejection can break an existing call, but does not remove a working
legacy item-read override.

A positive `max_integrated_cache_staleness_in_ms` is forwarded as a cache-age
header for an appropriately configured dedicated gateway. Zero currently
emits no header on these paths; it is not a cache-bypass request. Real cache
freshness and the interaction with conditional reads remain service-level
verification requirements. Forwarding priority and throughput-bucket headers
likewise does not establish their service effects. Trigger options and trigger
header overrides are excluded, not forwarded.

**Keep read requirements separate from create requirements**

Reads legitimately use session tokens and retry without a write-retry opt-in.
They already receive the customer's partition key, so they do not need to
extract it from a write body after container recreation. The driver supports
eligible name-based recreation recovery; resource-ID addresses and explicit
tokens restrict retargeting. Do not classify every recreation as unsupported.
The point-read capability is in the Rust driver itself, not only the separate
higher-level Rust client.

**New contract (async-client signature):**

```python
async def read_item(
    self,
    item: Union[str, Mapping[str, Any]],
    partition_key: PartitionKeyType,
    *,
    etag: Optional[str] = None,
    match_condition: Optional[MatchConditions] = None,
    session_token: Optional[str] = None,
    initial_headers: Optional[dict[str, str]] = None,
    max_integrated_cache_staleness_in_ms: Optional[int] = None,
    priority: Optional[Literal["High", "Low"]] = None,
    throughput_bucket: Optional[int] = None,
    availability_strategy: Optional[Union[bool, dict[str, Any]]] = None,
    response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
    **kwargs: Any
) -> CosmosDict:
    ...
```

**Review disposition:** Reading an item remains partially migrated. The
Python/binding corrections do not close the driver requirements or approve
removal of unsupported behavior. The shared driver integration is complete; live checks
for resource addressing, caching, regional behavior and metadata failures
remain pending. This is a draft for board review, not recorded approval.

<a id="18---reading-known-items"></a>
<a id="containerproxyread_items"></a>

### `ContainerProxy.read_items`

**Why the customer calls this API**

The customer needs several known orders for a single view and already has
each order's ID and partition key. This API accepts those pairs and returns
the matching items, rather than requiring the customer to issue each read
separately.

For example, `("order-42", "tenant-a")` and `("order-42", "tenant-b")` identify
different orders. The review must preserve that distinction and explain how
result order, repeated pairs, and missing items affect the returned list.

**Why the Python/binding behavior needs correction**

The customer needs the right order for each `(ID, partition key)` pair.
Matching by ID alone could confuse tenants and lose repeated input
occurrences. Some partition keys were represented incorrectly in requests,
and the reported charge could omit earlier query pages. A response callback
could also change the data eventually returned to the customer.

The input checks and timeout handling need consistent rules too. For example,
an empty list should not fetch container properties, and waiting for another
read to finish should consume the same timeout budget as the read itself.
These are Python/binding corrections, not requests to remove the API.

**Input rules and bounded concurrency**

Keep only `items` positional. Copy the inputs and request options, validate
the `(ID, partition key)` pairs before requesting container properties, and
check the number of key components once the container definition is available.

**Concurrency** means how many pieces of work may run together.
`max_concurrency` must be a positive integer, not a boolean. `None` retains
the async default of five or the synchronous executor's default. An
**executor** schedules synchronous work; customers can supply their own.
That does not make an invalid `max_concurrency` value acceptable.

The current combination of individual reads and queries is retained while
these behaviors are corrected. Changing its request count and performance
needs a separate decision; the remaining Rust-only integration is explained
below.

**Response contract:** Return a `CosmosList` in input order, matching by both ID
and the full typed partition key. Return one item per occurrence of an existing
pair, including duplicates; omit missing items. Sum available point-read and
query-page request charges, including empty continuation pages and point-read
404 responses. This is not separate accounting for all metadata or failed attempts.
Do not return partial results on other failures; unresolved routing is an error.

Empty input performs no network calls and returns an empty list with empty
headers. A supplied success hook runs once, including for empty input, with
independent headers and a deep `CosmosList` snapshot. `response_hook=None` means
no callback; false-valued callable objects are honored. Callback exceptions
propagate unchanged without replaying work. Hooks remain supplied through
`**kwargs`, rather than a new explicit signature parameter.

**Timeout contract:** A supported explicit `timeout` covers the whole call:
obtaining container and routing information, waiting for access to shared
SDK data, queued work, and all item reads and query pages. The SDK honors a
remaining fraction of a second rather than restarting or rounding up the
budget. Async failure/cancellation cancels outstanding work and waits for
it to stop.
Sync cancels pending work and leaves caller-owned executors open; already-running
synchronous requests may finish later. The
[first-use acquisition wait](#first-use-initialization-deadlines) uses the same
remaining budget without cancelling shared initialization.

**Customer migration:** Supply complete partition keys and valid positive
concurrency values, or omit concurrency to use its default. Remove duplicate
input pairs if one result per distinct item is desired. Match responses using
ID plus partition key, not ID alone or input position. Do not rely on input
mutation, hook edits to returned data, metadata requests for empty input, or a
separate timeout per chunk.

**Illustration - the partition key is part of item identity:**

```python
items = container.read_items([
    ("order-42", "tenant-a"),
    ("order-42", "tenant-b"),
    ("order-42", "tenant-a"),
    ("missing", "tenant-a"),
])
```

Assume the first two distinct items exist and `"missing"` does not. The result
contains tenant A's item, tenant B's item, then tenant A's item again, in that
order. It contains three entries, not two; duplicate input occurrences are
preserved. Matching by ID alone would confuse the two tenants. Missing items
are omitted, so do not zip the results blindly with the original input list.

| Input or response | Current observable result |
|---|---|
| `items=[]` | Empty result and headers, no network calls; supplied hook runs once |
| `max_concurrency=0` or `True` | Validation error before metadata lookup |
| Two data pages cost 2 and 3 RU, an empty continuation page costs 1 | Available charges sum to 6, not just the final page's 1 |
| One non-404 request fails | Raise the error rather than return a misleading partial list |

One timeout covers waiting work as well as running requests; it is not
renewed for each group of items. Refer to reading an item (`ContainerProxy.read_item`) for the shared-budget example
and database creation (`CosmosClient.create_database`) for hook isolation, here applied
to a `CosmosList` (a list with response headers). Async cancellation waits for
outstanding work to stop; already-running sync requests may finish later.
Charge summation is not a promise to include every metadata request or failed
attempt.

**Contract (async-client signature, unchanged):**

```python
async def read_items(
    self,
    items: Sequence[Tuple[str, PartitionKeyType]],
    *,
    max_concurrency: Optional[int] = None,
    consistency_level: Optional[str] = None,
    session_token: Optional[str] = None,
    initial_headers: Optional[dict[str, str]] = None,
    excluded_locations: Optional[list[str]] = None,
    priority: Optional[Literal["High", "Low"]] = None,
    throughput_bucket: Optional[int] = None,
    availability_strategy: Optional[Union[bool, dict[str, Any]]] = None,
    **kwargs: Any
) -> CosmosList:
    ...
```

**Remaining integration and capability gaps**

The current implementation groups requested items by physical partition and
divides each group into chunks. A one-item chunk can use a Rust point read;
multi-item chunks still use legacy Python queries. For example, when two
requested orders share a physical partition, a successful call can still
depend on that retained query path. It is not evidence of a complete Rust-only
implementation. Replacing this coordination is Python/binding work; changes
to its request count or performance need a separate decision.

Older-container partition-key handling remains unresolved, as explained in
the shared section "Older containers need their existing partition-key
representation". Original response headers outside the driver's selected
fields can also be lost. Neither limitation is an approved exclusion.
This entry is a draft for board review, not recorded board approval.

<a id="19---reading-every-item"></a>
<a id="containerproxyread_all_items"></a>

### `ContainerProxy.read_all_items`

**Why the customer calls this API**

The customer needs to process every item in `orders`, for example to produce
an export, without filtering by a query or knowing the order IDs in advance.
This API returns an iterator that fetches results in pages rather than
loading the whole container into one list.

After processing a page containing `order-42` and `order-43`, the customer
can save a **continuation token**, a bookmark for the next fetch. The review
must ensure later pages continue the same scan and explain whether a saved
bookmark remains usable after an SDK upgrade.

**Why the Python/binding behavior needs correction**

An export must continue correctly after its first page, including when orders
span several storage partitions. The earlier binding did not retain enough
progress information to do that reliably. Response headers could also belong
to another operation, and callback handling could fail or change returned data.

The corrections preserve progress and response details for each separate
scan. Requests begin only when the customer iterates. Unsupported settings
raise an error rather than silently running legacy Python. These are
integration corrections; they do not establish that all driver limitations
listed below have been resolved.

**Why bookmarks require a compatibility decision**

The Rust-backed scan uses a different bookmark format. A customer who saved
a bookmark after exporting `order-42` and `order-43` cannot assume the upgraded
SDK can resume from that same value. This input-compatibility difference is
separate from fixing how the SDK keeps track of the current scan.

**Request contract:** All arguments are keyword-only. `max_item_count` accepts
a positive integer, `-1` for service-selected size, or `None`. Cache staleness,
the permitted age of cached data, accepts a nonnegative integer or `None`.
Booleans are invalid for both settings.
Reject query metrics by presence, even `False` or `None`. Snapshot request
options and do not modify customer objects.

**Bookmark contract:** Rust accepts its `c1.` bookmarks and rejects
legacy/service bookmarks. Legacy Python does not accept the Rust bookmarks
either. The driver checks the token and the container and operation it
belongs to. There is no automatic conversion or silent restart. Save a bookmark only
after processing a complete page. A failed/cancelled fetch or hook failure
requires a new result iterator starting from the last successfully delivered bookmark.
Concurrent fetching on the same result iterator is rejected.

**Response contract:** Each scan keeps its own response headers and bookmark.
Call the customer's hook once per fetched public page, including an
empty-container response. The hook receives independent headers and a copy
of the response body, including its nested values; edits cannot change
returned orders or the bookmark. The body has a `Documents` field containing
the items, as illustrated below. `None` disables the hook; otherwise a valid
callable runs even if the object evaluates to `False`.

Hook errors reach the customer without fetching the page again. Errors used
to end iteration become `RuntimeError` instead, so a failing hook cannot make
an incomplete export look complete. Finishing an already-consumed scan does
not invent another response or callback. Reported charge includes available
charges for internal empty pages, but is not a complete account of metadata
requests or failed attempts.

**Timeout contract:** A supported explicit `timeout` is one budget per public
page fetch, spanning metadata, planning, and internal empty pages. Remaining
sub-second time reaches the binding; processing time between pages consumes
none of the next budget. Async cancellation waits for outstanding work to stop.
The [first-use acquisition wait](#first-use-initialization-deadlines) is bounded
by that page's deadline without forcibly terminating shared initialization.

**Customer migration:** Use keyword arguments and valid page/cache settings;
remove query metrics. Finish bookmarked scans using the earlier SDK version
before upgrading, or intentionally begin a new scan. Unsupported controls are
release gaps unless their exclusion is approved; selecting legacy Python is
not a configuration option in the Rust-only release.

**Illustration - save a bookmark only after processing the page:**

```python
pages = container.read_all_items(max_item_count=2, timeout=5).by_page()
for page in pages:
    for item in page:
        process(item)
    save_checkpoint(pages.continuation_token)
```

`process` and `save_checkpoint` stand for application functions. A bookmark
records where the next fetch should continue, not which individual items the
application has already processed. If processing fails halfway through a page,
restart from the previous saved bookmark and handle possible repeated items.
If fetching or the hook fails, create a new result iterator rather than continuing the
failed one. Rust's `c1.` prefix identifies its bookmark format; it is not a
service token that legacy Python can consume. Do not strip the prefix to
try to convert it.

Each public page gets its own five-second fetch budget. Spending 30 seconds
processing one delivered page does not consume the next page's five seconds.
Metadata, planning which partitions to read, and internal empty-page requests
all consume the current fetch budget. This differs from the single workflow
budget in database get-or-create (`CosmosClient.create_database_if_not_exists`).

The hook here receives `(headers, body)` with a copied `Documents` envelope,
for example `{"Documents": [{"id": "order-42"}]}`, not just the one argument
used by listing databases (`CosmosClient.list_databases`). Editing that copy cannot
change returned items or the bookmark. An exception normally used to end
iteration, such as `StopIteration`, becomes `RuntimeError` so a hook cannot
make a failed scan appear complete. Other hook exceptions propagate without
fetching the page again. Only one fetch at a time may use a given result iterator.

**Remaining driver limitations and ownership**

| Customer requirement | Remaining difference |
|---|---|
| Set connection or read-inactivity limits for one scan | The Rust driver lacks those per-operation controls. An overall page-fetch budget does not provide the same limits. |
| Start reads in additional regions when earlier attempts remain slow | Rust supports one primary and one alternate request, not progressively adding more regions. Explicit `threshold_steps_ms` is rejected. This is an accepted release-scope difference, not a request to add a third overlapping hedge. |
| Inspect original response headers | The driver returns selected fields rather than a generic success-header map, which is excluded by design. |
| Inspect throttle retry counts and accumulated waiting | Still open: clarify the available driver metadata and Python mapping. |
| Inspect or edit the outgoing HTTP request with `raw_request_hook` | Removed from both backends; supplying it raises `TypeError`. Use supported observability for information and supported settings for configuration; arbitrary prepared-request mutation is not preserved. |

The driver team owns the remaining driver requirements, not a new raw-hook
extension. The Python SDK/binding team owns
verifying that the scan preserves the required results, options,
and paging behavior. Overrides of driver-owned request headers require a
separate compatibility decision; they are not the same as adding an
application-specific header. This read-all review does not establish that
public `query_items` has completed migration. It records no board approval.

<a id="30---query-execution-defaults-and-unordered-distinct-compatibility"></a>
<a id="30---requiring-a-finite-window-for-unordered-distinct"></a>
<a id="containerproxyquery_items"></a>

### `ContainerProxy.query_items`

This entry tracks two separate public-contract decisions: automatically enabling
cross-partition execution and supporting an unbounded unordered DISTINCT query.
Changing the default does not supply a missing query execution stage.

#### Aligning the sync and async cross-partition default

**Why the customer calls this API**

The employee asks for orders across all customers. The existing `orders`
container uses `/customerId` as its partition-key path. Suppose `order-1` and
`order-2` belong to `customer-501`, and `order-3` belongs to `customer-502`.
The customer app must not restrict this request to one customer's partition:

```python
for order in orders.query_items("SELECT * FROM orders"):
    print(order["id"])
```

Here, `orders` is the SDK object for the existing container. The customer app
supplies the SQL without a partition key or feed range. The SDK enables execution
over the required partitions so the service backend can supply their orders.
For this illustrative data, the expected result contains all three IDs, with
no promised ordering.

**Implemented behavior and compatibility change**

The previous synchronous API did not automatically enable
cross-partition execution when the flag was omitted. Legacy async did.
Legacy sync now matches async for a query with neither a partition key nor a
feed range:

| `enable_cross_partition_query` input | Current sync and async behavior |
|---|---|
| Omitted or `None` | Automatically enable cross-partition execution |
| `True` | Explicitly enable cross-partition execution |
| `False` | Keep cross-partition execution disabled |

This is an intentional change to the legacy synchronous default: a request
that previously needed explicit opt-in can now execute. Explicit `False`
remains available to prevent automatic opt-in if the customer app accidentally
omits its partition scope. Enabling execution does not broaden a supplied scope;
`partition_key="customer-501"` still restricts this example to `order-1` and
`order-2`. Existing feed-range behavior is unchanged.

The Rust-backed sync and async wrappers already shared the automatic default.
No Rust driver or binding change was needed. The current Rust binding still
requires a complete partition key when `False` is supplied; it does not infer
that key from a SQL predicate.

**Review disposition:** The automatic default and explicit opt-out are implemented; approval is not recorded. The DISTINCT restriction below remains a separate open compatibility decision.

#### Requiring a finite window for unordered DISTINCT

**Why the customer calls this API**

The customer wants every category represented in its orders, without repeats:

```python
categories = orders.query_items(
    "SELECT DISTINCT VALUE c.category FROM c",
    enable_cross_partition_query=True,
    max_item_count=2,
)
```

Two results per page does not mean only two categories in total. The customer
expects to keep reading until every matching category has been returned.

**Difference introduced by the driver update**

Legacy and the previous integrated driver could enumerate this unbounded
unordered DISTINCT query. The newly integrated driver requires a finite TOP
or LIMIT for cross-partition unordered DISTINCT. With the binding's current
planning defaults, OFFSET plus the result limit cannot exceed 1,000; when
both TOP and LIMIT apply, the smaller value is used.

The original example therefore fails during result fetching with a planning
error rather than returning all categories. Adding `TOP 1000` might omit
categories and is not an equivalent migration. `max_item_count=2` controls
page size and does not satisfy the global limit requirement.

**Required ownership and decision**

The driver team owns support for the required unbounded execution or an
explicitly approved restriction. The driver permits a larger finite buffer
window, but the Python API does not expose that planning setting; exposing
it would be separate integration work and would still not restore an
unbounded query. The Python wrapper must not silently insert a limit or
switch to legacy execution.

**Review disposition:** Open compatibility gap, not an approved removal.
Bounded DISTINCT enumeration and its lack of resumable bookmarks are
separate from whether the original unbounded query is supported.

<a id="20---polling-item-changes"></a>
<a id="containerproxyquery_items_change_feed"></a>

### `ContainerProxy.query_items_change_feed`

**Why the customer calls this API**

The customer wants to process order changes without repeatedly reading every
order. A **change feed** provides changes from a saved position in a selected
part of the container. This API lets the customer fetch those changes and
save a continuation token, a bookmark used by a later poll.

For example, one poll delivers changes to `order-42` and `order-43`; the next
finds no more changes currently available. That empty poll can still supply
an updated bookmark. The review must make it possible to save that position
without treating an empty result as proof that no future changes will occur.

**Why the Python/binding behavior needs correction**

The customer needs a reliable position from which to poll again. Previously,
an empty poll could end iteration before exposing that bookmark. Separate
polls also relied on shared response state, and preparing a poll could change
the customer's options. The Rust driver was not connected to this public API.

The integration now keeps each poll's options, results, and bookmark separate.
An empty page exposes the updated position instead of hiding it. Those
corrections are distinct from the still-unresolved restriction on reading
across multiple storage partitions described below.

**Why migration needs an explicit decision**

The new bookmark format is not interchangeable with legacy bookmarks.
Moreover, the current Rust-backed API rejects some scopes that legacy Python
can poll. Correct handling of one empty page does not make those restrictions
acceptable; customers need both a resumable workflow and support for the
parts of `orders` they must process.

**Argument changes and compatibility limits:** All arguments are keyword-only.
The older `is_start_from_beginning` and `partition_key_range_id` keywords remain
with deprecation warnings, but selecting a physical storage partition by ID
still requires legacy Python; the Rust-backed path does not support it.
Page size accepts a positive integer, `-1`, or `None`, not a boolean.

The customer must select only one scope: a partition key, a feed range, or
a legacy physical-partition ID. An explicit null partition key still selects
orders with that key; it is not the same as omitting the setting.
The SDK copies the customer's options and fetches container information only
when iteration needs it.

**Bookmark contract:** A valid continuation, supplied at creation or through
`by_page()`, determines mode, start and scope before those settings are
validated. Rust bookmarks begin with `cf1.` and must be saved and passed back
unchanged. Legacy bookmarks cannot be converted automatically, and bookmarks
from item queries or read-all scans cannot be substituted. Invalid tokens
raise an error rather than silently restarting the feed.

**Polling/response contract:** `by_page()` returns one empty caught-up page
with its updated checkpoint, then ends that iteration. Ordinary item
iteration yields no item for that page. Create a new result iterator with the saved
checkpoint to poll again. Checkpoint only after processing a complete page,
including an empty page. Each public page has isolated headers and one
success-hook invocation. A valid callback runs even if the object evaluates
to `False`; the SDK does not clear customer-owned callback state. Hook errors
reach the customer without repeating requests. Errors used to end iteration
become `RuntimeError` so a failing callback cannot make polling appear complete.
After execution starts, a failed result iterator cannot be reused.
Certain service failures during setup can be retried on the same iterator
only when the binding confirms execution has not started. Timeout and
cancellation remain terminal even during setup.
Concurrent fetches on one result iterator are rejected.

**Timeout contract:** One explicit supported timeout budget per public page,
including metadata, routing, retries and internal polls. Customer processing
between pages is excluded. Async cancellation waits for outstanding work to stop;
the [first-use acquisition wait](#first-use-initialization-deadlines) is bounded
without cancelling the shared worker. Available response charges are aggregated, not represented as
complete accounting for all metadata or driver-internal work.

**Current capability restriction:** The binding rejects scopes spanning multiple
physical partitions, including after observed split recovery. It must not treat
one child's empty response as whole-scope completion
when other children may still have changes; the driver can continue polling
those children. Legacy Python supports cross-partition polling in both feed modes.
There is no automatic fallback. Lifting the guard requires a scope-wide polling
contract and integration verification; rejection is not an approved exclusion.
Fixing this restriction does not by itself establish support for every
request control or preserve every original service response header.

**Customer migration:** Use named arguments. Legacy bookmarks are not
interchangeable with the Rust-backed API's bookmarks. An ongoing feed cannot
be migrated simply by "finishing" a poll: changes can arrive afterward.
Selecting a fresh `Now` can leave changes after the old bookmark unread;
selecting `Beginning` is not an equivalent resume and is unavailable for a
fresh all-versions-and-deletes feed. The migration plan for ongoing readers
remains an explicit open decision, not an approved restart or token-conversion
contract.

Blocked scopes/options remain release gaps, not a reason to offer a legacy
backend switch. Within a supported Rust-backed reader, persist the bookmark
from the caught-up empty page and create a new iterator for the next poll.
This is a draft for board review, not recorded board approval.

**Illustration - an empty poll can carry the checkpoint you need:**

| Poll result | Public page | Customer action |
|---|---|---|
| Two changes were found | Two items and a new bookmark | Process both, then save the bookmark |
| No more changes are currently available | One empty page with an updated bookmark | Save that bookmark too; this iteration then ends |
| Poll again later | Create a new result iterator with the saved bookmark | Resume checking from that position |

```python
pages = container.query_items_change_feed(
    continuation=saved_checkpoint
).by_page()
for page in pages:
    for change in page:
        process(change)
    save_checkpoint(pages.continuation_token)  # Runs for an empty page too.
```

The example assumes a supported scope and a checkpoint from the same backend.
Ordinary item iteration has no item to yield for the empty page, which is why
page iteration matters when saving the caught-up position. "Caught up" means
there are no currently available changes in the polled scope, not that future
changes cannot occur. A supplied valid bookmark already identifies its mode,
starting position and scope; it is not combined with a new unrelated start.

Rust uses `cf1.` change-feed bookmarks, not the `c1.` read-all bookmarks.
Refer to reading every item (`ContainerProxy.read_all_items`) for saving complete pages,
separate page budgets, failed-iterator handling and hooks that must not silently
end iteration. Do not transfer bookmarks between those APIs or between backends.

**Why the current Rust restriction matters:** suppose a scope covers storage
partitions A and B. A has no changes, but B has two. If the driver declares
"caught up" after checking only A, the application can miss B's available work.
The current Rust path rejects such multi-partition scopes instead of returning
that misleading result. Defining completion across the whole requested scope
requires driver and binding work; it is not an approved removal of
cross-partition polling.

<a id="29---replacing-an-existing-order"></a>
<a id="containerproxyreplace_item"></a>

### `ContainerProxy.replace_item`

**Customer motivation and retained behavior**

The customer wants to replace the complete contents of an existing order:

```python
replacement = {
    "id": "order-42", "tenant": "northwind", "status": "shipped"
}
saved = orders.replace_item("order-42", replacement)
```

An omitted property, such as `deliveryNote`, is removed rather than retained
by a merge. Missing orders are not created. The SDK normally extracts the
partition key from the replacement body, using cached or fetched container
metadata, then sends the replacement.

An ETag is the service backend's version marker. Supplying the previously
read `_etag` with `MatchConditions.IfNotModified` guards against intervening
edits. A failed condition raises `CosmosAccessConditionFailedError`; a missing
order raises `CosmosResourceNotFoundError`. `no_response=True` returns an empty
dictionary with available response metadata, not confirmation that no write
occurred.

**Disposition:** Partial migration; this entry does not record board approval
of the remaining restrictions.

**Addressing is preserved, not intentionally changed**

```python
saved_order = orders.read_item("order-42", partition_key="northwind")
orders.replace_item(saved_order, replacement)
```

The dictionary returned by the read contains `_self`, an address shaped as
`dbs/<database-resource-ID>/colls/<container-resource-ID>/docs/<item-resource-ID>/`.
These IDs are generated by the service backend; they are not the customer's
names.

```text
Caller A reads order-42 and retains its dictionary.
Caller B deletes that order and creates a new order-42 in the same partition.
Caller A submits the retained dictionary as the replacement target.
```

Legacy Python targets the old resource address. The Rust-backed path previously
discarded that address and targeted the current item by name. Our binding now
preserves `_self` using an existing driver capability. Passing an ID string
continues to deliberately select by name. This correction is not a proposal
to approve retargeting stale dictionaries.

**Other Python/binding corrections**

The customer may exclude West US on one replacement. Previously the exclusion
reached the write but not the binding's preliminary container-resolution call.
Both driver calls now receive it, without applying item-only ETag conditions
to container metadata. The driver still performs any required service lookup.
Region exclusions retain their fallback semantics, not a strict network boundary.

Replacement also now carries one remaining timeout budget. With `timeout=5`,
two seconds of initialization and two of metadata work leave one second for
replacement. The Rust-backed public timeout must be finite and at least one
second. The [acquisition wait](#first-use-initialization-deadlines) is bounded
by that same budget; the shared worker is not forcibly interrupted. Timeout or
cancellation does not roll back a write already accepted by the service backend.
Legacy ID validation is restored: for example, `"order/42"` in the replacement
body fails locally rather than proceeding into driver acquisition.

**Customer-visible restrictions requiring migration treatment**

| Existing customer behavior | Rust-backed restriction and impact |
|---|---|
| Replace orders in a legacy container with no partition key, or with a service-created system key | This compatibility mode is excluded from the release; driver reconsideration depends on customer need. These older containers cannot be declared equivalent to a normal `/tenant` container. |
| Control ambiguous write retries through `retry_write` | The per-call option is rejected. The driver's retry policy does not preserve legacy opt-in. A replacement guarded by ETag V1 can commit as V2, lose its response, and then receive a stale-condition error if retried with V1. The customer-visible failure does not prove the first write failed. |
| Set connection or read-inactivity limits on one replacement | Per-call `connection_timeout` and `read_timeout` are rejected. The overall `timeout` does not provide the same controls. |
| Inspect all original service response headers | The driver reconstructs selected headers. A customer can receive ETag and request charge but lose a header that it does not model, such as `date`. A response hook cannot recover discarded information. |
| Inspect or modify the outgoing HTTP request with `raw_request_hook` | Removed from both backends; supplying it raises `TypeError`. Supported options/static headers and observability do not preserve arbitrary request mutation. |
| Inspect the legacy HTTP pipeline response with `raw_response_hook` | Removed from both backends; supplying it raises `TypeError`. Use supported results, headers, tracing, and diagnostics. Customer code reading `pipeline_response.http_response.status_code` cannot migrate unchanged to `response_hook`, which receives headers and a parsed result. |
| Override SDK-generated protocol headers through `initial_headers` | Overrides of `accept`, `cache-control`, `user-agent`, and `x-ms-version` are rejected. Supported application headers are distinct from replacing driver-owned headers. |

Removing an unsupported argument is only a migration path when the customer
does not need its behavior. None of these restrictions silently invokes legacy
Python. The shared section "Older containers need their existing partition-key
representation" explains why the partition-key restrictions require two
related fixes rather than a change to the customer's order body.

**Remaining verification and decisions**

The following service-level outcomes remain unverified. Compare synchronous
and asynchronous clients against legacy Python using isolated test resources.

| Scenario | Required confirmation |
|---|---|
| Replace using a read document's resource-ID address | Replacement succeeds while the original order exists. After Caller B deletes and recreates it, Caller A's stale dictionary must not overwrite Caller B's new order. Omit an ETag condition so it cannot hide an addressing error; record the actual service error and final stored document. |
| Request a replacement trigger | The Rust-backed API rejects the excluded trigger input before replacing the order. Legacy trigger effects are no longer a parity acceptance criterion for this release. |
| Exclude West US with a cold container cache | Observe the metadata lookup and replacement destinations separately, then repeat with a warm cache. Account bootstrap and all-regions-excluded fallback are not covered by a blanket no-traffic promise. |
| Lose connectivity before delivery versus lose the response after commit | Record attempts, regions, the customer-visible result, and the stored order separately for both cases. Repeat the committed-write case with an ETag condition: a retry can report a stale condition even though the first write succeeded. |

The SDK team owns Python/binding integration and verification; driver capability
work belongs to the driver team. The recorded retry-policy difference does not
close other capability gaps or approve the raw response-hook contract.

<a id="33---persisting-patch-tracking-information-in-the-customers-order"></a>
<a id="34---accepting-more-than-ten-patch-instructions"></a>
<a id="containerproxypatch_item"></a>

### `ContainerProxy.patch_item`

**Compatibility decisions pending.**

#### Tracking information in the stored order

Alpha Bank increments `refund_attempts` from 5 to 6. On the reviewed Rust
path, the stored and returned order also contains `_azsdkPatchTracking`.
Legacy Python does not add that property when incrementing the same field.

The SDK uses the added property to recognize a patch after a lost response. An application that restricts stored fields could be affected; that impact has not been established. Hiding the property in the returned value would not remove it from the stored order or later reads.

Decide whether to accept and document the added property or require a
different retained contract. This is not approval to remove the driver's
retry-safety information. Broader lost-response behavior remains open.

**Bounded local verification:** On October 18, 2026 (UTC), the selected isolated
snapshot recovered a tracked increment after an independent read confirmed
counter one while returning traffic was held, followed by a 20,000-byte
cutoff. Sync and async returned the complete order; independent and later
same-client reads still found counter one. The test distinguishes a committed
write response from the driver's preliminary read. PATCH attempt diagnostics
are unavailable in this snapshot, so no exact retry sequence is claimed.
This does not approve tracking-property compatibility, establish general
exactly-once behavior, or validate concurrent SDK changes.

The test-harness review follow-up
repeated both committed-response cutoffs with synchronized observation.
Both calls still recovered with counter one; PATCH attempt diagnostics
remain unavailable.

#### More than ten patch instructions

Alpha Bank submits one patch list containing eleven instructions. Legacy Python rejects the list with status 400; the Rust path accepts it on both synchronous and asynchronous clients.

The Rust-backed SDK can apply that list.
The driver is not missing the ability to perform the update. The compatibility
question is whether the Python SDK should preserve rejection of lists longer
than ten instructions or intentionally allow these calls.

Accepting the larger list changes which customer calls succeed. Retaining
the legacy limit would require explicit validation on the Rust path.
Neither choice has been approved. Accepting the call does not establish equivalence with legacy behavior.

<a id="containerproxyexecute_item_batch"></a>

### `ContainerProxy.execute_item_batch`

#### Why the customer needs one batch

Contoso Bank stores two account records under the same partition key. The
customer app submits their updates together so the service backend applies
both or neither. This is a **transactional batch**. It is not the separate
API that deletes every item with a particular partition key.

Selecting Rust must also select the Rust execution path for this batch.
Previously, both Python client types called legacy `Batch` directly even
when the client selected Rust.

#### How the SDK now sends the request

The Python wrapper formats the existing operation tuples into one request,
retaining per-operation ETag conditions and patch filters. It registers
`execute_item_batch` as a native capability without legacy fallback, then
calls the synchronous or asynchronous binding entry point.

The binding resolves the container through the selected Rust driver and
executes `CosmosOperation::batch` with the supplied partition key and body.
Metadata resolution and execution share the remaining operation budget.
The Python wrapper returns `CosmosList` on success or constructs
`CosmosBatchOperationError` with the failing index and per-operation results.
An execution, parsing, or response-hook failure does not replay the batch
through legacy Python.

An explicitly selected `core-python` client retains the legacy path for
comparison. This integration does not implement partition-wide deletion or
close the separately documented Rust driver gaps.

#### What remains to prove

The original nine synchronous and nine asynchronous functional test bodies
are copied under `tests/execute_item_batch/sync/legacy` and
`tests/execute_item_batch/aio/legacy`. Only setup, resource cleanup, backend
selection, and the `_rust` method-name suffix change. An offline comparison
checks that the copied test bodies still match the originals.

Run those copies with `COSMOS_BACKEND=core-python`, then with
`COSMOS_BACKEND=rust`, using `--noconftest`. Their setup creates uniquely named
databases and deletes only resources it owns. For operation captures, also
set `COSMOS_PARITY_CAPTURE_OP=execute_item_batch` and load
`-p common.parity_capture_plugin`. The Rust runs reject calls to legacy
`Batch`; captures additionally record native binding and fallback counters.

The native extension has been built and its two batch exports loaded.
Offline routing and result-contract checks passed. **Live functional parity
is not established:** the first legacy probe failed during container
creation with emulator status `503`, substatus `1007`. An async test-guard
import was corrected, but terminal execution subsequently became unavailable
before both surfaces could be rerun against both backends. None of those
probes reached a batch operation. Atomic rollback, mixed-operation results,
conditions, patch filters, size limits, and hierarchical keys still require
the service-backed comparisons; matching setup failures would not prove them.

## Throughput management

<a id="31---keeping-database-throughput-results-independent-of-response-hooks"></a>
<a id="databaseproxyget_throughput"></a>

### `DatabaseProxy.get_throughput`

**Why does the customer read throughput?**

The customer app checks the shared capacity of its database before
accepting a larger order workload.

**Why this needs a public decision**

Reading database throughput is already supported by the Rust driver. Removing
the deprecated public alias and applying the common response-hook contract
are Python wrapper cleanup and compatibility decisions; neither requires a
new Rust driver capability.

Throttle retry metadata remains an open requirement.
The wrapper cleanup does not settle that contract. Timeout scope follows
the shared runtime/operation model; generic success-header preservation is
excluded by design, not pending driver implementation.

**Which response-hook rules apply?**

The common response-hook contract and required customer changes are explained
in [`CosmosClient.create_database`](#2---creating-a-database). The same rules apply here.

Here, an *offer* is the record containing the database's throughput settings,
such as manual throughput of 4,000 RU/s. `response_hook(headers, offers)`
receives response headers and a list containing that record. The method
itself returns one `ThroughputProperties` object, not a list. The response
hook runs once after a successful read.

Use `get_throughput` to read capacity. The removed `read_offer` aliases have their own entries below.

**What happens to an unsupported input?**

The shared rule under
[Unsupported settings must not silently run legacy Python](#unsupported-settings-no-longer-silently-change-the-selected-backend)
applies. For this API, rejection happens before database metadata or offer
requests on both synchronous and asynchronous clients.

**Async signature for review**

```python
async def get_throughput(
    self,
    *,
    response_hook: Optional[
        Callable[[Mapping[str, Any], list[dict[str, Any]]], None]
    ] = None,
    **kwargs: Any,
) -> ThroughputProperties:
    ...
```

This is the current implementation's signature. The synchronous client
accepts the same arguments using `def`; its call is not awaited. Both return
one `ThroughputProperties` object.

**Review disposition:** The alias removal is approved. The response-hook contract remains a separate review decision; this read does not resolve the timeout or response-header restrictions.

<a id="databaseproxyread_offer"></a>

### `DatabaseProxy.read_offer`

**Omitted.** Use `DatabaseProxy.get_throughput` instead. Accessing the removed alias raises `AttributeError`.

<a id="32---reading-container-throughput-without-changing-the-result-or-execution-path"></a>
<a id="containerproxyget_throughput"></a>

### `ContainerProxy.get_throughput`

**What does the customer need?**

The customer app reads the capacity reserved for its `orders` container.
For a container configured at 4,000 RU/s:

```python
throughput = container.get_throughput()
print(throughput.offer_throughput)  # 4000
```

**Why this needs a public decision**

The Rust driver already supports reading throughput. This review covers
Python wrapper integration corrections for missing throughput and recreated
containers, plus the common response-hook compatibility change. These do
not require a new Rust driver capability.

Throttle retry metadata remains an open requirement.
The wrapper corrections do not settle that contract. Timeout scope follows
the shared runtime/operation model; generic success-header preservation is
excluded by design, not pending driver implementation.

**Which response-hook rules apply?**

The common contract and required customer changes follow
[`CosmosClient.create_database`](#2---creating-a-database). The throughput-specific response-hook
arguments are explained in
[`DatabaseProxy.get_throughput`](#31---keeping-database-throughput-results-independent-of-response-hooks).

**What happens when the container uses shared throughput?**

If `orders` uses the database's shared capacity, it has no dedicated
throughput configuration to return. Both implementations now raise
`CosmosResourceNotFoundError`, status 404 and substatus 10004, instead of the
observed `IndexError` or `AttributeError`. The customer app must read the
database's throughput to inspect that shared capacity.

**What happens after container recreation?**

If `orders` is deleted and recreated at 8,000 RU/s, the customer app needs
the new configuration rather than a failure caused by the SDK's saved
properties for the old container.

After a missing throughput record or a container-recreation error, the Python
wrapper can refresh container properties once. It retries the throughput read
only if the container's internal identity changed. Recovery still uses Rust;
unrelated request failures and response-hook failures do not trigger it.
The same pre-write lookup recovery now applies to container throughput
replacement; the write itself is not replayed.

One operation deadline covers cache-lock waiting, cold metadata, the complete
offer query and any refresh/retry. Both clients inherit the client timeout
unless the call overrides it, without restarting the budget at each phase.

**What happens to unsupported inputs?**

The shared rule under
[Unsupported settings must not silently run legacy Python](#unsupported-settings-no-longer-silently-change-the-selected-backend)
applies. For this API, rejection happens before container metadata or
throughput requests on both synchronous and asynchronous clients.

**Async signature for review**

```python
async def get_throughput(
    self,
    *,
    response_hook: Optional[
        Callable[[Mapping[str, Any], list[dict[str, Any]]], None]
    ] = None,
    **kwargs: Any,
) -> ThroughputProperties:
    ...
```

This is the current implementation's signature. The synchronous client
accepts the same arguments using `def`; its call is not awaited. Both return
one `ThroughputProperties` object.

**Review disposition:** The read changes are approved. Replacement has its own
decision below; the retry-information contract remains open under gap 30.

<a id="containerproxyread_offer"></a>

### `ContainerProxy.read_offer`

**Omitted.** Use `ContainerProxy.get_throughput` instead. Accessing the removed alias raises `AttributeError`.

<a id="databaseproxyreplace_throughput"></a>
<a id="containerproxyreplace_throughput"></a>

### `DatabaseProxy.replace_throughput` and `ContainerProxy.replace_throughput`

**What does the customer change?**

Alpha Bank raises `orders` from 400 to 1,000 RU/s before a larger workload:

```python
updated = container.replace_throughput(1000)
print(updated.offer_throughput)  # 1000
```

The database method changes shared database capacity instead. Both return
`ThroughputProperties`; their asynchronous counterparts accept the same
settings and are awaited.

**Why are two throughput requests needed?**

The service stores capacity in a separate record called an offer. The SDK
first finds the offer belonging to the database or container. That lookup
cannot change capacity, so the SDK copies the returned record, applies the
new settings and sends a replacement. Both requests use Rust. An unsupported
input is rejected before metadata lookup; failure in either request never
causes a legacy retry.

For database and container replacement, one operation deadline covers cold
metadata, the complete offer lookup and the replacement. Container cache-lock
waiting and any pre-write identity refresh/retry use that same deadline.
The coordinators inherit the client timeout unless overridden, stop before
starting a later phase after expiration, and await asynchronous cancellation
cleanup. Internal remaining budgets can be below the one-second public minimum;
they are not treated as new public timeout inputs.

**What changes for a customer using callbacks or autoscale?**

Supported caller options apply to both requests, consistently across sync
and async. A successful replacement calls `response_hook(headers, offer)`
once with the updated offer dictionary, not the lookup's list. The common
response-hook contract applies: invalid callbacks fail before requests,
callback exceptions propagate, and callback mutation cannot change the
returned settings or their available headers.

For an autoscale resource, replacing its maximum returns the service's
autoscale maximum and increment percentage. An explicitly supplied zero
increment is retained. Caller-owned options and the looked-up offer are not
modified. Supplying manual and autoscale settings together raises `KeyError`
before requests.

**What happens when no throughput configuration exists?**

The SDK raises `CosmosResourceNotFoundError` without sending a replacement.
For a container using shared database throughput, the error has status 404
and substatus 10004; change shared capacity through the database instead.

**What was approved, and what remains open?**

The session decision approves Rust-only throughput execution without
automatic fallback and the internal names `get_throughput` and
`replace_throughput`. It does not reinstate public offer aliases or rename
the external Rust driver's offer API. Explicit legacy selection remains
only as a comparison reference. This is not a claim of formal API-board
approval or complete response-header parity. The database correction passed
all eight original-derived replacement methods on each backend and nine paired
live comparisons, including callback isolation. These live results are
distinct from binding-boundary failure/deadline
checks. The container correction passed 25 original-derived read tests and
18 replacement tests on each backend, plus 18 live read/rejection checks and
14 paired replacement comparisons. Two replacement rejections and four
Rust-only input rejections occur before native entry; they are not native
execution evidence. Gap 30 remains open; accepted generic-header differences
do not reopen gap 29.

## Feed ranges and session consistency

<a id="27---discovering-ranges-for-parallel-order-reads"></a>
<a id="containerproxyread_feed_ranges"></a>

### `ContainerProxy.read_feed_ranges`

**Why the customer calls this API**

The customer wants to divide a large `orders` container into parts that can
be read separately. A **feed range** describes which part of the container
a supported query or change-feed operation should read. This API discovers
the ranges; it does not read the orders or start the parallel work.

```text
Discover ranges for orders
    -> range A: one part of the container
    -> range B: another part
    -> range C: the remaining part
Pass each range unchanged to a separate supported read operation.
```

Discovery begins during iteration and returns range dictionaries. These
describe where to read, not how far a previous read progressed.

**Why this needs a public decision**

The SDK caches a **partition map**, information describing the container's
physical storage ranges. If B splits into B1 and B2, the customer can request
`force_refresh=True` to discover the new divisions. Legacy Python reports
an error if that refresh fails. The Rust driver can instead return cached
A, B, and C successfully without indicating that the refresh failed.

The customer might therefore keep three read assignments instead of four
and receive no refresh error on which to base another discovery attempt.
This does not by itself mean orders are missed: the old B still covers the
part now served by B1 and B2. The decision is whether a successful refresh
call may hide that its requested update failed.

**Compatibility:** Preserve the existing lazy iteration and dictionary values.
The legacy Python lookup accepted extra keywords, but did not apply every one
to its metadata requests:

| Legacy setting | What the customer previously received |
|---|---|
| `timeout` | A limit for each partition-range fetch and its retries, not one budget for complete discovery. |
| `connection_timeout` | Legacy per-call connection-setup control on those fetches. |
| `response_hook` | Headers and body for each successful partition-range response; no callback when cached ranges avoided the requests. |
| `raw_request_hook`, `raw_response_hook` | Access to the outgoing pipeline request or HTTP response object; the request hook could also modify the request. |
| `headers` | Custom headers on partition-range requests. |
| `initial_headers`, `excluded_locations` | Accepted keywords, but no corresponding custom-header or region-exclusion behavior on partition-range requests. |

The legacy controls above did not apply to the preliminary container-property
lookup. A timeout spanning that lookup and all range fetches would be a new
guarantee, not restoration of the old per-fetch limit.

The Rust lookup supports `timeout` as one overall discovery budget, including
first-use driver acquisition and metadata resolution. For example, with
`CosmosClient(..., timeout=5)`, creating `ranges = container.read_feed_ranges()`
does not start the timer. Iterating `ranges` starts the five-second budget.
If acquisition consumes one second, the binding receives four seconds, not
another five. A per-call `timeout=10` replaces the default for that discovery;
`timeout=None` inherits the default. Expiry raises `CosmosClientTimeoutError`,
and a result completing after expiry is not cached as a successful discovery.

Other unsupported per-call settings still raise instead of silently losing
their behavior. The driver must expose the remaining request controls and
response details through the binding; the Python wrapper owns invoking the
customer's callbacks. Timeout support does not close those separate gaps.

| Area | New contract and customer reason |
|---|---|
| Refresh flag | Require `True` or `False`. Other values raise `TypeError` when the iterable is constructed; `"false"` is not a boolean setting. |
| Timeout | Support the client default and per-call override as one lazy discovery budget, not the legacy per-fetch limit. Replaying an already successful result uses its cached list, not a new discovery or deadline. |
| Extra options | Apart from `timeout`, the current Rust lookup rejects additional per-call options with `NotImplementedError` when fetching. Restore remaining confirmed legacy request controls and the response callback without running legacy Python. Separately decide compatibility for `initial_headers` and `excluded_locations`, which this legacy API did not apply as header or routing settings. |
| Iteration | Preserve lazy discovery and return dictionaries. One iterable retains one complete range list; requesting its page again gives independent copies. Make a new API call for another discovery. |
| Continuation | Reject a non-`None` token passed to `by_page` with `ValueError` rather than ignore it and start again. There is no public resumable range enumeration or page-size control. |
| Parallel calls | Separate result iterators are independent. Concurrent fetches on one result iterator raise `RuntimeError` rather than race two discoveries. |
| Response details | Return types are `CosmosItemPaged` and `CosmosAsyncItemPaged`, exposing available metadata through `get_response_headers()`. Copies are independent of other calls, but these are not the complete metadata HTTP response headers. |

**Pending decisions:** Agree on the refresh-failure behavior, required per-call
controls, and which metadata response details customers must receive.
The driver can also discard a partition-metadata error: without a usable map,
the customer may receive a generic lookup failure rather than the original
service status and headers. Losing the distinction between a permission
failure (HTTP 403) and a temporary service failure (HTTP 503) changes how
the customer can recover. Preserving that information and each metadata
response's charge and activity ID remains required work. These limitations
are not approved feature exclusions; this entry is a draft, not board approval.

<a id="35---rejecting-unsupported-subset-inputs-without-legacy-fallback"></a>
<a id="containerproxyis_feed_range_subset"></a>

### `ContainerProxy.is_feed_range_subset`

**Review disposition:** Strict-input rejection approved and implemented.
Boundary-comparison changes are deferred.

Alpha Bank asks whether a customer's range fits inside a worker's assigned
range. A valid call returns `True` or `False`. If the customer app instead
passes a hand-edited range with reversed bounds or an unsupported dictionary
shape, the Rust-backed SDK now raises `NotImplementedError`.

Previously, the wrapper sent those inputs to the local legacy Python
comparison. It could therefore return an answer without executing the selected
Rust path. The approved decision removes that fallback rather than preserving
every legacy-accepted input.

For example, a parent starting at `"7F"` and ending before `"3F"` has its bounds
reversed. Legacy Python returns `False` against a child from `"3F"` to `"7F"`;
the Rust-backed SDK now rejects the parent explicitly. Extra dictionary fields,
non-Boolean inclusion flags, and invalid hexadecimal boundary strings are
also rejected. Customers should pass SDK-returned range dictionaries unchanged.

This input decision does not settle trailing-zero EPK equality or excluded-boundary behavior; those remain separate open questions.

## Cosmos database users

The `UserProxy` type is also omitted. Cosmos database users are not Microsoft Entra identities.

<a id="databaseproxylist_users"></a>

### `DatabaseProxy.list_users`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos database-user management belongs to the unsupported resource-token model.

<a id="databaseproxyquery_users"></a>

### `DatabaseProxy.query_users`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos database-user management belongs to the unsupported resource-token model.

<a id="databaseproxyget_user_client"></a>

### `DatabaseProxy.get_user_client`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos database-user management belongs to the unsupported resource-token model.

<a id="databaseproxycreate_user"></a>

### `DatabaseProxy.create_user`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos database-user management belongs to the unsupported resource-token model.

<a id="databaseproxyupsert_user"></a>

### `DatabaseProxy.upsert_user`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos database-user management belongs to the unsupported resource-token model.

<a id="databaseproxyreplace_user"></a>

### `DatabaseProxy.replace_user`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos database-user management belongs to the unsupported resource-token model.

<a id="databaseproxydelete_user"></a>

### `DatabaseProxy.delete_user`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos database-user management belongs to the unsupported resource-token model.

<a id="userproxyread"></a>

### `UserProxy.read`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos users and resource permissions belong to the unsupported resource-token model.

## Cosmos resource permissions

The `Permission` and `PermissionMode` types and `resource_token_expiry_seconds` option are also omitted. Cosmos permissions are not Entra role assignments.

<a id="userproxylist_permissions"></a>

### `UserProxy.list_permissions`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos users and resource permissions belong to the unsupported resource-token model.

<a id="userproxyquery_permissions"></a>

### `UserProxy.query_permissions`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos users and resource permissions belong to the unsupported resource-token model.

<a id="userproxyget_permission"></a>

### `UserProxy.get_permission`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos users and resource permissions belong to the unsupported resource-token model.

<a id="userproxycreate_permission"></a>

### `UserProxy.create_permission`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos users and resource permissions belong to the unsupported resource-token model.

<a id="userproxyupsert_permission"></a>

### `UserProxy.upsert_permission`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos users and resource permissions belong to the unsupported resource-token model.

<a id="userproxyreplace_permission"></a>

### `UserProxy.replace_permission`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos users and resource permissions belong to the unsupported resource-token model.

<a id="userproxydelete_permission"></a>

### `UserProxy.delete_permission`

**Omitted on both synchronous and asynchronous clients, on both backends.** Cosmos users and resource permissions belong to the unsupported resource-token model.

<a id="26---reviewing-conflict-resolution-separately-from-container-management"></a>

## Conflicts

The scope decision remains open for these four APIs. Retaining them requires equivalent conflict-feed behavior; omission requires a customer migration for unresolved conflicts. Container-policy configuration is not a substitute.

<a id="containerproxylist_conflicts"></a>

### `ContainerProxy.list_conflicts`

**Scope decision pending.** Lists unresolved conflict records for customer
inspection. Configuring a container's conflict policy through a management API
does not replace reading this feed.

<a id="containerproxyquery_conflicts"></a>

### `ContainerProxy.query_conflicts`

**Scope decision pending.** Filters unresolved conflict records with a query.
Container deployment and management listing are not equivalent replacements.

<a id="containerproxyget_conflict"></a>

### `ContainerProxy.get_conflict`

**Scope decision pending.** Reads a conflict record identified by its record ID,
not the order's ID. Reading the record does not merge competing item versions.

```python
conflict = container.get_conflict(
    conflict="conflict-1", partition_key="customer-42"
)
print(conflict["operationType"])
```

<a id="containerproxydelete_conflict"></a>

### `ContainerProxy.delete_conflict`

**Scope decision pending.** Deletes a conflict record, not the conflicting item.
The application must apply its chosen outcome to the item before removing the
record and recover safely if it stops between those separate operations.

<a id="23---omitting-stored-procedures-without-confusing-management-and-execution"></a>

## Stored procedures

**Implementation: removed.** All seven methods below and their legacy
connection implementations are gone from both sync and async clients.
The entries retain the exclusion decision; they are not available APIs or
pending Rust work. Dedicated execution, CRUD, logging and parity tests and
the stored-procedure-based multi-master sample path have been removed.

<a id="scriptsproxylist_stored_procedures"></a>

### `ScriptsProxy.list_stored_procedures`

**Excluded from both synchronous and asynchronous Rust-backed clients.** Stored-procedure management and execution are outside this release's scope.

<a id="scriptsproxyquery_stored_procedures"></a>

### `ScriptsProxy.query_stored_procedures`

**Excluded from both synchronous and asynchronous Rust-backed clients.** Stored-procedure management and execution are outside this release's scope.

<a id="scriptsproxyget_stored_procedure"></a>

### `ScriptsProxy.get_stored_procedure`

**Excluded from both synchronous and asynchronous Rust-backed clients.** Stored-procedure management and execution are outside this release's scope.

<a id="scriptsproxycreate_stored_procedure"></a>

### `ScriptsProxy.create_stored_procedure`

**Excluded from both synchronous and asynchronous Rust-backed clients.** Stored-procedure management and execution are outside this release's scope.

<a id="scriptsproxyreplace_stored_procedure"></a>

### `ScriptsProxy.replace_stored_procedure`

**Excluded from both synchronous and asynchronous Rust-backed clients.** Stored-procedure management and execution are outside this release's scope.

<a id="scriptsproxydelete_stored_procedure"></a>

### `ScriptsProxy.delete_stored_procedure`

**Excluded from both synchronous and asynchronous Rust-backed clients.** Stored-procedure management and execution are outside this release's scope.

<a id="scriptsproxyexecute_stored_procedure"></a>

### `ScriptsProxy.execute_stored_procedure`

**Excluded from both synchronous and asynchronous Rust-backed clients.** Stored-procedure management and execution are outside this release's scope.

<a id="25---reviewing-trigger-management-separately-from-item-writes"></a>

## Triggers

**Implementation: removed.** The six definition-management methods below,
their legacy connection implementations, and dedicated CRUD/execution tests
and parity fixtures have been removed. `TriggerType` and `TriggerOperation`
are no longer exported or defined in `azure.cosmos.documents`.

Trigger invocation is excluded on item operations as well: `pre_trigger_include`, `post_trigger_include`, their request-option aliases, and trigger header overrides are unsupported.

<a id="scriptsproxylist_triggers"></a>

### `ScriptsProxy.list_triggers`

**Excluded from both synchronous and asynchronous Rust-backed clients.** Trigger management and invocation are outside this release's scope.

<a id="scriptsproxyquery_triggers"></a>

### `ScriptsProxy.query_triggers`

**Excluded from both synchronous and asynchronous Rust-backed clients.** Trigger management and invocation are outside this release's scope.

<a id="scriptsproxyget_trigger"></a>

### `ScriptsProxy.get_trigger`

**Excluded from both synchronous and asynchronous Rust-backed clients.** Trigger management and invocation are outside this release's scope.

<a id="scriptsproxycreate_trigger"></a>

### `ScriptsProxy.create_trigger`

**Excluded from both synchronous and asynchronous Rust-backed clients.** Trigger management and invocation are outside this release's scope.

<a id="scriptsproxyreplace_trigger"></a>

### `ScriptsProxy.replace_trigger`

**Excluded from both synchronous and asynchronous Rust-backed clients.** Trigger management and invocation are outside this release's scope.

<a id="scriptsproxydelete_trigger"></a>

### `ScriptsProxy.delete_trigger`

**Excluded from both synchronous and asynchronous Rust-backed clients.** Trigger management and invocation are outside this release's scope.

<a id="24---reviewing-udf-management-separately-from-query-use"></a>

## User-defined functions

**Implementation: definition management removed.** The six methods below,
their legacy connection implementations and dedicated definition tests have
been removed. They are intentionally excluded, not a Rust integration backlog.

Calling deployed UDFs in `query_items` SQL remains supported; only definition management is excluded.

<a id="scriptsproxylist_user_defined_functions"></a>

### `ScriptsProxy.list_user_defined_functions`

**Excluded from both synchronous and asynchronous Rust-backed clients.** UDF definition management is excluded; calling deployed UDFs in `query_items` SQL remains supported.

<a id="scriptsproxyquery_user_defined_functions"></a>

### `ScriptsProxy.query_user_defined_functions`

**Excluded from both synchronous and asynchronous Rust-backed clients.** UDF definition management is excluded; calling deployed UDFs in `query_items` SQL remains supported.

<a id="scriptsproxyget_user_defined_function"></a>

### `ScriptsProxy.get_user_defined_function`

**Excluded from both synchronous and asynchronous Rust-backed clients.** UDF definition management is excluded; calling deployed UDFs in `query_items` SQL remains supported.

<a id="scriptsproxycreate_user_defined_function"></a>

### `ScriptsProxy.create_user_defined_function`

**Excluded from both synchronous and asynchronous Rust-backed clients.** UDF definition management is excluded; calling deployed UDFs in `query_items` SQL remains supported.

<a id="scriptsproxyreplace_user_defined_function"></a>

### `ScriptsProxy.replace_user_defined_function`

**Excluded from both synchronous and asynchronous Rust-backed clients.** UDF definition management is excluded; calling deployed UDFs in `query_items` SQL remains supported.

<a id="scriptsproxydelete_user_defined_function"></a>

### `ScriptsProxy.delete_user_defined_function`

**Excluded from both synchronous and asynchronous Rust-backed clients.** UDF definition management is excluded; calling deployed UDFs in `query_items` SQL remains supported.

## Shared customer-visible changes

### Older containers need their existing partition-key representation

Legacy partitionless and system-key container compatibility is outside the
Rust-backed release's scope. Changing SDKs does not migrate existing data or
rewrite partition keys. Customers using that compatibility mode need a
supported client for that workload or a separate data-migration plan.

A missing value in an ordinary partitioned container is a different case.
For example, an order without `tenant` in a `/tenant` container is not an
order in a partitionless container. Do not substitute a null or undefined
partition key to work around the excluded compatibility mode.

### Hedging uses one threshold, not progressive threshold steps

For eligible reads, `availability_strategy={"threshold_ms": 100}` allows
an alternate regional attempt when the first remains pending for 100
milliseconds. It does not promise a third concurrent attempt if both are slow.

`threshold_steps_ms` is excluded from client and operation settings, including
request-option dictionaries. Supplying it raises `TypeError`; removing it
accepts the threshold-only contract, not equivalent progressive scheduling.
`threshold_ms`, `True`, `False`, and inheritance keep their eligibility rules.

`from_connection_string` applies the same constructor rules. Constructing a
client configures future requests; it does not send a hedged request.

### Raw pipeline hooks are removed from both backends

`raw_request_hook` and `raw_response_hook` are Python Core-specific exposures,
not publicly documented Cosmos SDK options. The Rust API decision is not to
reproduce them. Customers should obtain information through supported
response headers, results, OpenTelemetry, and diagnostic strings.

For example, use the returned order to read its ID and the exposed response
headers to record request charge. Use supported tracing and diagnostics to
investigate execution, after verifying the information delivered to Python.
This does not promise every original header, raw response bytes,
per-attempt callbacks, or arbitrary prepared-request mutation.
The ordinary `response_hook` is not excluded.

Constructor and per-operation inputs, including nested option dictionaries
and explicit `None`, raise `TypeError` on sync/async legacy and Rust paths.
The raw-hook policy and query forwarding are removed. Execution/parity tests
for these callbacks are retired; unsupported-input regression coverage
remains. These exclusions are not blocked on a new Rust extension or
equivalent callback delivery. Separate observability integration still needs
its own evidence.

<a id="unsupported-settings-no-longer-silently-change-the-selected-backend"></a>

### Unsupported settings must not silently run legacy Python

An unsupported setting must produce an explicit error on APIs that adopt
this rule, not silently select the legacy request implementation. For example,
a database listing with `raw_request_hook=my_hook` raises `TypeError` because
that input is removed; it cannot appear successful after discarding it.

The error may occur when iteration fetches a page. Remove an unsupported
option only if the application does not need its behavior; otherwise that
application cannot migrate until the capability or its replacement is resolved.
`response_hook` is different: it observes a returned response.

Database and container `get_throughput` adopt this rule. Throughput replacement
still has option-dependent legacy paths; do not treat those pending differences
as resolved or generalize one API's behavior to every operation.

### Throttle retry waiting follows the driver policy

The Rust-backed contract accepts driver-owned retry timing rather than exact
legacy Python delays. `retry_throttle_backoff_max` governs ordinary throttle
waiting, not a strict cap on every retry delay: a final retry can use the
remaining overall operation budget. Retry-count and operation-timeout limits
still apply.

This compatibility difference is intentional, not an outstanding implementation
requirement. Throttle retry counts and accumulated wait-time metadata remain a
separate open requirement.

### Timeout settings are explicit about their scope

The chosen Rust timeout model intentionally excludes legacy read-inactivity
timers and per-operation transport overrides. Connection and independent
data/metadata whole HTTP-attempt limits are configured through
`ConnectionPoolOptions` on `CosmosRuntime`. These settings are implemented;
gap 17 is closed by design, not pending equivalent legacy driver controls.

Client-default and per-call overall budgets are separate from runtime HTTP limits:

```python
client = CosmosClient(endpoint, credential=key, timeout=10)
database = client.get_database_client("sales")
properties = database.read(timeout=5)
```

`timeout=10` sets the client default. `timeout=5` overrides it for this supported
operation's work. The reviewed operation-timeout inputs must be finite numeric
durations of at least one second, within the supported range, and not booleans.
This initial-input rule does not prevent an operation from passing a remaining
fraction of a second to its next internal request.

`read_timeout` is removed from both execution paths, including constructors,
operations, and nested options. Even explicit `None` raises `TypeError`.
For the supported overall `timeout`, omission or `None` inherits the client default.

| With `timeout=5` | Budget |
|---|---|
| Database creation | Setup and creation share five seconds. |
| Database get-or-create | Read, possible create, and possible recovery read share five seconds. |
| Reviewed paged listing | Each page fetch gets five seconds. Processing previous results does not consume the next budget. |

For example, fetching page 1 in two seconds and processing it for 30 seconds
still leaves a fresh five-second budget for page 2. This is not a time limit
on the entire listing. Non-interruptible setup and cancellation cleanup can
delay return beyond the configured budget.

### Rust success responses expose modeled metadata, not a generic raw-header map

The generic collection of original success-response headers is intentionally
excluded from the Rust-backed contract. The Python wrapper and binding must
preserve the available modeled metadata, but are not required to reconstruct
every original header or its original textual spelling.

Python-added throttle retry counts and accumulated wait time are a separate
requirement, still open pending Rust-team clarification.
This decision does not rewrite historical capture results or establish
current failure-response header parity.

### Rust response metadata includes an additional diagnostics header

The SDK can add `x-ms-cosmos-sdk-diagnostics` to Rust-backed response metadata
when diagnostic information is available. This is SDK-provided text, not an
original service response header or an outgoing request header.

```python
properties = database.read()
summary = properties.get_response_headers().get("x-ms-cosmos-sdk-diagnostics")
if summary is not None:
    print(summary)
```

Strict header allowlists may need to allow this optional entry. Treat its value
as human-readable text, not a stable format to parse. It may be absent when no
request or diagnostics exist, and it does not recover missing original service
headers such as `date`.
