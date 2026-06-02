---
name: azure-identity
description: 'Domain knowledge for azure-identity. Covers architecture, credential chain, MSAL integration, sync/async split, managed identity, token APIs, and common pitfalls. WHEN: modify azure-identity; fix azure-identity bug; add azure-identity credential; azure-identity feature; change DefaultAzureCredential; update managed identity.'
---

# azure-identity — Package Skill

`azure-identity` is **entirely hand-authored** — there is no TypeSpec, no `_generated/` directory, no `_patch.py` files, and no code generation step. Every file is owned and maintained directly.

## Architecture

```
azure/identity/
├── __init__.py                  # Public API re-exports; __all__ is the contract
├── _version.py                  # VERSION string
├── _constants.py                # EnvironmentVariables, AzureAuthorityHosts, KnownAuthorities
├── _enums.py                    # RegionalAuthority, TokenRefreshStatus
├── _auth_record.py              # AuthenticationRecord (serializable identity snapshot)
├── _bearer_token_provider.py    # get_bearer_token_provider() helper (sync + async variants)
├── _persistent_cache.py         # TokenCachePersistenceOptions, platform-specific cache loading
├── _exceptions.py               # CredentialUnavailableError, AuthenticationRequiredError
├── _credentials/                # Sync credential implementations (one file per credential)
│   ├── default.py               # DefaultAzureCredential — the chain
│   ├── chained.py               # ChainedTokenCredential — base chain logic
│   ├── managed_identity.py      # ManagedIdentityCredential — env-sniffing dispatcher
│   ├── environment.py           # EnvironmentCredential — reads env vars
│   ├── broker.py                # BrokerCredential (WAM, Windows/WSL only)
│   └── ...                      # certificate, client_secret, browser, device_code, etc.
├── _internal/                   # Shared plumbing (NOT public API)
│   ├── get_token_mixin.py       # GetTokenMixin — unified get_token/get_token_info flow
│   ├── msal_credentials.py      # MSAL app wrapper (per-tenant, CAE/non-CAE separation)
│   ├── msal_client.py           # Low-level MSAL HTTP adapter
│   ├── aad_client.py / aad_client_base.py  # In-house OAuth client (raw HTTP, uses msal.TokenCache)
│   ├── managed_identity_client.py          # In-house MI client (Cloud Shell uses this)
│   ├── msal_managed_identity_client.py     # MSAL-based MI client (all other MI sources)
│   ├── client_credential_base.py           # Base for confidential client credentials
│   ├── interactive.py           # Base for interactive credentials
│   ├── decorators.py            # Logging decorators (log_get_token, log_get_token_async)
│   └── utils.py                 # Authority normalization, within_dac ContextVar, DAC helpers
└── aio/                         # Async mirror (see Async Parity section)
    ├── __init__.py              # Async public API re-exports (fewer than sync)
    ├── _credentials/            # Async credential implementations
    └── _internal/               # Async plumbing — raw OAuth via azure-core async pipeline
```

**Extension package:** `azure-identity-broker` provides `InteractiveBrowserBrokerCredential` (sync only) for native broker auth (WAM/Company Portal). `VisualStudioCodeCredential` requires this package and only works on Windows/WSL.

## Token APIs

Two methods exist on every credential — understanding the distinction is critical:

- **`get_token()`** — **deprecated**. Returns `AccessToken(token, expires_on)`. Keyword set frozen at `claims` / `tenant_id` / `enable_cae`. Cannot do PoP tokens, `refresh_on` hints, or non-Bearer `token_type`.
- **`get_token_info()`** — **preferred going forward**. Returns `AccessTokenInfo(token, expires_on, refresh_on, token_type)`. Required for CAE, Proof-of-Possession (PoP/mTLS/SHR), refresh-on hints. A credential signals support via `SupportsTokenInfo`.

Both are implemented in `GetTokenMixin` (`_internal/get_token_mixin.py`). `get_token` internally builds `TokenRequestOptions` and delegates to `_get_token_base`. New features go on `get_token_info` / `TokenRequestOptions` only.

## Common Pitfalls

1. **Three sync-only credentials.** `DeviceCodeCredential`, `InteractiveBrowserCredential`, and `UsernamePasswordCredential` are intentionally sync-only — they prompt a human and there is no benefit to an async surface. They are NOT in `aio/__init__.py` or the async DAC chain. Do not add async versions.

2. **`__all__` in both `__init__.py` files.** New public symbols must be added to BOTH `azure/identity/__init__.py` AND `azure/identity/aio/__init__.py` (if async-applicable). Missing entries silently hide the class.

3. **MSAL is sync-only.** No async credential ever instantiates `msal.PublicClientApplication`, `msal.ConfidentialClientApplication`, or `msal.ManagedIdentityClient`. Async token acquisition uses the in-house `AadClient` (raw OAuth HTTP via azure-core async pipeline). MSAL's `TokenCache` data structure IS reused by async for cache compatibility. See `references/architecture.md` for the three tiers of MSAL usage.

4. **DAC chain order matters and differs sync vs async.** Sync DAC has 10 entries (including `InteractiveBrowserCredential` excluded by default, and `BrokerCredential`). Async DAC has only 8 (omits those two). New credentials must be inserted at the correct position in BOTH `_credentials/default.py` and `aio/_credentials/default.py`, with matching `exclude_*` kwargs.

5. **`within_dac` ContextVar.** When DAC is iterating its chain, `within_dac` is set so child credentials suppress noisy errors and exit fast on `CredentialUnavailableError`. Log level depends on this context — don't bypass it.

6. **Multi-tenant: `additionally_allowed_tenants`.** Credentials reject cross-tenant token requests unless the target tenant is in `additionally_allowed_tenants` or `*` is specified. Forgetting this causes `ClientAuthenticationError`.

7. **Managed identity has 7 backends + an exception.** `ManagedIdentityCredential` auto-detects App Service, IMDS, Azure Arc, Service Fabric, Cloud Shell, Azure ML, Workload Identity. Most use `MsalManagedIdentityClient` (wraps `msal.ManagedIdentityClient`), but **`CloudShellCredential` is the exception** — it uses the in-house `ManagedIdentityClient` and talks to the Cloud Shell MSI endpoint directly.

8. **Don't hardcode authority URLs.** Use `AzureAuthorityHosts` constants and `get_default_authority()` / `normalize_authority()` from `_internal/utils.py`. Hardcoded URLs break sovereign clouds.

9. **`AZURE_TOKEN_CREDENTIALS` env var.** Narrows DAC before `exclude_*` flags: `prod` keeps only Environment/WorkloadIdentity/ManagedIdentity; `dev` keeps developer credentials + broker; a specific credential name selects one. `SharedTokenCacheCredential` and `BrokerCredential` have no `env_name` and cannot be selected individually.

10. **CAE requires separate caches.** `AadClient` and `MsalCredential` maintain separate token caches for CAE vs non-CAE so tokens don't collide. When adding a credential that supports CAE, ensure it respects this separation.

## Key Internal Flow: `GetTokenMixin`

Most credentials inherit `GetTokenMixin`, which unifies both `get_token()` and `get_token_info()`:

1. Validate at least one scope is provided
2. Build `TokenRequestOptions` from kwargs (for `get_token`) or use options directly (for `get_token_info`)
3. Try `_acquire_token_silently()` (cache hit / refresh token)
4. Check `get_refresh_status()` → `REQUIRED` | `RECOMMENDED` | `NOT_NEEDED`
5. If `REQUIRED` or `RECOMMENDED`, call `_request_token()` (full auth flow)
6. Log result — log level depends on `within_credential_chain` / `within_dac` context

Each credential implements `_acquire_token_silently()` and `_request_token()`.

## Async Parity

Async credentials live under `aio/` and mirror sync, with key differences:

- **MSAL is never used directly in async.** Async `AadClient` performs raw OAuth HTTP via azure-core's async pipeline. Async MI sources hit IMDS/app-host endpoints directly.
- **Three credentials are sync-only** (see pitfall #1).
- **Async DAC has 8 entries** vs sync's 10 (no `InteractiveBrowserCredential`, no `BrokerCredential`).
- Shared helpers should live in sync `_internal/` and be imported by async — don't duplicate.

## Testing

See `references/testing.md` for test commands and patterns.

## References

- Credential taxonomy, MSAL tiers, managed identity, DAC details: `references/architecture.md`
- Test commands and patterns: `references/testing.md`
