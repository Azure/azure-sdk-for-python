---
name: azure-identity
description: 'Domain knowledge for azure-identity. Covers architecture, credential chain, MSAL integration, sync/async split, managed identity, token APIs, and common pitfalls. WHEN: modify azure-identity; fix azure-identity bug; add azure-identity credential; add azure-identity feature; change azure-identity DefaultAzureCredential; update azure-identity managed identity.'
---

# azure-identity — Package Skill

`azure-identity` is **entirely hand-authored**: no TypeSpec, no `_generated/`, no `_patch.py`, and no regeneration step. Every changed file is production source, so first verify public API exports, sync/async parity, credential-chain behavior, and tests.

```
azure/identity/
├── __init__.py              # public sync exports; __all__ is the contract
├── _credentials/            # sync credentials, DAC, managed identity dispatcher
├── _internal/               # shared auth plumbing; not public API
└── aio/                     # async mirror, with fewer public credentials
```

**Extension package:** `azure-identity-broker` provides `InteractiveBrowserBrokerCredential` (sync only) for broker auth on Windows, macOS, Linux, and WSL, with non-Windows/WSL fallback behavior. `VisualStudioCodeCredential` requires this package and only works on Windows/WSL.

## Common Pitfalls

1. **Public symbols require `__all__`.** Add new sync public symbols to `azure/identity/__init__.py`; add async-applicable symbols to `azure/identity/aio/__init__.py`.
2. **Three credentials are sync-only.** Do not add async `DeviceCodeCredential`, `InteractiveBrowserCredential`, or `UsernamePasswordCredential`.
3. **MSAL is sync-only.** Async credentials may reuse MSAL `TokenCache`, but never instantiate `msal.PublicClientApplication`, `ConfidentialClientApplication`, or `ManagedIdentityClient`.
4. **DAC chain order is contract-sensitive.** Sync DAC has Environment, WorkloadIdentity, ManagedIdentity, SharedTokenCache, VS Code, CLI, PowerShell, Developer CLI, InteractiveBrowser (excluded by default), Broker. Async DAC stops after Developer CLI.
5. **`within_dac` is intentional.** DAC sets this `ContextVar` while iterating so child credentials suppress noisy errors and exit fast on `CredentialUnavailableError`.
6. **Managed identity dispatch is environment-driven.** Cloud Shell uses the in-house `ManagedIdentityClient`; most other managed-identity hosts use `MsalManagedIdentityClient`; Workload Identity dispatches to `WorkloadIdentityCredential`.
7. **Never hardcode authorities.** Use `AzureAuthorityHosts`, `get_default_authority()`, and `normalize_authority()` so sovereign clouds work.

## Token API Rule

Every credential supports `get_token()` and `get_token_info()` through `GetTokenMixin`. `get_token()` is legacy but supported; new token-response features such as PoP, `refresh_on`, or non-Bearer token types belong on `get_token_info()` / `TokenRequestOptions`.

## Change Checklist

1. Mirror sync changes under `aio/` unless the credential is one of the three sync-only credentials.
2. Keep shared helpers in sync `_internal/` and import them from async; do not duplicate logic.
3. If DAC changes, update both sync and async defaults, exclude kwargs, `AZURE_TOKEN_CREDENTIALS` behavior, and tests.
4. If token acquisition changes, preserve CAE/non-CAE cache separation and multi-tenant `additionally_allowed_tenants` checks.
5. Update `CHANGELOG.md`, README snippets, and troubleshooting links when public behavior changes.

After code changes, run the package validation tool:

```
azsdk_package_run_check with packagePath="sdk/identity/azure-identity" and checkType="All"
```

For targeted local checks from `sdk/identity/azure-identity`, use `azpysdk pytest .`, `azpysdk pylint .`, `azpysdk mypy .`, and `azpysdk sphinx .`.

## References

- Credential taxonomy, MSAL tiers, managed identity, DAC details: `references/architecture.md`
- Test commands and patterns: `references/testing.md`
