# Architecture Reference for azure-identity

## Credential Taxonomy

### By OAuth Application Type

This is the OAuth/MSAL distinction that drives most of the credential design.

**Public client application** — cannot keep a secret; authenticates a _user_ interactively. Backed by `msal.PublicClientApplication`:
- `InteractiveBrowserCredential`, `DeviceCodeCredential`, `UsernamePasswordCredential`
- `AuthorizationCodeCredential`, `SharedTokenCacheCredential`
- `VisualStudioCodeCredential` (delegates to broker)
- `InteractiveBrowserBrokerCredential` (broker package)

**Confidential client application** — runs on a server, holds a secret/certificate/assertion. Backed by `msal.ConfidentialClientApplication`:
- `ClientSecretCredential`, `CertificateCredential`, `ClientAssertionCredential`
- `OnBehalfOfCredential`
- `WorkloadIdentityCredential` (built on `ClientAssertionCredential`)
- `AzurePipelinesCredential` (composes `ClientAssertionCredential`)
- `EnvironmentCredential` (resolves to one of the above)

**Neither (managed identity)** — authenticates the compute resource via local IMDS/metadata endpoint:
- `ManagedIdentityCredential` and backends: `ImdsCredential`, `AppServiceCredential`, `AzureMLCredential`, `AzureArcCredential`, `ServiceFabricCredential`, `CloudShellCredential`

**Subprocess-based** — shells out to a developer tool that has already authenticated (no MSAL):
- `AzureCliCredential`, `AzureDeveloperCliCredential`, `AzurePowerShellCredential`

### By Production vs Developer (DAC Classification)

Used by `DefaultAzureCredential` and the `AZURE_TOKEN_CREDENTIALS` env var:

| Category | Credentials |
|----------|------------|
| **Production** | `EnvironmentCredential`, `WorkloadIdentityCredential`, `ManagedIdentityCredential` |
| **Developer** | `SharedTokenCacheCredential`, `VisualStudioCodeCredential`, `AzureCliCredential`, `AzurePowerShellCredential`, `AzureDeveloperCliCredential`, `BrokerCredential` |
| **Other** (explicit use only) | `ClientSecretCredential`, `CertificateCredential`, `ClientAssertionCredential`, `OnBehalfOfCredential`, `AuthorizationCodeCredential`, `DeviceCodeCredential`, `UsernamePasswordCredential`, `AzurePipelinesCredential`, `InteractiveBrowserCredential` (DAC-excluded by default) |

## MSAL Integration — Three Tiers

Understanding the three tiers of MSAL usage is critical for making changes:

### Tier 1: Full MSAL client app (sync only)

These instantiate `msal.PublicClientApplication`, `msal.ConfidentialClientApplication`, or `msal.ManagedIdentityClient`:
- `ClientSecretCredential`, `CertificateCredential` → `ConfidentialClientApplication`
- `OnBehalfOfCredential` → `ConfidentialClientApplication.acquire_token_on_behalf_of`
- `InteractiveBrowserCredential`, `DeviceCodeCredential`, `UsernamePasswordCredential` → `PublicClientApplication`
- `ManagedIdentityCredential` (most backends) → `MsalManagedIdentityClient` → `msal.ManagedIdentityClient`
  - **Exception:** `CloudShellCredential` does NOT use `msal.ManagedIdentityClient` — uses in-house `ManagedIdentityClient`

### Tier 2: MSAL TokenCache only

The in-house `AadClient` performs raw OAuth HTTP requests but stores results in `msal.TokenCache` for cache compatibility:
- `AuthorizationCodeCredential`, `ClientAssertionCredential`, `WorkloadIdentityCredential`, `AzurePipelinesCredential`
- `SharedTokenCacheCredential` — reads MSAL's persisted cache, redeems refresh tokens via `AadClient`

### Tier 3: No MSAL at all

Subprocess-based credentials that parse stdout JSON:
- `AzureCliCredential` (`az account get-access-token`)
- `AzureDeveloperCliCredential` (`azd auth token`)
- `AzurePowerShellCredential` (`Get-AzAccessToken` via `pwsh`)

### Sync vs Async — The Big Rule

**MSAL is a sync-only library.** No async credential ever instantiates a MSAL client application. Async credentials inherit from sync base classes that import MSAL, but token acquisition on the async side is implemented in-house:
- Async `AadClient` performs raw OAuth HTTP requests via azure-core's async pipeline
- Async managed-identity sources hit IMDS/app-host endpoints directly
- MSAL's `TokenCache` data structure IS reused for cache compatibility

So every Tier 1 sync credential drops to Tier 2 in its async counterpart.

## Managed Identity Backends

`ManagedIdentityCredential` sniffs the environment and picks ONE backend:

| Environment | Detection | Uses MSAL MI Client? |
|------------|-----------|---------------------|
| App Service | `IDENTITY_ENDPOINT` + `IDENTITY_HEADER` | Yes |
| Service Fabric | `IDENTITY_ENDPOINT` + `IDENTITY_SERVER_THUMBPRINT` | Yes |
| Azure Arc | `IDENTITY_ENDPOINT` + `IMDS_ENDPOINT` | Yes |
| Azure ML | `MSI_ENDPOINT` + `MSI_SECRET` | Yes |
| Cloud Shell | `MSI_ENDPOINT` (no secret) | **No** — uses in-house client |
| Workload Identity | `AZURE_FEDERATED_TOKEN_FILE` + `AZURE_TENANT_ID` + `AZURE_CLIENT_ID` | Yes |
| IMDS (fallback) | None of the above | Yes |

## DefaultAzureCredential Chain

### Sync chain (10 entries)

1. `EnvironmentCredential`
2. `WorkloadIdentityCredential`
3. `ManagedIdentityCredential`
4. `SharedTokenCacheCredential`
5. `VisualStudioCodeCredential`
6. `AzureCliCredential`
7. `AzurePowerShellCredential`
8. `AzureDeveloperCliCredential`
9. `InteractiveBrowserCredential` (**excluded by default** — `exclude_interactive_browser_credential=True`)
10. `BrokerCredential` (no-op unless `azure-identity-broker` installed + Windows/WSL)

### Async chain (8 entries)

Same as sync entries 1–8. **No** `InteractiveBrowserCredential` or `BrokerCredential`.

### `FailedDACCredential` pattern

If a credential fails to **initialize** (not at token time), it's replaced with `FailedDACCredential` (sync) or `AsyncFailedDACCredential` (async). This lets the chain continue and reports the init error only if ALL credentials fail.

### `AZURE_TOKEN_CREDENTIALS` env var

Narrows DAC before `exclude_*` flags:
- `prod` → keeps only Environment, WorkloadIdentity, ManagedIdentity
- `dev` → keeps developer credentials + broker
- Specific credential name → selects one (but `SharedTokenCacheCredential` and `BrokerCredential` have no `env_name` and can't be selected this way)
- `require_envvar=True` + unset var → `ValueError`

### `within_dac` ContextVar

Set while DAC iterates its chain. Child credentials check this to:
- Suppress noisy error logging (use DEBUG instead of WARNING)
- Exit fast on `CredentialUnavailableError`

## Authentication Flows

| Flow | Credentials |
|------|------------|
| Client credentials — secret | `ClientSecretCredential`, `EnvironmentCredential` (with `AZURE_CLIENT_SECRET`) |
| Client credentials — certificate | `CertificateCredential`, `EnvironmentCredential` (with `AZURE_CLIENT_CERTIFICATE_PATH`) |
| Client credentials — federated assertion | `ClientAssertionCredential` |
| Workload identity federation | `WorkloadIdentityCredential` |
| Azure Pipelines OIDC | `AzurePipelinesCredential` |
| On-Behalf-Of | `OnBehalfOfCredential` |
| IMDS / app-host metadata | `ManagedIdentityCredential` (auto-detects source) |
| Authorization code + PKCE | `InteractiveBrowserCredential`, `InteractiveBrowserBrokerCredential` |
| Authorization code redemption | `AuthorizationCodeCredential` |
| Device code | `DeviceCodeCredential` |
| ROPC (discouraged) | `UsernamePasswordCredential` |
| Silent / refresh-token from cache | `SharedTokenCacheCredential`, silent step in interactive credentials |
| Native broker (WAM) | `InteractiveBrowserBrokerCredential`, `VisualStudioCodeCredential` |
| Subprocess delegation | `AzureCliCredential`, `AzurePowerShellCredential`, `AzureDeveloperCliCredential` |

## Cross-Cutting Behaviors

- **CAE**: Credentials that proxy MSAL pass `enable_cae` through. `AadClient` keeps a separate `cae_cache`. CAE and non-CAE tokens must not collide.
- **Multi-tenant**: Per-call `tenant_id` overrides constructor tenant, subject to `additionally_allowed_tenants` allow-list.
- **Token caching**: In-memory by default. Persistent via `TokenCachePersistenceOptions` → `msal-extensions` (DPAPI/Keychain/libsecret, plaintext fallback only if explicitly allowed).
- **Authorities/clouds**: Controlled by `authority=` or `AZURE_AUTHORITY_HOST`. `AzureAuthorityHosts` enumerates Public, US Gov, China.
- **Logging**: Every credential logs through `azure.identity` logger. `TROUBLESHOOTING.md` is the canonical troubleshooting reference.
