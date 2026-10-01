# Python Cosmos DB SDK - Public API changes for review


## Contents

- [1 - Connection-string client creation](#1---connection-string-client-creation)
- [2 - Creating a database](#2---creating-a-database)
- [3 - Creating a database if it does not exist](#3---creating-a-database-if-it-does-not-exist)
- [4 - Listing databases](#4---listing-databases)
- [5 - Querying databases](#5---querying-databases)
- [6 - Deleting a database](#6---deleting-a-database)
- [7 - Reading database properties](#7---reading-database-properties)
- [8 - Creating a container](#8---creating-a-container)
- [9 - Creating a container if it does not exist](#9---creating-a-container-if-it-does-not-exist)
- [10 - Deleting a container](#10---deleting-a-container)
- [12 - Listing containers](#12---listing-containers)
- [13 - Querying containers](#13---querying-containers)
- [14 - Replacing container settings](#14---replacing-container-settings)
- [15 - Reading container properties](#15---reading-container-properties)
- [16 - Reading an item](#16---reading-an-item)
- [17 - Creating an item](#17---creating-an-item)
- [18 - Reading known items](#18---reading-known-items)
- [19 - Reading every item](#19---reading-every-item)
- [20 - Polling item changes](#20---polling-item-changes)
- [21 - Getting a database client from properties](#21---getting-a-database-client-from-properties)
- [22 - Excluding resource tokens and Cosmos user and permission APIs](#22---excluding-resource-tokens-and-cosmos-user-and-permission-apis)
- [23 - Omitting stored procedures without confusing management and execution](#23---omitting-stored-procedures-without-confusing-management-and-execution)
- [24 - Reviewing UDF management separately from query use](#24---reviewing-udf-management-separately-from-query-use)
- [25 - Reviewing trigger management separately from item writes](#25---reviewing-trigger-management-separately-from-item-writes)
- [26 - Reviewing conflict resolution separately from container management](#26---reviewing-conflict-resolution-separately-from-container-management)
- [27 - Discovering ranges for parallel order reads](#27---discovering-ranges-for-parallel-order-reads)
- [29 - Replacing an existing order](#29---replacing-an-existing-order)
- [30 - Requiring a finite window for unordered DISTINCT](#30---requiring-a-finite-window-for-unordered-distinct)
- [31 - Keeping database throughput results independent of response hooks](#31---keeping-database-throughput-results-independent-of-response-hooks)
- [32 - Reading container throughput without changing the result or execution path](#32---reading-container-throughput-without-changing-the-result-or-execution-path)
- [33 - Persisting patch tracking information in the customer's order](#33---persisting-patch-tracking-information-in-the-customers-order)
- [34 - Accepting more than ten patch instructions](#34---accepting-more-than-ten-patch-instructions)
- [Shared customer-visible changes](#shared-customer-visible-changes)

## 1 - Connection-string client creation

**API:** `CosmosClient.from_connection_string`

**Why the customer calls this API**

The customer app needs a Cosmos DB client before it can store or read orders
in the existing `orders` container. The customer's configuration supplies a
**connection string**: one string containing the account endpoint (the service
backend's address) and an account key (the credential used to authenticate).
This API creates the client from that string, so the customer app does not
have to split the endpoint and key into separate constructor arguments.

```text
Customer configuration supplies:
    AccountEndpoint=<account endpoint>;AccountKey=<account key>;
        -> customer app calls CosmosClient.from_connection_string(...)
        -> receives a client for that account
        -> uses that client to access sales / orders
        -> calls item APIs to store or read order-42
```

Creating the client does not create the `sales` database or the `orders`
container, and it does not itself store or read `order-42`. Those are separate
operations.

**Why this needs a public decision**

For the orders example above, the connection string supplies everything
needed to identify the account and authenticate with its key. The contract
question arises when the customer app also passes a separate credential to
this same API:

```text
Customer app calls from_connection_string with:
    connection string containing account key A
    credential=account_key_B
        -> should the SDK use key A, use key B, or reject the call?
```

That choice determines which credential the client uses for later requests
to the `orders` container. The sync and async APIs need the same explicit
rule, so the customer does not have to discover which credential takes
precedence.

This is a Python wrapper contract decision, not a missing Rust-driver capability.

**Current decision; approval is not recorded**

Both sync and async methods use the embedded key. A separate `credential` keyword raises
`TypeError` whenever it is supplied, even as `None`, `False`, or an empty
string.
The normal constructor remains the route for a separate key or Entra credential.

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

**Omitting `credential` is different from setting it to `None`**

Some customer apps keep reusable arguments in a dictionary. `**settings`
passes every entry as a named argument, so this call still supplies
`credential=None` and raises `TypeError`:

```python
settings = {"credential": None, "consistency_level": "Session"}
client = CosmosClient.from_connection_string(connection_string, **settings)
```

For the connection-string call, use settings that omit the entry:

```python
connection_string_settings = {"consistency_level": "Session"}
client = CosmosClient.from_connection_string(
    connection_string, **connection_string_settings
)
```

This uses the embedded account key without changing a dictionary that other
customer calls might still need. Other supported client settings remain
available.

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

## 2 - Creating a database

**API:** `CosmosClient.create_database`, synchronous and asynchronous clients.

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

## 3 - Creating a database if it does not exist

**API:** `CosmosClient.create_database_if_not_exists`, synchronous and
asynchronous clients.

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

The argument rules and response-hook contract explained in section 2 also
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
settings, as explained in section 2.

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

As explained in section 2, both clients use `response_hook(headers, properties)`
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

Together with the shared changes in section 2, these rules require customers
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

As in section 2, the signature shows supported named options explicitly
for review. The synchronous client accepts the same arguments and returns
its corresponding `DatabaseProxy`.

Returning only the database object remains the default.
`return_properties=True` already exists; it is not a new return form.
Its properties and headers come from the final successful response
described above.

## 4 - Listing databases

**API:** `CosmosClient.list_databases`, synchronous and asynchronous clients.

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

Section 12 consolidates this timing change across database and container
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

## 5 - Querying databases

**API:** `CosmosClient.query_databases`, synchronous and asynchronous clients.

**Why the customer calls this API**

The customer app needs to find databases matching a condition, rather than
retrieve every database as in section 4. For example, it wants the properties
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

As in section 4, results are fetched during iteration. The example uses the
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

**Shared changes from section 4**

The page-size, response-hook timing, timeout and settings-copying changes in
section 4 also apply here, as does the proposal to use `request_options`
and deprecate the old dictionary name.

For `query_databases`, the SDK previously invoked the customer's
`response_hook(headers)` before returning the iterator. It now returns the
iterator first and invokes that same one-argument hook after each successful
service page, including empty pages. Customer code must start iteration before
expecting the hook to run and account for multiple invocations. Section 12
consolidates the timing comparison; no results-iterator argument is added here.

The current wrapper also rejects `session_token`, `populate_query_metrics`,
`availability_strategy`, `no_response` and `content_type`, including explicit
`None` or `False` and their entries in the selected settings dictionary.
Removal approval remains limited to forms established to have been ignored;
the blanket rejection is not an approved compatibility decision.

**Decision requested; approval is not recorded**

Approve or revise the required query argument, named optional settings,
early query validation, fixed query-parameter values and shared changes from
section 4.

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

## 6 - Deleting a database

**API:** `CosmosClient.delete_database`, synchronous and asynchronous clients.

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

## 7 - Reading database properties

**API:** `DatabaseProxy.read`, synchronous and asynchronous clients.

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

As with deletion in section 6, the proposal removes arguments that legacy
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

## 8 - Creating a container

**API:** `DatabaseProxy.create_container`, synchronous and asynchronous clients.

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

As in sections 6 and 7, legacy asynchronous handling of
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

## 9 - Creating a container if it does not exist

**API:** `DatabaseProxy.create_container_if_not_exists`, synchronous and asynchronous clients.

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

**Proposed breaking change: use the argument rules from section 8**

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
raises `TypeError`, as explained in section 8.

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
section 8: the current implementation rejects the keyword, but its legacy
handling through `**kwargs` remains unverified. That rejection is not yet
an approved removal decision.

**Decision requested; approval is not recorded**

Approve or revise applying section 8's argument rules and verified
ignored-argument removals to this API, including when the container already
exists.

**Asynchronous-client signature for review**

The expanded calling contract matches section 8. The implementation
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

## 10 - Deleting a container

**API:** `DatabaseProxy.delete_container`, synchronous and asynchronous clients.

**Why the customer calls this API**

The customer wants to remove a test `orders` container and its stored orders
while keeping the `sales` database and its other containers.

```python
await database.delete_container("orders")
```

Success returns `None`. Unlike database deletion in section 6, this operation
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
callers could supply it through `**kwargs`. As in section 6, the current
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

## 12 - Listing containers

**API:** `DatabaseProxy.list_containers`

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
`request_options` proposal in section 4 also applies here.

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

## 13 - Querying containers

**API:** `DatabaseProxy.query_containers`, synchronous and asynchronous clients.

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

As explained in section 5, `@id` supplies a value separately from the SQL
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

**Response-hook timing follows section 12**

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
both arguments and consume results outside the hook. Section 12 explains
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
decision in section 12 and `request_options` proposal in section 4 also
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

## 14 - Replacing container settings

**API:** `DatabaseProxy.replace_container`

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

**Other public changes:** Non-`None` per-call `read_timeout` is rejected;
`None` is discarded. Configure socket timeouts on the client instead.
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
Refer to creating a container (section 8) for named policy
arguments and database creation (section 2) for independent
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

## 15 - Reading container properties

**API:** `ContainerProxy.read`

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

**Other public changes:** Reject non-`None` per-call `read_timeout`; discard
`None`. Configure socket timeouts on the client instead. Unsupported Rust
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
database creation (section 2). Argument naming and socket-setting
rules follow reading database properties (section 7).

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

## 16 - Reading an item

**API:** `ContainerProxy.read_item`

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
| A per-read consistency setting could be overwritten by the driver's client setting. | Pass supported read settings through the driver's actual consistency option, not only a custom header. This also controls automatic cached-session-token selection. |
| Per-read `availability_strategy=True` replaced the client's configured hedge threshold with the default. | Preserve the client's first threshold, as legacy does. A client configured for 20 ms keeps 20 ms, not 500 ms. With no configured client strategy, `True` uses 500 ms; `False` disables the item strategy and an explicit dictionary supplies its own threshold. |

For example, with a client configured for Session consistency:

```python
order = container.read_item(
    "order-42", partition_key="tenant-a",
    request_options={"consistencyLevel": "Eventual"},
)
```

Legacy forwards the requested read level. Before the correction, Rust could
still send the client's Session strategy and cached token. The binding now
selects Eventual for this read without changing the client or preliminary
metadata settings. `Session` and `Strong` use the same mapping already used
for client settings; omitting the override preserves inherited behavior.
Actual service guarantees still require comparison on a suitably configured
account, not just inspection of an outgoing request.

**Conditional results:** `IfModified` uses If-None-Match; an unchanged item
returns an empty `CosmosDict` on 304. If-Match on item GET is service-enforced,
not a client-side version comparison: preserve 200 if that is what the service
returns, and preserve a real service 412 as `CosmosAccessConditionFailedError`.
Do not promise that stale If-Match on GET always fails with 412.

**Customer migration:** Pass post triggers and conditions by keyword and remove
retired query metrics arguments. Do not rely on modifying hook arguments to
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
metadata-cache lock consumes time too. `timeout=None` leaves this overall
budget unset and clears a nested timeout; separate transport settings still
apply. Python initialization, parsing and synchronous callback code are not
forcibly interrupted at every instruction. The async client requests
cancellation of pending binding work, but cannot guarantee immediate
cancellation of work already received by the service backend.

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

The binding has been rebuilt against a pinned Rust driver `main` revision.
The included fixes cover version 1 routing for long/non-ASCII keys and
parent-aware session-token lookup. Live split behavior still needs
verification; a dependency update is not service-level proof.

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
| Read an order in an older partitionless/system-key container | Legacy can supply the special empty key representation. The driver still cannot represent it equivalently and does not retain the older `systemKey` flag. The driver must supply those capabilities and our binding must integrate them; null and undefined keys are not substitutes. |
| Explicitly request `BoundedStaleness` or `ConsistentPrefix` on one read | Legacy forwards `request_options={"consistencyLevel": ...}`. The driver has no equivalent explicit read strategy. The binding now raises `NotImplementedError` instead of accepting a setting the driver can override. Driver support or an approved restriction is needed; inheriting an account default is not an explicit per-read override. |
| Limit connection setup or response inactivity for this read | Legacy supports per-call `connection_timeout` and `read_timeout`. The Rust item path rejects non-`None` values. An overall `timeout` does not replace those separate controls. Driver support or an approved compatibility change is required. |
| Try additional regions while earlier read attempts remain slow | Legacy can progressively start attempts in additional regions. Rust supports the initial primary/alternate race, not the additional `threshold_steps_ms` progression. The driver must provide equivalent behavior or the changed availability contract needs approval. |
| Obtain every original service response header | The driver preserves selected fields, not the complete map. An original `date` or diagnostic header can be absent even when the order is returned. Copying hook arguments cannot restore it; driver preservation and binding forwarding are required. |
| Inspect or modify the raw outgoing request | The Rust path rejects `raw_request_hook`. The driver needs a supported interception capability before the binding can restore it. Static headers and a success callback are not equivalent. |
| Inspect the raw pipeline response object | `raw_response_hook` is also rejected. Its replacement/removal contract still needs classification and approval; selected response headers alone do not replace that object. |
| Distinguish a permission failure from a temporary failure during physical-map loading | The default eager-resolution path on `main` can discard the underlying metadata error and return a generic topology-resolution failure. Typed error preservation in other topology-planning paths does not close this particular gap. The driver must preserve the cause and our binding must expose it. |

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
verification requirements. Forwarding priority, throughput-bucket and trigger
headers likewise does not establish their service effects.

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
    post_trigger_include: Optional[str] = None,
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

## 17 - Creating an item

**API:** `ContainerProxy.create_item`

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
below one second are not rounded up. Lazy driver initialization consumes
elapsed budget but is not forcibly interrupted. The client's
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

**Customer migration:** Pass triggers and indexing directives by keyword;
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

The binding is rebuilt against a pinned Rust driver `main` revision. Checked
partition-key construction and the changed query-planning API are integrated.
The build now includes corrected version 1 routing for long/non-ASCII keys,
parent-aware session lookup and automatic cached-token suppression on ordinary
single-write-region creates. These are integrated capabilities, not new
requests to the driver team. Live split and account behavior remain pending.

| Customer need | Difference and required decision or work |
|---|---|
| Continue writing to an older container created without a partition key | Legacy can send the special empty key header. The driver cannot represent it equivalently and does not retain the older container's system-key flag. Driver support and binding integration are required; removing these customers' write support has not been approved. |
| Decide whether to retry after the result of a create is uncertain | Legacy exposes a write-retry opt-in for these failures. The driver can retry creates without the equivalent per-write control, while the Rust item path rejects non-`None` `retry_write`, including zero. The driver must provide the control or the changed retry contract needs approval. |
| Reuse a saved session token across calls | Legacy omits explicit tokens on ordinary single-write-region creates; Rust forwards them. Valid tokens did not break these creates on the single-write-region emulator. The confirmed difference is malformed input: `session_token="not-a-session-token"` is ignored by legacy, so the order is created, but Rust receives 400 and the order is not created. Decide whether preserving acceptance of malformed values is required; this is not a confirmed missing driver capability. Do not remove tokens indiscriminately: on multi-write-region accounts they can require a write region to catch up with data the customer app already read elsewhere. Failover and container-recreation behavior remain unverified. |
| Keep writing after a container is recreated under the same name | Driver recovery can refresh the container identity, but retains the already-extracted logical key. If the definition changed from `/customerId` to `/region`, the body needs a newly extracted value. The driver must expose compatible recovery and the binding must supply that value. |
| Bound connection setup or response waiting for this create | Legacy per-call `connection_timeout` and `read_timeout` have no equivalent driver controls. The Rust path rejects non-`None` values. A single overall `timeout` does not preserve those separate limits. |
| Start another eligible regional write while the first remains slow | Legacy can hedge writes with write-retry opt-in and suitable writable regions. Driver `main` does not hedge document creates. Accepting `availability_strategy` in Python does not preserve that behavior; driver support or an approved availability change is needed. |
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
may have saved the order. This is not evidence of two orders with the same ID
and partition key. Nor does any 409 prove that the existing order contains
this call's intended data. Timeout or async cancellation also cannot undo a
write already accepted by the service backend.

**Preliminary requests have their own consequences**

Before sending the order, driver `main` defaults to obtaining the physical
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

`raw_response_hook` is also rejected. It formerly received a raw pipeline
response object, rather than the parsed headers/body given to `response_hook`.
The replacement or removal of that contract still needs classification and
approval; preserving selected headers alone does not settle it.

**New contract (async-client signature):**

```python
async def create_item(
    self,
    body: dict[str, Any],
    *,
    pre_trigger_include: Optional[str] = None,
    post_trigger_include: Optional[str] = None,
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
for triggers, account-dependent session behavior, uncertain write outcomes,
recreation and metadata failures remain open. This entry is self-contained
for board review; it does not record approval of the proposed changes or
removal of unsupported behavior.

## 18 - Reading known items

**API:** `ContainerProxy.read_items`

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
synchronous requests may finish later. Lazy driver initialization consumes
elapsed budget but is not forcibly interrupted.

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
renewed for each group of items. Refer to reading an item (section 16) for the shared-budget example
and database creation (section 2) for hook isolation, here applied
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

## 19 - Reading every item

**API:** `ContainerProxy.read_all_items` (sync and async)

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
none of the next budget. Async cancellation waits for outstanding work to stop. Lazy
synchronous driver initialization consumes elapsed budget but is not forcibly
interrupted.

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
budget in database get-or-create (section 3).

The hook here receives `(headers, body)` with a copied `Documents` envelope,
for example `{"Documents": [{"id": "order-42"}]}`, not just the one argument
used by listing databases (section 4). Editing that copy cannot
change returned items or the bookmark. An exception normally used to end
iteration, such as `StopIteration`, becomes `RuntimeError` so a hook cannot
make a failed scan appear complete. Other hook exceptions propagate without
fetching the page again. Only one fetch at a time may use a given result iterator.

**Remaining driver limitations and ownership**

| Customer requirement | Remaining difference |
|---|---|
| Set connection or read-inactivity limits for one scan | The Rust driver lacks those per-operation controls. An overall page-fetch budget does not provide the same limits. |
| Start reads in additional regions when earlier attempts remain slow | Rust supports one primary and one alternate request, not progressively adding more regions. If both are slow, a third healthy region is not added merely because a further delay has elapsed. The legacy `threshold_steps_ms` setting is accepted but dropped on the Rust path; this is a recorded driver design difference. |
| Inspect original response headers | The driver returns selected fields rather than the original complete header map. An original header such as `date` can be lost. |
| Inspect or edit the outgoing HTTP request with `raw_request_hook` | The callback is unsupported. Removing it is not equivalent if customer code depends on its inspection or changes. |

The driver team owns those capabilities. The Python SDK/binding team owns
verifying that the scan preserves the required results, options,
and paging behavior. Overrides of driver-owned request headers require a
separate compatibility decision; they are not the same as adding an
application-specific header. This read-all review does not establish that
public `query_items` has completed migration. It records no board approval.

## 20 - Polling item changes

**API:** `ContainerProxy.query_items_change_feed` (sync and async)

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
A failed/cancelled result iterator cannot be reused.
Concurrent fetches on one result iterator are rejected.

**Timeout contract:** One explicit supported timeout budget per public page,
including metadata, routing, retries and internal polls. Customer processing
between pages is excluded. Async cancellation waits for outstanding work to stop; lazy
synchronous driver initialization consumes elapsed budget but is not forcibly
interrupted. Available response charges are aggregated, not represented as
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

**Customer migration:** Use named arguments and finish existing polling work
on the earlier SDK version before upgrading; its tokens are not interchangeable
with Rust tokens. Blocked scopes/options remain release gaps, not a reason
to offer a legacy backend switch. Persist the bookmark from the caught-up empty page and
start a fresh result iterator for the next polling cycle. This is a draft for board
review, not recorded board approval.

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
Refer to reading every item (section 19) for saving complete pages,
separate page budgets, failed-iterator handling and hooks that must not silently
end iteration. Do not transfer bookmarks between those APIs or between backends.

**Why the current Rust restriction matters:** suppose a scope covers storage
partitions A and B. A has no changes, but B has two. If the driver declares
"caught up" after checking only A, the application can miss B's available work.
The current Rust path rejects such multi-partition scopes instead of returning
that misleading result. Defining completion across the whole requested scope
requires driver and binding work; it is not an approved removal of
cross-partition polling.

## 21 - Getting a database client from properties

**API:** `CosmosClient.get_database_client`

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

## 22 - Excluding resource tokens and Cosmos user and permission APIs

The customer previously let a restricted application read the `orders`
container without giving it an account key. A trusted application server
created a **Cosmos database user**, a named object holding permissions inside
the `sales` database. It then created a permission describing the allowed
resource and access mode. The service backend returned a **resource token**,
a temporary credential representing that permission.

That Cosmos user is not an Entra user, service principal, or managed
identity. A Cosmos permission is not a Cosmos DB role assignment for an Entra
identity.

**Before and after**

| Area | Before: legacy Python SDK | Rust-backed release |
|---|---|---|
| Authentication | Accepted account keys, Entra credentials, and Cosmos resource-token dictionaries or permission lists. | Supports account keys and Entra credentials. Resource-token authentication is intentionally excluded. |
| Cosmos database users | Exposed methods to create, read, list, query, replace, upsert, and delete users, plus local `get_user_client` navigation. | This API family is excluded, including the local navigation method. |
| Cosmos resource permissions | Exposed methods to create, read, list, query, replace, upsert, and delete permissions used by resource-token clients. | This API family is excluded, even when an administrator would call it using an account key. |
| Entra identities | Could authenticate using an Entra token credential. | Remain supported. The exclusion does not remove service-principal or managed-identity authentication. |

**Why the contract changes**

The Rust driver supports account-key and Entra authentication, not
Cosmos resource-token authentication. The SDK will follow that supported
authentication model rather than add a separate resource-token implementation.
It will also omit the Cosmos user and permission APIs dedicated to managing
that model. These are deliberate exclusions, not features waiting for driver
support.

Using an account key to create a permission and using the resulting resource
token are different operations. Key support alone does not imply that the SDK
will retain permission management. Likewise, obtaining a local `UserProxy`
without a service request is not useful navigation into an excluded API family.

**Affected APIs on both synchronous and asynchronous clients**

| Area | Excluded surface |
|---|---|
| Client construction | Resource-token dictionaries and permission lists supplied as `credential`. |
| `DatabaseProxy` | `list_users`, `query_users`, `get_user_client`, `create_user`, `upsert_user`, `replace_user`, `delete_user`. |
| `UserProxy` | `read`, `list_permissions`, `query_permissions`, `get_permission`, `create_permission`, `upsert_permission`, `replace_permission`, `delete_permission`. |

**Illustration: the legacy workflow will not carry forward**

Assume `database` is the trusted server's key-authenticated legacy client for
`sales`. This legacy example grants read access to the `orders` container:

```python
user = database.create_user({"id": "customer-17"})
permission = user.create_permission({
    "id": "read-orders",
    "permissionMode": "read",
    "resource": "dbs/sales/colls/orders",
})
resource_token = permission.properties["_token"]
restricted_client = CosmosClient(
    ACCOUNT_URL,
    credential={"dbs/sales/colls/orders": resource_token},
)
```

The Rust-backed release supports neither those user/permission calls nor the
resource-token client. Passing that token as an account key or returning it
from an Entra credential does not turn it into a supported credential.

**Customer effect**

The customer must change this access design before moving it to the Rust-backed
release. An application can use an Entra identity with the required Cosmos DB
role assignment, or make requests through a trusted application server using
an account key or Entra credential. That server must enforce the end user's
access rules. Do not replace a restricted token on a browser or phone with an
account key.

Existing Cosmos permissions are not automatically converted into Cosmos DB
role assignments for Entra identities. Changing only the `credential` argument
does not preserve their access rules. This is an SDK support decision, not a claim that the Cosmos DB
service has removed users, permissions, or resource tokens.

## 23 - Omitting stored procedures without confusing management and execution

The customer app saves an order and its receipt together. A **stored
procedure** is a JavaScript function saved on a Cosmos DB for NoSQL container
and run by the service backend. Its item changes form one transaction:
both writes are saved, or neither is saved. They must target the same
partition key value in the same container.

Deploying that function and executing it are different customer actions.
The customer can deploy `place_order` once, then execute it for each new
order. The Python customer app does not run the JavaScript itself.

**Before and after**

| Customer action | Before: legacy Python SDK | Planned Rust-backed release |
|---|---|---|
| Create, get, list, replace, or delete the saved definition | Available through `ScriptsProxy`. | Omitted for now. Azure Resource Manager's Cosmos management API can manage definitions through a separate management client. |
| Query saved definitions using SQL | `query_stored_procedures` returns matching definitions. | Omitted for now. The management API has no equivalent SQL-query operation; listing and filtering in the customer app changes the contract. |
| Execute the function against items | `execute_stored_procedure` sends arguments and a partition key and returns the function's response. | Omitted for now. The management API cannot execute it. |

The affected methods on both sync and async `ScriptsProxy` are
`list_stored_procedures`, `query_stored_procedures`, `get_stored_procedure`,
`create_stored_procedure`, `replace_stored_procedure`,
`delete_stored_procedure`, and `execute_stored_procedure`.

**Why the distinction matters**

**Azure Resource Manager (ARM)** is Azure's deployment and configuration
service. It routes Cosmos management requests to the **Cosmos management
API**, which creates and maintains Cosmos resources and saved JavaScript.
The Python `azure-mgmt-cosmosdb` package calls that API; it is not the
`azure-cosmos` data client.

That management API can save `place_order`, but it cannot run the function
against order items. Moving deployment to ARM therefore does not replace
the execution call omitted from this release. This is not a claim that the
service backend can no longer run stored procedures or that future SDK
releases must exclude them permanently.

ARM's create-or-update operation also differs from the legacy methods:
it can update an existing definition instead of raising a create-only
duplicate-ID error, or create a missing definition instead of raising a
replace-only missing-ID error. Management calls need an authorized Entra
identity and subscription/resource-group information, not just an account key.

The management API is owned by a separate service team from the Python data
SDK/shared Rust driver work. Changes to its supported operations require
coordination with those owners. A missing service capability cannot be
supplied merely by changing a Python wrapper. This ownership boundary also
applies to the management alternatives in entries 24-26.

**Illustration: deployment is not execution**

Assume `place_order` is already deployed on `orders`, partitioned by
`/customerId`. Its JavaScript writes the supplied order and a receipt with
the same customer ID, then sets its response to their IDs. Legacy Python calls:

```python
order = {"id": "order-42", "customerId": "customer-42", "type": "order", "total": 25}
result = container.scripts.execute_stored_procedure(
    sproc="place_order", partition_key="customer-42", params=[order]
)
# result: {'orderId': 'order-42', 'receiptId': 'order-42-receipt'}
```

Deploying that same JavaScript with the management SDK does not make this
execution call available in the Rust-backed SDK. The customer must retain a
supported execution client or redesign the transaction. Two independent item
writes are not equivalent. A same-partition transactional batch is a candidate
for this fixed two-write example, subject to its own SDK support; it is not an
automatic replacement for functions that read data and decide further writes
inside the transaction.

This entry records the planned public contract, not board approval.

## 24 - Reviewing UDF management separately from query use

The customer app needs order queries to calculate a review category using a
shared rule. A **user-defined function (UDF)** is JavaScript saved on the
container and called inside SQL, for example `udf.reviewBand(c.total)`.
It computes a value from its arguments; it cannot read another item, write
an order, or create a receipt.

**Decision status: pending for definition management.** The decision about
creating and maintaining saved functions is separate from the decision
about using them in order queries.

| Customer action | Legacy Python | Boundary for the Rust-backed release |
|---|---|---|
| Create, get, list, replace, or delete the function definition | `ScriptsProxy` management methods. | Release scope remains pending. The separate Cosmos management SDK has definition-management equivalents. |
| Query function definitions with SQL | `query_user_defined_functions`. | Scope remains pending; management listing/filtering is not the same SQL-query contract. |
| Call a saved function while querying orders | `query_items` with `udf.functionId(...)`. | A separate query capability, not removed by a definition-management decision. |

The six management methods are `list_user_defined_functions`,
`query_user_defined_functions`, `get_user_defined_function`,
`create_user_defined_function`, `replace_user_defined_function`, and
`delete_user_defined_function`, on both sync and async clients.

Assume `reviewBand` returns `"manual"` for totals of at least 500 and
`"standard"` otherwise. It is already registered, and `order-42` has
`total=25` in the `customer-42` partition. The legacy customer app reads
the calculated category without uploading JavaScript again:

```python
rows = container.query_items(
    query=(
        "SELECT c.id, udf.reviewBand(c.total) AS reviewBand FROM c "
        "WHERE c.type = 'order' AND c.id = @id"
    ),
    parameters=[{"name": "@id", "value": "order-42"}],
    partition_key="customer-42",
)
for row in rows:
    print(row)
# {'id': 'order-42', 'reviewBand': 'standard'}
```

Azure Resource Manager (**ARM**) can deploy the function but does not run
this item query. Its create-or-update operation differs from legacy
create-only and replace-only behavior. Deployment also needs an Entra
identity allowed to manage these resources, the subscription ID, and the
resource group, account, database, and container names.

**Customer impact to decide:** If definition management moves to ARM,
customers must change deployment and any definition-query workflow.
That must not silently remove ordinary queries using deployed functions.
Customers need a clear answer about both jobs: how to deploy the function
and whether their existing queries will keep working.
For a simple threshold, direct SQL may be preferable; using a UDF does not
guarantee lower query cost.

## 25 - Reviewing trigger management separately from item writes

The customer app needs to validate an order and save its receipt as part of
the same write. A **trigger** is saved JavaScript requested on an item
operation. A pre-trigger runs before the item change; a post-trigger runs
after the change but before the transaction completes. A **transaction**
saves all those changes together or discards them together on failure.
Additional item changes must stay in the same container and **logical
partition**, the items sharing one partition key value.

**Decision status: pending for definition management.** This does not
approve removing `pre_trigger_include` or `post_trigger_include`.

| Customer action | Legacy Python | Boundary for the Rust-backed release |
|---|---|---|
| Create, get, list, replace, or delete a trigger definition | `ScriptsProxy` management methods. | Scope remains pending; the separate Cosmos management SDK offers definition management. |
| Query saved definitions with SQL | `query_triggers`. | Scope remains pending; ARM has no equivalent SQL query over definitions. |
| Request a deployed trigger on an item write | Trigger options on that write. | A separate runtime contract, not an ARM management operation. |

The six management methods are `list_triggers`, `query_triggers`,
`get_trigger`, `create_trigger`, `replace_trigger`, and `delete_trigger`,
on both sync and async clients.

Assume `validateOrder` rejects an invalid total and `auditOrder` writes the
receipt, and both are registered for creates. The customer app requests them:

```python
container.create_item(
    body={"id": "order-43", "customerId": "customer-42", "type": "order", "total": 25},
    pre_trigger_include="validateOrder",
    post_trigger_include="auditOrder",
)
```

Registration alone does not run either function. A writer omitting the
options bypasses them, so they cannot enforce a rule across every writer.
A post-trigger is not an asynchronous notification after a successful commit.

**Customer impact to decide:** Moving deployment to ARM changes credentials,
resource identifiers, and create/replace semantics: ARM creates or updates
instead of preserving both legacy failure rules. It does not replace this
item write. Customers also need an explicit answer about which item
operations will keep supporting these options, including patch operations.

Patch trigger compatibility remains unresolved. For example, if a customer
requests an audit-stamping trigger when patching an order's status, success
must include the requested trigger's effects, not just the status change.
A successful create with a trigger does not establish that patches execute
it correctly. The September 30 sync/async comparison now reproduces a
failure for increments: legacy runs each requested trigger, while Rust
returns 400 without changing the order. Other strategy cases still need
verification. This observed failure is not a decision to remove trigger support or an
approval of the proposed management-API change.

## 26 - Reviewing conflict resolution separately from container management

The customer app can change the same order in two regions that accept
writes. Those regions may accept different delivery instructions before the
service backend brings the versions together. A **conflict-resolution
policy** tells the service backend how to choose the final version.
Last-writer-wins chooses automatically. A **merge procedure**, a saved
JavaScript function called by the service backend, can instead supply the
customer's rule. The **conflict feed**
contains records left for the customer app, not an audit of every write.

**Decision status: pending for conflict-feed APIs.** These methods handle
unresolved item changes, not account or container deployment. They cannot
be replaced just by moving deployment to the management API.

| Customer action | Legacy Python | Management alternative |
|---|---|---|
| Choose the container policy at creation or deploy a merge procedure | Container creation and stored-procedure definition APIs. | ARM can configure the policy and deploy the procedure. |
| Read unresolved conflicts | `list_conflicts`, `query_conflicts`, `get_conflict`. | No equivalent in the Cosmos management SQL Resources inventory. |
| Apply the approved outcome and remove the handled record | Item operations followed by `delete_conflict`. | ARM does not replace the data writes or conflict deletion. |

The four conflict methods exist on both sync and async `ContainerProxy`.
For example, the legacy app inspects a record in the customer's partition:

```python
conflict = container.get_conflict(
    conflict="conflict-1", partition_key="customer-42"
)
print(conflict["operationType"])
```

The record ID is not the order ID. Reading or deleting the record does not
merge competing versions. The customer must decide the outcome, apply it
safely to the item, and only then remove the handled record. Item writes
and conflict deletion are separate operations. The customer app must
recover safely if it stops after writing the item but before deleting
the record.

**Customer impact to decide:** If these APIs are retained, Rust needs the
conflict-feed operations. If omitted, the release must explain how customers
will operate manual resolution and handle failed custom merges. Moving
container deployment to ARM is not sufficient. Nor does omitting explicit
stored-procedure execution necessarily disable a merge procedure invoked
automatically by the service backend.

Removal remains blocked on the explicit scope decision. Retaining the APIs
requires an equivalent implementation; omitting them requires a viable
customer migration for the unresolved-conflict workflow described above.

## 27 - Discovering ranges for parallel order reads

**API:** `ContainerProxy.read_feed_ranges`, synchronous and asynchronous.

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
| `connection_timeout`, `read_timeout` | Per-call controls for connection setup and waiting without receiving data on those fetches. |
| `response_hook` | Headers and body for each successful partition-range response; no callback when cached ranges avoided the requests. |
| `raw_request_hook`, `raw_response_hook` | Access to the outgoing pipeline request or HTTP response object; the request hook could also modify the request. |
| `headers` | Custom headers on partition-range requests. |
| `initial_headers`, `excluded_locations` | Accepted keywords, but no corresponding custom-header or region-exclusion behavior on partition-range requests. |

The legacy controls above did not apply to the preliminary container-property
lookup. A timeout spanning that lookup and all range fetches would be a new
guarantee, not restoration of the old per-fetch limit.

The current Rust lookup rejects additional per-call settings. Removing
`timeout=5`, for example, makes the call run without the requested limit.
That is not equivalent behavior. The driver must expose the relevant request
controls and response details through the binding; the Python wrapper owns
invoking the customer's callbacks.

| Area | New contract and customer reason |
|---|---|
| Refresh flag | Require `True` or `False`. Other values raise `TypeError` when the iterable is constructed; `"false"` is not a boolean setting. |
| Extra options | The current Rust lookup rejects additional per-call options with `NotImplementedError` when fetching. Restore confirmed legacy request controls and the response callback without running legacy Python. Separately decide compatibility for `initial_headers` and `excluded_locations`, which this legacy API did not apply as header or routing settings. |
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

## 29 - Replacing an existing order

**API:** `ContainerProxy.replace_item`, synchronous and asynchronous clients.

**Customer motivation and retained behavior**

The customer wants to replace the complete contents of an existing order:

```python
replacement = {
    "id": "order-42", "tenant": "tenant-a", "status": "shipped"
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
saved_order = orders.read_item("order-42", partition_key="tenant-a")
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
second. Initialization is counted but not forcibly interrupted. Timeout or
cancellation does not roll back a write already accepted by the service backend.
Legacy ID validation is restored: for example, `"order/42"` in the replacement
body fails locally rather than proceeding into driver acquisition.

**Customer-visible restrictions requiring migration treatment**

| Existing customer behavior | Rust-backed restriction and impact |
|---|---|
| Replace orders in a legacy container with no partition key, or with a service-created system key | No-partition-key behavior is not preserved, and the driver loses the system-key flag needed for some missing-key cases. These older containers cannot be declared equivalent to a normal `/tenant` container. |
| Control ambiguous write retries through `retry_write` | The per-call option is rejected. The driver's retry policy does not preserve legacy opt-in. A replacement guarded by ETag V1 can commit as V2, lose its response, and then receive a stale-condition error if retried with V1. The customer-visible failure does not prove the first write failed. |
| Set connection or read-inactivity limits on one replacement | Per-call `connection_timeout` and `read_timeout` are rejected. The overall `timeout` does not provide the same controls. |
| Inspect all original service response headers | The driver reconstructs selected headers. A customer can receive ETag and request charge but lose an unmodeled header such as `date`. A response hook cannot recover discarded information. |
| Inspect or modify the outgoing HTTP request with `raw_request_hook` | The callback is rejected; the current production driver has no equivalent supported interception point. |
| Inspect the legacy HTTP pipeline response with `raw_response_hook` | The callback is rejected. It receives a pipeline response object, unlike `response_hook`'s headers and parsed body. For example, customer code reading `pipeline_response.http_response.status_code` cannot migrate unchanged. Its complete replacement contract remains unclassified. |
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
| Request a replacement trigger | A validation pre-trigger rejects an invalid order and leaves the original unchanged; an allowed replacement succeeds. A post-trigger produces its expected observable result. Sending trigger names alone is insufficient. |
| Exclude West US with a cold container cache | Observe the metadata lookup and replacement destinations separately, then repeat with a warm cache. Account bootstrap and all-regions-excluded fallback are not covered by a blanket no-traffic promise. |
| Lose connectivity before delivery versus lose the response after commit | Record attempts, regions, the customer-visible result, and the stored order separately for both cases. Repeat the committed-write case with an ETag condition: a retry can report a stale condition even though the first write succeeded. |

The SDK team owns Python/binding integration and verification; driver capability
work belongs to the driver team. The recorded retry-policy difference does not
close other capability gaps or approve the raw response-hook contract.

## 30 - Requiring a finite window for unordered DISTINCT

**API:** `ContainerProxy.query_items`

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

## 31 - Keeping database throughput results independent of response hooks

**API:** Synchronous/asynchronous `DatabaseProxy.get_throughput`.
The public-name removal below also applies to `ContainerProxy`.

**Why does the customer read throughput?**

The customer app checks the shared capacity of its database before
accepting a larger order workload.

**Why this needs a public decision**

Reading database throughput is already supported by the Rust driver. Removing
the deprecated public alias and applying the common response-hook contract
are Python wrapper cleanup and compatibility decisions; neither requires a
new Rust driver capability.

Missing per-call connection and read-inactivity timeout controls and original
response headers are separate Rust driver gaps. An overall operation timeout
does not replace those controls, and selected response fields do not preserve
the complete service header map. The cleanup does not resolve or approve
removal of those capabilities.

**Which response-hook rules apply?**

The common response-hook contract and required customer changes are explained
in section 2. The same rules apply here.

Here, an *offer* is the record containing the database's throughput settings,
such as manual throughput of 4,000 RU/s. `response_hook(headers, offers)`
receives response headers and a list containing that record. The method
itself returns one `ThroughputProperties` object, not a list. The response
hook runs once after a successful read.

**Which public names remain in v5?**

The customer app needs one method to read configured capacity and another to
change it. V5 keeps `get_throughput` and `replace_throughput` on database and
container clients. The deprecated synchronous `read_offer` aliases were
removed on September 27, 2026 following the review decision:

```python
# Before v5:
throughput = database.read_offer()

# V5:
throughput = database.get_throughput()
```

For a container, change `container.read_offer()` to
`container.get_throughput()`. An unchanged old call now raises `AttributeError`,
not a deprecation warning. Asynchronous clients already use `get_throughput`.

Neither client exposes a public `replace_offer` alias. The internal offer
operations remain: they read and update the service backend's throughput
record on behalf of the public methods. This name cleanup does not resolve
timeout scope or original-header loss in the Rust driver.

**What happens to an unsupported input?**

The shared rule under
"Unsupported settings must not silently run legacy Python"
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

**Review disposition:** Implemented for review; formal board approval is not
recorded. Targeted live response hook and input-ownership checks passed on
September 27, 2026; broader service-level verification remains pending.
The v5 alias removal was explicitly approved; that
decision is separate from formal board approval of the response hook change.

## 32 - Reading container throughput without changing the result or execution path

**API:** Synchronous/asynchronous `ContainerProxy.get_throughput`.

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

Missing per-call connection and read-inactivity timeout controls and original
response headers remain separate Rust driver gaps. An overall operation timeout
does not replace those controls, and selected response fields do not preserve
the complete service header map. The wrapper corrections do not close them.

**Which response-hook rules apply?**

The common contract and required customer changes follow
section 2. The throughput-specific response-hook
arguments are explained in
section 31.

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

**What happens to unsupported inputs?**

The shared rule under
"Unsupported settings must not silently run legacy Python"
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

**Review disposition:** Implemented following approval
on September 27, 2026. Formal board approval is not recorded. This read review
does not approve throughput replacement or close the driver header and retry
information gaps. Broader service-level verification remains pending.

## 33 - Persisting patch tracking information in the customer's order

**API:** `ContainerProxy.patch_item`
**Review disposition:** Pending compatibility decision; approval is not recorded.

The customer app increments `refund_attempts` from 5 to 6. On the reviewed Rust
path, the stored and returned order also contains `_azsdkPatchTracking`.
Legacy Python does not add that property in the paired increment.

The driver uses this information to recognize a patch after a lost response.
For example, if the increment is saved but its response is lost, retrying it
without recognizing the earlier update could increment the value again.
The question here is whether the SDK may add tracking information to the
customer's document.

The September 30, 2026 comparison confirmed the stored/returned property,
not a failure in the customer's application. An application that validates
allowed fields could be affected, but that outcome was not reproduced.
Hiding the property only in the Python return value would not remove it
from the stored order or from later reads.

Decide whether to accept and document the added property or require a
different retained contract. This is not approval to remove the driver's
retry-safety information. Lost-response retry behavior remains unverified.

## 34 - Accepting more than ten patch instructions

**API:** `ContainerProxy.patch_item`
**Review disposition:** Pending compatibility decision; approval is not recorded.

The customer app submits one patch list containing eleven instructions. In the
paired synchronous and asynchronous comparison, legacy Python rejects the
list with status 400; the Rust path accepts it.

The Rust driver can apply that list using its client-side patch implementation.
The driver is not missing the ability to perform the update. The compatibility
question is whether the Python SDK should preserve rejection of lists longer
than ten instructions or intentionally allow these calls.

Accepting the larger list changes which customer calls succeed. Retaining
the legacy limit would require explicit validation on the Rust path.
Neither choice has been approved. The observed acceptance does not establish
equivalence with legacy behavior.

## Shared customer-visible changes

### Older containers need their existing partition-key representation

The customer has an older `orders` container created without a
customer-defined partition key. It needs existing order reads and writes
to keep working after the SDK upgrade, without moving its data into a new
container.

Legacy Python represents the empty key for these item operations by sending
`x-ms-documentdb-partitionkey: []`. The Rust driver's empty-key representation
instead omits that header. Those are different requests. The current binding
rejects explicit partitionless item inputs, so an unchanged customer call can
fail before sending the item operation.

A related case occurs when the service backend upgrades the existing
container to the system-defined path `/_partitionKey`. The metadata flag
`systemKey: true` identifies that compatibility mode; the upgrade does not
automatically add `_partitionKey` to old order bodies.

```text
Container metadata: /_partitionKey, systemKey=true
Existing order-42:  {"id": "order-42", "status": "pending"}
    -> legacy SDK sees that the system-defined property is missing
    -> sends the empty-key representation []
```

The driver drops `systemKey` from its typed container information, so the
binding cannot make that same selection. Both pieces are needed: preserve
the flag to select the right representation and support sending `[]` instead
of rejecting it or omitting the header. The driver team owns those capabilities;
the Python SDK/binding team owns their integration.

For an ordinary `/tenant` container, `systemKey: false` or an absent flag
does not mean the container is unpartitioned. A missing `tenant` value uses
the different representation `[{}]`. If an order has an actual partition-key
value, including `_partitionKey` in an upgraded container, the SDK uses that
value rather than automatically sending `[]`.

These are unresolved item-operation compatibility gaps, not approval to
require customers to move their existing orders to a different container.

### Unsupported settings must not silently run legacy Python

The customer configures an order request because it needs a particular
behavior, not merely a successful call. For example, a callback that edits
an outgoing request must actually run if the SDK accepts it. The customer
needs an explicit error when that capability is unavailable, rather than
success achieved by silently using a different request implementation.

**Existing problem:** Some unsupported options silently caused a call to use
legacy Python instead, making those settings appear supported on Rust.

**Decision and reasoning:** Reject unsupported Rust settings on migrated
operations rather than silently run old Python code. A successful
call should mean the chosen configuration was honored.

**Customer migration:** Remove the unsupported option or use a supported
configuration. Listings may report the error only when iteration requests a
page. This rule applies to the reviewed APIs that explicitly adopt it, not
every method with any Rust implementation. Database and container
`get_throughput` now adopt it; throughput replacement still retains
option-dependent legacy paths. This decision does not assert that those
pending replacement differences have been fixed.

**Illustration:** a database listing with
`raw_request_hook=my_hook` must not quietly run the legacy request pipeline.
That hook would let customer code edit the outgoing HTTP request, a capability
the reviewed Rust path does not provide. The listing reports the unsupported
setting when execution reaches its validation, which can be during iteration.
Remove the option only if the application does not need it; otherwise the
missing capability must be resolved before that application can migrate.
This is different from `response_hook`, which observes a returned response.

### Timeout settings are explicit about their scope

The customer wants to limit how long it waits for an order read or for the
next page of results. If it allows five seconds for a page fetch, that should
not mean five new seconds for every internal request, nor should time spent
processing the previous page consume the next page's allowance.

The review must distinguish that overall operation budget from a socket
timeout, which limits a particular kind of network waiting.

**Existing problem:** Per-call timeout support differed between backends, and
some Rust-selected calls switched backends when given a timeout. Customers
could also mistake a page timeout for a limit on the whole listing.

**Decision and reasoning:** Separate client-level socket settings from supported
per-call operation timeouts. The reviewed validators require finite numeric
durations of at least one second, not booleans, and within the supported range.
Listing timeouts apply per page fetch by default, so time spent processing
previous results does not consume the next page's budget.

**Customer migration:** Where an API rejects per-call `read_timeout`, configure
socket timeouts when constructing `CosmosClient`, not on the individual
operation call. An operation budget and a page-fetch budget have different
scopes, as illustrated below. Setup that cannot be interrupted and cancellation
cleanup can delay return beyond the configured budget.
Database creation follows this initial-timeout validation rule and uses one
budget across setup and execution. Its binding enforces any remaining fraction
of a second; that is different from accepting a subsecond initial timeout.

**Illustration - socket setting versus operation budget:**

```python
client = CosmosClient(endpoint, credential=key, read_timeout=10)
database = client.get_database_client("sales")
properties = database.read(timeout=5)
```

The client-level `read_timeout` configures socket read waiting; `timeout=5`
limits this supported operation's work. They are not interchangeable.
`database.read(read_timeout=10)` now raises `TypeError`, while `None` is
discarded on APIs with this rule. Database get-or-create explicitly retains
the legacy per-call control, as described in
entry 3; do not generalize a
single API's restrictions to all methods.

| With `timeout=5` | Budget ownership |
|---|---|
| Database creation | Setup and creation share 5 seconds; see entry 2 |
| Database get-or-create | Read, possible create and possible recovery read share 5 seconds; see entry 3 |
| Reviewed paged listing | Each page fetch gets 5 seconds; application processing between pages does not consume the next budget |

For example, fetch page 1 in 2 seconds, process it for 30 seconds, then fetch
page 2 with a fresh 5-second budget. This is not a five-second limit on the
entire listing. Setup that cannot be interrupted and cancellation cleanup
retain the limits explained in entry 2.

### Rust response metadata includes an additional diagnostics header

The customer is investigating an unexpectedly slow order request and wants
to record the SDK's diagnostic information alongside the response. The
Rust-backed SDK can expose that information as an additional entry in the
response-header mapping, the dictionary of named response values.

The review must explain who adds that entry and what customer code may assume
about it. A customer that accepts only a fixed set of header names may need
to allow it; a customer looking for original service headers must not mistake
it for one.

**Existing problem:** Legacy response metadata did not expose the Rust
diagnostics header.

**Decision and reasoning:** The **Python Cosmos DB SDK** adds
`x-ms-cosmos-sdk-diagnostics` to Rust-backed response metadata when the binding
returns diagnostics. The Rust driver supplies the diagnostic information;
Python adds the header entry exposed to the application. This is not a header
received from the service backend.

**Customer migration:** Reading the header is optional, but strict header
allowlists may need updating. Treat its value as human-readable text, not a
stable format to parse. It is not guaranteed when no request or diagnostics
exist.

**Illustration - optional diagnostic text, not a service header:**

```python
properties = database.read()
headers = properties.get_response_headers()
summary = headers.get("x-ms-cosmos-sdk-diagnostics")
if summary is not None:
    print(summary)
```

The shared Rust driver collects diagnostic information, the compiled binding
formats a summary, and Python adds this entry to the mapping the customer
receives. It is neither an outgoing request header nor an original service
response header. Do not parse its text as a stable data format.
Allowing this extra entry does not resolve the loss of original service
response headers. Adding a summary cannot recover missing headers such as
`date`; preserving them remains driver/binding work.
