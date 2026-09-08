# Architecture Decision Log

This document captures **non-obvious** architecture and design decisions made over the
life of `azure-identity`, in chronological order, with citations to the pull
requests (and, where relevant, the review discussions) that introduced them.

It is **not** a changelog and **not** a substitute for the user docs
([`README.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md),
[`TOKEN_CACHING.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/TOKEN_CACHING.md),
[`TROUBLESHOOTING.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/TROUBLESHOOTING.md),
[`BREAKING_CHANGES.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/BREAKING_CHANGES.md)).
Those explain *what* the library does today and *how* to use it. This file explains *why*
the codebase looks the way it does — the constraints, debates, rejected alternatives, and
deliberate trade-offs that a new developer or agent would otherwise have to reconstruct from
years of git history. When you are tempted to "simplify" or "fix" something here that looks
odd, read the relevant entry first.

> Convention: PR numbers link to `https://github.com/Azure/azure-sdk-for-python/pull/<N>`.
> Dates are merge dates (year-month).

## How to maintain this file (read before editing)

This log is **strictly chronological** and must stay that way so future readers and agents can
trust the timeline:

- **Sections are single calendar years** (`## 2019`, `## 2020`, …). Do not create overlapping
  ranges like `2020–2021`.
- **Entries are ordered by the merge date of the PR that *introduced* the decision** (the
  earliest/primary PR cited in that entry), oldest first within each year.
- **When adding a new decision, append it** to the section for the year it was introduced —
  which is almost always the latest year, at the bottom. Only insert earlier if you are
  documenting an older decision that was previously missing.
- **An entry may cite later follow-up PRs** (fixes, reworks) inside its body; placement is still
  governed by the *introducing* PR's date, not the follow-ups.
- **Keep the Table of Contents in sync** when you add or rename a year section.
- Add the year subheading-style date line (e.g. `PR [#12345](https://github.com/Azure/azure-sdk-for-python/pull/12345) (2026-01)`) immediately under
  every `###` entry title so placement is auditable.

## Table of contents

- [2019 — Foundations](#2019--foundations)
- [2020 — Building on MSAL and managed-identity runtimes](#2020--building-on-msal-and-managed-identity-runtimes)
- [2021 — CAE, cache configuration, and per-request tenants](#2021--cae-cache-configuration-and-per-request-tenants)
- [2022 — Multi-tenant hardening](#2022--multi-tenant-hardening)
- [2023 — Chain semantics, managed-identity resilience, broker, workload identity](#2023--chain-semantics-managed-identity-resilience-broker-workload-identity)
- [2024 — Protocol evolution and MSAL managed identity](#2024--protocol-evolution-and-msal-managed-identity)
- [2025 — DAC configuration, deprecations, and broker in the default chain](#2025--dac-configuration-deprecations-and-broker-in-the-default-chain)
- [Recurring patterns worth internalizing](#recurring-patterns-worth-internalizing)

---

## 2019 — Foundations

### The credential contract: `TokenCredential` protocol + `get_token`
PRs [#5246](https://github.com/Azure/azure-sdk-for-python/pull/5246),
[#5547](https://github.com/Azure/azure-sdk-for-python/pull/5547),
[#5728](https://github.com/Azure/azure-sdk-for-python/pull/5728) (2019-05/06)

The package began as a prototype shipping only `Async/ClientSecretCredential` to unblock
other teams' development, before the rest of the credentials existed. Architecture-board
feedback (#5728) then settled several conventions that persist to this day:
- `SupportsGetToken` was renamed `TokenCredential` (the structural-typing protocol).
- `get_token` takes **scopes as variadic positional args** and the chain takes
  **credentials as variadic args** — chosen for cross-language API consistency, not Python
  ergonomics.
- `ManagedIdentityCredential` was made a **factory** that returns `MsiCredential` when MSI
  env vars are present and `ImdsCredential` otherwise. (This factory split was later
  reworked, but the "one credential, many runtime environments" idea originates here.)

### IMDS availability is detected with an HTTP probe, not a TCP connect
PR [#5908](https://github.com/Azure/azure-sdk-for-python/pull/5908) (2019-06)

Probing the metadata endpoint is the only way to know managed identity is available. A TCP
handshake probe would be "neater but would break the current tests," so an HTTP request with
a short timeout was chosen instead. This pragmatic choice persisted for years and underlies
the later probe-timeout tuning (#31745).

### App Service returns `expires_on` as a locale date string
PR [#5972](https://github.com/Azure/azure-sdk-for-python/pull/5972) (2019-06)

The App Service MSI endpoint returns `expires_on` as a US-locale string (e.g.
`"06/19/2019 23:42:01 +00:00"`) rather than epoch seconds. The string-vs-int parsing branch in
the managed identity code exists because of this undocumented endpoint quirk — don't remove it.

### Names match other Azure SDK languages, even when it costs a rename
PR [#5983](https://github.com/Azure/azure-sdk-for-python/pull/5983) (2019-06)

`TokenCredentialChain` was renamed `ChainedTokenCredential` purely for cross-language
consistency. Expect public type names here to be governed by cross-language alignment, not
Python convention.

### Async credentials live in `azure.identity.aio`, without name prefixes
PR [#6063](https://github.com/Azure/azure-sdk-for-python/pull/6063) (2019-06)

Early async classes were exposed as `AsyncEnvironmentCredential` etc. in the top-level
namespace. This was deliberately reversed: async credentials keep the **same class name** as
their sync counterparts and are instead segregated by module (`azure.identity.aio`). This is
why every credential has a sync/async pair with identical names — code that imports from
`aio` gets async, everything else is sync. The prototype author also noted that sharing code
between sync/async pairs was attempted but abandoned because "everything I tried [was] too
difficult to read" — hence the intentional duplication between sync and async
implementations.

### MSAL is the normative spec for token behavior; local shims are temporary debt
PR [#6176](https://github.com/Azure/azure-sdk-for-python/pull/6176) (2019-07)

Before MSAL 0.4.1 the SDK carried an in-repo workaround for an upstream MSAL bug. As soon as
MSAL fixed it, the pin was raised and the shim deleted. This sets a recurring pattern: the
team tracks MSAL upstream issues closely and treats its own workarounds as debt to be repaid
once MSAL ships a real fix. (See also #13215 and #11892 below.)

### MSAL HTTP routed through azure-core — first via monkeypatch, then the official API
PRs [#6358](https://github.com/Azure/azure-sdk-for-python/pull/6358) (2019-07),
[#11892](https://github.com/Azure/azure-sdk-for-python/pull/11892) (2020-06)

The goal was to make MSAL's HTTP calls flow through the `azure-core` pipeline so they share
logging, retries, proxy, and tracing config with the rest of the SDK. No extension point
existed in MSAL yet, so #6358 introduced an **internal** `ConfidentialClientCredential` that
monkeypatched MSAL's HTTP session — explicitly a "first step," with async deferred as
"significantly more complex." When MSAL 1.3.0 added an official custom-transport interface,
#11892 replaced the monkeypatch with the supported API and **deleted**
`ConfidentialClientCredential`. The sync-first, async-later cadence here set the rhythm for
the whole multi-year MSAL migration.

### `DefaultAzureCredential` swallows `ImportError` during construction; individual credentials do not
PR [#8294](https://github.com/Azure/azure-sdk-for-python/pull/8294) (2019-11)

`SharedTokenCacheCredential` could raise `ImportError` (msal-extensions dependency issues on
some platforms). Rather than make that credential resilient — which would mask real import
failures for direct users — only `DefaultAzureCredential` was taught to catch the error while
building its chain. This asymmetry is intentional: DAC degrades gracefully; standalone
credentials preserve their full exception contract.

---

## 2020 — Building on MSAL and managed-identity runtimes

### `DefaultAzureCredential` locks onto the first successful credential and never re-iterates
PR [#10349](https://github.com/Azure/azure-sdk-for-python/pull/10349) (2020-03)

DAC caches `_successful_credential` and on subsequent `get_token` calls uses **only** that
credential — it does not retry the chain, even if the locked credential later fails. A
reviewer pushed back directly:

> "if last successful credential fails, [the new behavior is to] return fail. Is this
> expected?"

The author confirmed it is by design:

> "The desired behavior of DefaultAzureCredential is not to iterate the chain again after a
> credential returns a token, because doing so only wastes cycles and introduces the
> possibility of an unexpected change of authentication method."

So DAC prefers **identity stability over availability**: a transient failure of the chosen
credential surfaces as an error rather than silently switching identities.

### Persistent token cache: encrypted by default, plaintext fallback is opt-in
PRs [#11319](https://github.com/Azure/azure-sdk-for-python/pull/11319) (2020-05),
[#11824](https://github.com/Azure/azure-sdk-for-python/pull/11824) (2020-06)

Cross-platform persistent caching (Linux via `libsecret`/`PyGObject`) defaults to
**encrypted only**; the unencrypted fallback is an explicit opt-in (`allow_unencrypted_cache`,
default `False`). Silently writing tokens in plaintext would be a security surprise. Cache
paths and schema names were intentionally copied from the Java SDK for cross-SDK cache
portability, and the encrypted cache deliberately clobbers a pre-existing unencrypted one to
prevent a silent security downgrade after upgrading. Service-principal caches use a separate
keychain schema (`MSALConfidentialCache`) from interactive user caches to keep the two
populations isolated.

### `AadClient` deliberately drops `msal.oauth2cli` (a non-public MSAL internal)
PRs [#11466](https://github.com/Azure/azure-sdk-for-python/pull/11466) (2020-05),
[#11718](https://github.com/Azure/azure-sdk-for-python/pull/11718),
[#11719](https://github.com/Azure/azure-sdk-for-python/pull/11719) (2020-06)

The custom `AadClient` was originally built on `msal.oauth2cli`, which the MSAL team did not
consider a public contract. To add caching features (and to stop depending on an unstable
internal), the SDK reimplemented `AadClient` from scratch and inlined its own JWT signing for
client-assertion/certificate auth — removing the last `msal.oauth2cli.JwtSigner` usage. This
is why `azure-identity` maintains its own AAD client code (`_internal/aad_client*.py`) instead
of delegating everything to MSAL: it is the "token acquisition separated from caching" layer
that MSAL did not cleanly expose at the time.

### `SharedTokenCacheCredential` becomes dual-mode (legacy vs. MSAL) — accepted as tech debt
PRs [#11637](https://github.com/Azure/azure-sdk-for-python/pull/11637) (2020-06),
[#13490](https://github.com/Azure/azure-sdk-for-python/pull/13490) (2020-09)

An optional `AuthenticationRecord` was added so the credential could initialize in a
"silent-only" mode and delegate entirely to MSAL — but only *when given a record*, to avoid
breaking the existing legacy code path. The author was candid about the resulting shape:

> "This implementation feels like bolting another class onto an existing one, but I don't see
> a better way to accomplish this while maintaining legacy behavior."

The async `authentication_record` arg was simultaneously removed because no async credential
produced an `AuthenticationRecord`. If this class looks like two credentials wearing one
coat, that is why.

### Credential constructors must not have observable side effects (lazy cache load)
PR [#12172](https://github.com/Azure/azure-sdk-for-python/pull/12172) (2020-06)

`SharedTokenCacheCredential` loaded the persistent cache in `__init__`/`supported()`. Because
`DefaultAzureCredential` *probes* that credential, every DAC user on Linux without
`PyGObject` saw an alarming, irrelevant `msal-extensions` error. The fix deferred cache
loading to the first `get_token()` call — **a UX fix, not a performance optimization**. The
general lesson encoded here: a constructor must stay silent because the credential may just be
probed and discarded inside a chain.

### `AZURE_CLIENT_ID` does double duty (service principal **and** user-assigned MI)
PRs [#12689](https://github.com/Azure/azure-sdk-for-python/pull/12689) (2020-07),
[#13218](https://github.com/Azure/azure-sdk-for-python/pull/13218) (2020-08)

`AZURE_CLIENT_ID` selects a service principal for `EnvironmentCredential` and, inside DAC, was
additionally wired to select a **user-assigned managed identity**. This reuse is safe only
because at most one credential consumes it at a time. #13218 added an explicit
`managed_identity_client_id` kwarg; note the subtle escape hatch that passing `None`
explicitly overrides the env var and forces *system-assigned* identity.

### One credential class per managed-identity runtime, not one class with branches
PR [#13053](https://github.com/Azure/azure-sdk-for-python/pull/13053) (2020-08)

When App Service shipped a second API version (different header: `secret` vs
`X-IDENTITY-HEADER`), the team added a dedicated `AppServiceCredential` rather than branching
inside the existing code, reasoning it "will be easier to manage the growing list of
supported platforms if each has its own credential class." This codified the
one-class-per-environment pattern that App Service, Cloud Shell, Service Fabric, Arc, and
Azure ML all follow.

### Service principal credentials adopt `msal.ConfidentialClientApplication`
PR [#13215](https://github.com/Azure/azure-sdk-for-python/pull/13215) (2020-08)

Once the official transport API existed, `ClientSecretCredential` and `CertificateCredential`
moved onto `msal.ConfidentialClientApplication`. Password-protected certificates were not yet
formally supported by MSAL, so `CertificateCredential` temporarily relied on an MSAL
**implementation detail** to pass the password — a deliberate, time-boxed compromise to ship
the integration before MSAL's formal support landed.

### Service Fabric disables TLS verification — Python can't validate the cluster cert
PR [#14025](https://github.com/Azure/azure-sdk-for-python/pull/14025) (2020-10)

Service Fabric uses self-signed cluster certs and expects thumbprint validation against
`IDENTITY_SERVER_THUMBPRINT`. That validation isn't reachable through Python's standard
`requests`/`urllib3` stack, so `service_fabric.py` sets `connection_verify=False` (with a
`# pylint: disable=do-not-hardcode-connection-verify`). This is a **known, documented
security trade-off**, not an oversight — don't "fix" it without solving thumbprint
validation first.

### Azure Arc uses a 401-challenge / file-read / Basic-auth replay; no user-assigned identity
PR [#15020](https://github.com/Azure/azure-sdk-for-python/pull/15020) (2020-11)

Arc authentication is a two-step dance: the first request returns `401` with a
`WWW-Authenticate: Basic realm=<path>` header; the SDK reads a secret from that file path and
replays the request with `Authorization: Basic <key>`. Later hardening restricts the file to
platform-specific directories and enforces a size limit to prevent path traversal. Arc does
**not** support user-assigned identities, so passing a `client_id` raises immediately rather
than silently ignoring it.

---

## 2021 — CAE, cache configuration, and per-request tenants

### CAE arrived "always-on (CP1)" for user credentials only — the start of a multi-year saga
PRs [#16323](https://github.com/Azure/azure-sdk-for-python/pull/16323) (2021-02),
[#17136](https://github.com/Azure/azure-sdk-for-python/pull/17136) (2021-03),
[#18148](https://github.com/Azure/azure-sdk-for-python/pull/18148) (2021-05)

Continuous Access Evaluation (CAE) support began by configuring MSAL with client capability
`CP1` **always on**, but only for *user* credentials (interactive, device code, shared cache),
not service principals. #17136 surfaced the CAE `claims` challenge on
`AuthenticationRequiredError` so headless apps could re-authenticate with the right claims.
When always-on CP1 broke some customers, #18148 added an **emergency escape hatch** env var
`AZURE_IDENTITY_DISABLE_CP1` (deliberately a "compatibility switch," signalling it was meant to
be temporary). This always-on, user-only asymmetry is the root cause of the later rework.

### `TokenCachePersistenceOptions` replaced flat kwargs to make a cache `name` possible
PR [#16326](https://github.com/Azure/azure-sdk-for-python/pull/16326) (2021-03)

The earlier flat booleans (`enable_persistent_cache`, `allow_unencrypted_cache`) had no room
for a **cache name**, so apps couldn't isolate their cache from others sharing the same OS
keychain entry. Bundling the options into a `TokenCachePersistenceOptions` class was the only
clean way to add `name`. The unencrypted-storage flag was also renamed
(`allow_unencrypted_cache` → `allow_unencrypted_storage`) to emphasize the storage medium over
the "cache" noun.

### `ManagedIdentityClient` extracted as a shared internal HTTP client
PR [#18120](https://github.com/Azure/azure-sdk-for-python/pull/18120) (2021-04)

`ImdsCredential` moved to its own module and a shared `ManagedIdentityClient` was introduced to
de-duplicate the IMDS and MSI HTTP paths. The large diff is mostly a file move; the intent was
to make the managed-identity code easier to understand and extend.

### Per-request `tenant_id`, and the opt-in → opt-out flip from the Architecture Board
PRs [#19602](https://github.com/Azure/azure-sdk-for-python/pull/19602) (2021-07),
[#20940](https://github.com/Azure/azure-sdk-for-python/pull/20940) (2021-10)

Services issue challenges naming the tenant a token must come from, so `get_token` needed a
**per-request** `tenant_id` (a single configured tenant can't work across a DAC chain whose
credentials target different tenants). The initial design required opting in via
`allow_multitenant_authentication=True`; the Architecture Board concluded multi-tenant should
be the **default**, with an env-var escape hatch instead of a constructor flag. #20940 removed
the opt-in kwarg and added `AZURE_IDENTITY_DISABLE_MULTITENANTAUTH` (plus a legacy
`AZURE_IDENTITY_ENABLE_LEGACY_TENANT_SELECTION`).

---

## 2022 — Multi-tenant hardening

### `DefaultAzureCredential(tenant_id=...)` raises `TypeError` on purpose
PR [#23322](https://github.com/Azure/azure-sdk-for-python/pull/23322) (2022-03)

Users expected a constructor `tenant_id` to flow to every sub-credential, but DAC's
credentials have incompatible tenant semantics (MI ignores tenant; `ClientSecretCredential`
has a fixed one). A single constructor `tenant_id` would behave inconsistently, so DAC
explicitly **rejects** it. The supported mechanism is per-request `tenant_id` in `get_token`.

### `additionally_allowed_tenants` allowlist — defending against the confused-deputy risk
PR [#26133](https://github.com/Azure/azure-sdk-for-python/pull/26133) (2022-09)

The main intention was to constrain multi-tenant authentication by default: if a credential is
configured for one tenant when constructed, then token requests for another tenant raise an
error unless explicitly allowed. This also defends against a confused-deputy risk — once
per-request `tenant_id` was honored unconditionally, a malicious/compromised service could
return a challenge steering token acquisition to an attacker-controlled tenant. The fix
(`_internal/utils.py: resolve_tenant`) refuses any tenant not in `additionally_allowed_tenants`
(or `*`). A carve-out: credentials whose `default_tenant` is `"organizations"` (inherently
multi-tenant dev tools like `AzureCliCredential`) allow any tenant when no allowlist is set,
so developers using the CLI across subscriptions aren't broken. This is a **breaking
behavioral change** documented in [`BREAKING_CHANGES.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/BREAKING_CHANGES.md) (1.11.0); the
rationale is at <https://aka.ms/azsdk/blog/multi-tenant-guidance>.

---

## 2023 — Chain semantics, managed-identity resilience, broker, workload identity

### `WorkloadIdentityCredential` can crash DAC construction
PRs [#28536](https://github.com/Azure/azure-sdk-for-python/pull/28536) (2023-02),
[#29728](https://github.com/Azure/azure-sdk-for-python/pull/29728) (2023-04)

`WorkloadIdentityCredential.__init__` raises `ValueError` if its required env vars
(`AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_FEDERATED_TOKEN_FILE`) are missing — which would
crash DAC on any non-AKS machine. DAC wraps construction in a `try/except ValueError` so the
chain can continue. (The `FailedDACCredential` placeholder that formalized this handling came
later — see the 2025 section.)

### CAE rework: per-request `enable_cae`, and the dual MSAL app / dual cache architecture
PRs [#29037](https://github.com/Azure/azure-sdk-for-python/pull/29037) (2023-03),
[#29773](https://github.com/Azure/azure-sdk-for-python/pull/29773) (2023-04),
[#30777](https://github.com/Azure/azure-sdk-for-python/pull/30777) (2023-07)

Extending always-on CP1 to service principals (#29037) was immediately disabled for the stable
release (#29773) because the always-on model couldn't selectively enable CAE only for resources
that support it. The final design (#30777) makes CAE a **per-request** flag (`enable_cae=True`)
so one credential instance can serve both CAE and non-CAE resources. The non-obvious
consequence: because MSAL token caches are scope-agnostic and would otherwise overwrite a
CAE token with a non-CAE one (or vice versa), each credential now keeps **two** MSAL
applications and **two** caches (`_client_applications`/`_cae_client_applications`,
`_cache`/`_cae_cache`; persistent caches get `.nocae`/`.cae` suffixes). `AZURE_IDENTITY_DISABLE_CP1`
was removed since always-on no longer exists. Routing to the right cache by `is_cae` is easy to
get wrong — see the later bug fix #42145.

### Chain flow is signaled by exception *type*, not an `is_chained` flag
PRs [#31296](https://github.com/Azure/azure-sdk-for-python/pull/31296),
[#31328](https://github.com/Azure/azure-sdk-for-python/pull/31328) (2023-07)

Credentials used to inspect a public `is_chained` property to alter behavior. That property was
made internal and its usages removed in favor of a clean contract: raising
`CredentialUnavailableError` (a subclass of `ClientAuthenticationError`) means "I couldn't even
try" → the chain **continues**; any other exception means "I tried and failed" → the chain
**stops**. This is why `CredentialUnavailableError` is the universal "not applicable here"
signal throughout the codebase, and why credentials inside DAC re-classify
`ClientAuthenticationError` into `CredentialUnavailableError` (via the `within_dac` /
`within_credential_chain` context vars) to avoid terminating the chain.

### Credentials' `get_token` signatures were widened to satisfy the `TokenCredential` protocol
PR [#31047](https://github.com/Azure/azure-sdk-for-python/pull/31047) (2023-08)

Many credentials had narrower `get_token` signatures than the `azure-core` `TokenCredential`
protocol, which broke structural subtyping under mypy/pyright. All implementations were aligned
to `get_token(*scopes, **kwargs)` (documenting which kwargs may be ignored). This was
prerequisite groundwork for the `get_token_info` protocol.

### IMDS probe redesign: probe only inside chains, 0.3s → 1s, never permanently disable
PR [#31745](https://github.com/Azure/azure-sdk-for-python/pull/31745) (2023-09)

Transient network failures used to permanently break a `ManagedIdentityCredential` instance.
Three coupled changes fixed this: (1) the probe fires **only** when running inside a chain
(`within_credential_chain` is set) — standalone `ManagedIdentityCredential` skips the probe and
goes straight to full retry logic; (2) the probe timeout was raised 0.3s → 1s to match .NET and
reduce false negatives (accepting a slightly longer DAC fallback delay); (3) an IMDS failure no
longer sets `_endpoint_available = False`, so the same instance can be retried.

### Docker Desktop's 403 "unreachable" must be treated as *unavailable*, not *error*
PR [#31824](https://github.com/Azure/azure-sdk-for-python/pull/31824) (2023-09)

Docker Desktop proxies all traffic and answers an unreachable IMDS with HTTP 403 containing the
word `"unreachable"` instead of timing out. That special case is detected and mapped to
`CredentialUnavailableError` (chain-transparent) instead of `ClientAuthenticationError`
(chain-terminating).

### IMDS 410 means "retry," and retry timing later needed its own policy
PRs [#32200](https://github.com/Azure/azure-sdk-for-python/pull/32200) (2023-10),
[#35070](https://github.com/Azure/azure-sdk-for-python/pull/35070) (2024-04),
[#42330](https://github.com/Azure/azure-sdk-for-python/pull/42330) (2025-08)

Per Azure IMDS docs, HTTP 410 is *temporary* and must be retried (#32200 added it to the
retryable set). #35070 then cut the global backoff factor 2 → 0.8 because the old setting
produced ~62s of cumulative delay on transient 404/5xx — far too slow for production — and made
the factor user-configurable. But Azure later required retrying 410 for **≥70s**, which
contradicts a fast global backoff. The resolution (#42330) is a custom `ImdsRetryPolicy` that
switches backoff **per status code**: ~2.5 factor (≈75s total) for 410, 0.8 for everything
else.

### Broker support: added to core, then pulled out into `azure-identity-broker`
PRs [#32369](https://github.com/Azure/azure-sdk-for-python/pull/32369) (2023-10),
[#32442](https://github.com/Azure/azure-sdk-for-python/pull/32442) (2023-10)

WAM (Windows Web Account Manager) brokered auth was briefly added to core `azure-identity`,
then removed one beta cycle later: WAM needs Windows-native binaries (`pywin32`,
platform-specific `msal` extras), but core `azure-identity` must stay pure-Python and
cross-platform. The functionality moved to the opt-in `azure-identity-broker` package (same
"heavy/platform-specific auth lives in a separate package" precedent as managed-identity
extensions). In that package, `allow_broker` defaults to `True` because installing the package
*is* the opt-in.

---

## 2024 — Protocol evolution and MSAL managed identity

### All managed-identity credentials migrate onto `msal.ManagedIdentityClient`
PR [#36225](https://github.com/Azure/azure-sdk-for-python/pull/36225) (2024-07)

A new `MsalManagedIdentityClient` base wraps `msal.ManagedIdentityClient` (passing an
azure-core-backed `http_client`), and every platform credential (App Service, Arc, Azure ML,
Service Fabric, IMDS) inherits from it. The older custom `ManagedIdentityClient` survives as a
thin HTTP layer used for the IMDS **probe** that precedes full MSAL acquisition. Because
`msal.ManagedIdentityClient` is not picklable, `__getstate__`/`__setstate__` rebuild it on
unpickle (same reason `SharedTokenCacheCredential` got pickling support in #36404).

### `get_token_info` / `AccessTokenInfo` / `TokenRequestOptions`: an options bag for extensibility
PR [#36882](https://github.com/Azure/azure-sdk-for-python/pull/36882) (2024-09)

`get_token` returns a 2-tuple `AccessToken(token, expires_on)`; adding fields like `refresh_on`
(proactive refresh) or `token_type` (PoP vs bearer) would be a breaking change, and threading
new request params (e.g. `enable_cae`) through every credential's kwargs is fragile. The
solution adds a parallel `get_token_info(*scopes, options: TokenRequestOptions) ->
AccessTokenInfo`, where `TokenRequestOptions` is a `TypedDict` options bag and `AccessTokenInfo`
is an extensible dataclass. Crucially, **`get_token` is kept for backward compatibility** and
both methods funnel into the same `GetTokenMixin._get_token_base`, so cache/retry logic is
shared and `get_token` simply drops the extra `AccessTokenInfo` fields. This is why the
codebase has two parallel token methods that look redundant but aren't.

> Related: `GetTokenMixin._get_token_base` implements **proactive refresh** — a token may be in
> `RECOMMENDED` (refresh if possible, ignore failures) or `REQUIRED` (must refresh) state via
> `refresh_on`. It also logs at DEBUG inside a chain and INFO/WARNING standalone, to keep DAC
> probing quiet. See `_internal/get_token_mixin.py`.

---

## 2025 — DAC configuration, deprecations, and broker in the default chain

### Deprecations driven by external lifecycle, not internal cleanup
PRs [#39785](https://github.com/Azure/azure-sdk-for-python/pull/39785) (2025-03),
[#40613](https://github.com/Azure/azure-sdk-for-python/pull/40613) (2025-05),
[#41822](https://github.com/Azure/azure-sdk-for-python/pull/41822) (2025-07)

- **`UsernamePasswordCredential`** was deprecated because it uses the ROPC OAuth flow, which
  cannot satisfy the mandatory MFA that Entra is rolling out tenant-wide
  (<https://aka.ms/mfaforazure>). The recommended replacements are interactive/device-code
  credentials, which support MFA.
- **`VisualStudioCodeCredential`** was deprecated (#40613) because the VS Code *Azure Account*
  extension it read tokens from was discontinued, then **re-implemented** (#41822) on top of the
  *Azure Resources* extension via the broker. The new version reads
  `~/.azure/ms-azuretools.vscode-azureresourcegroups/authRecord.json`, requires its `clientId`
  to match `AZURE_VSCODE_CLIENT_ID` exactly (security check), and uses a silent-only broker
  (`use_default_broker_account=True, disable_interactive_fallback=True`). It is currently
  Windows/WSL only and requires `azure-identity-broker`.

### Brokered auth in the DAC chain — last, silent-only, conditional
PR [#40335](https://github.com/Azure/azure-sdk-for-python/pull/40335) (2025-07)

A `BrokerCredential` was added to the **end** of the DAC chain (after all developer
credentials) so it covers the "already signed into Windows" case without overriding explicit
dev credentials. It is **silent-only** (`use_default_broker_account=True`,
`disable_interactive_fallback=True`) so it never pops a browser in server/CI contexts, and it
raises `CredentialUnavailableError` if `azure-identity-broker` isn't installed or the platform
isn't Windows/WSL — keeping the chain transparent.

### `AZURE_TOKEN_CREDENTIALS` can select a single credential; explicit args win
PRs [#41709](https://github.com/Azure/azure-sdk-for-python/pull/41709) (2025-07),
[#42660](https://github.com/Azure/azure-sdk-for-python/pull/42660) (2025-08),
[#43080](https://github.com/Azure/azure-sdk-for-python/pull/43080) (2025-10)

`AZURE_TOKEN_CREDENTIALS` was extended from `prod`/`dev` groups to also name a single credential
(e.g. `WorkloadIdentityCredential`). Precedence is "explicit wins over implicit": user
`exclude_*` kwargs override the env var, and a contradiction (selecting a credential you also
excluded) raises `ValueError` rather than silently producing an empty chain. #42660 added
`require_envvar=True` so ops teams can **fail fast** if the env var is absent (guaranteeing the
chain is env-controlled in production). #43080 skips the IMDS probe entirely when
`AZURE_TOKEN_CREDENTIALS=ManagedIdentityCredential`, since the user has explicitly chosen MI —
matching standalone `ManagedIdentityCredential` retry behavior.

### CAE caches finally wired up for the last two credentials
PR [#42145](https://github.com/Azure/azure-sdk-for-python/pull/42145) (2025-08)

`AuthorizationCodeCredential` and async `OnBehalfOfCredential` had the dual-cache fields but
their `_get_app`/`_get_cache` logic didn't route to `_cae_cache` when `enable_cae=True`, so CAE
tokens silently landed in the non-CAE cache and never hit on lookup. A pure follow-through bug
from the #30777 dual-cache design.

### `FailedDACCredential` placeholder for credentials that fail at construction
PR [#42346](https://github.com/Azure/azure-sdk-for-python/pull/42346) (2025-08)

When a credential (e.g. `WorkloadIdentityCredential`) raises during construction inside DAC,
DAC substitutes a `FailedDACCredential` placeholder that raises `CredentialUnavailableError` on
`get_token` (chain-continue) while still surfacing the init failure in the final aggregated
error message. This placeholder pattern exists specifically because some credentials fail *by
design* during construction.

### `WorkloadIdentityCredential` AKS "binding mode" (FIC-per-MI ceiling workaround)
PR [#43287](https://github.com/Azure/azure-sdk-for-python/pull/43287) (2025-11)

Entra limits Federated Identity Credentials (FICs) per managed identity, which large AKS
clusters can exhaust. Binding mode routes the FIC exchange through an AKS-side proxy
(`enable_azure_proxy=True`, configured via `AZURE_KUBERNETES_TOKEN_PROXY` and SNI/CA env vars)
so a single set of FICs serves many pods. The proxy path is intentionally skipped when running
inside a `ChainedTokenCredential`.

---

## Recurring patterns worth internalizing

- **MSAL is the source of truth (for most sync credentials).** Local workarounds for MSAL gaps
  are deliberate, time-boxed debt; expect them to be deleted once MSAL ships a real fix (#6176,
  #11892, #13215, #36225). The custom `AadClient` exists only because MSAL didn't cleanly expose
  acquisition-without-MSAL-caching (#11466). Async credentials don't use MSAL underneath (MSAL
  has no async API) — they only use MSAL's token cache.
- **`CredentialUnavailableError` vs other errors is the chain contract.** Unavailable →
  continue; anything else → stop. Credentials inside DAC re-classify errors to cooperate
  (#31296, #31824, `within_dac`/`within_credential_chain`).
- **Constructors must be side-effect-free and cheap**, because DAC probes and discards
  credentials (#12172, #8294, #31745, `FailedDACCredential`).
- **DAC favors identity stability over availability** — it locks onto one credential and won't
  silently switch (#10349).
- **One class per managed-identity runtime**, each with its own quirks (App Service date
  strings, Service Fabric TLS, Arc challenge flow) (#13053, #5972, #14025, #15020).
- **Two of everything for CAE.** Per-request `enable_cae` forces dual MSAL apps and dual caches;
  routing by `is_cae` is a common source of bugs (#30777, #42145).
- **Security decisions are explicit and opt-in/allowlist-based**: encrypted cache by default
  (#11319), tenant allowlist (#26133), exact `clientId` match for VS Code (#41822).
- **Many "design" changes are actually reactions to external lifecycles** — Entra MFA, VS Code
  extension retirement, Docker Desktop proxy behavior, Azure IMDS retry guidance — not internal
  refactors (#39785, #40613, #31824, #42330).
