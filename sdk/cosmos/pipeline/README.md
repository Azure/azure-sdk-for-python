# Cosmos live-test accounts

The Cosmos live tests bind to **fixed, team-owned Cosmos DB accounts** instead of provisioning a
new account on every pipeline run.

## Why

The azure-sdk live-test tenant is destroyed and recreated roughly every 90 days. Each rotation
invalidates the service principals, the `azure-sdk-tests-cosmos` service connection and every RBAC
assignment, so any run that calls `eng/common/TestResources/deploy-test-resources.yml` →
`New-TestResources.ps1` fails on auth until a human re-onboards the tenant.

Fixed accounts move that coupling to a single rotatable secret. On rotation, someone regenerates the
accounts JSON and updates one variable — no repo change, no pipeline change.

This mirrors [Azure/azure-sdk-for-java#49735](https://github.com/Azure/azure-sdk-for-java/pull/49735),
and deliberately reads the **same secret, in the same schema, from the same accounts**. Tracking
issue: [Azure/azure-sdk-for-python#48236](https://github.com/Azure/azure-sdk-for-python/issues/48236).

## The accounts

They live in resource group `sdk-ci` of the Cosmos-team-owned subscription
`CosmosDB_Test_Subscription` (`54c97bd0-fc52-41c8-a5f2-faf722f1f417`), named `sdkci-<selector>`.
That subscription is not part of the ephemeral tenant, which is the whole point.

Java's `New-CosmosLiveTestAccounts.ps1` is the shared provisioning/rotation tool. **Do not duplicate
it here** — Python consumes the same accounts and the same JSON.

## Selector map

| Selector | Shape | Python matrix legs |
|---|---|---|
| `single-session` | 1 region, Session | `cosmosQuery`, `cosmosLong` (×2), `cosmosSearchQuery` |
| `single-session-split` | 1 region, Session, isolated | `cosmosSplit` (×2) |
| `multiregion-tc-session` | 2 regions, Session, **single**-write | `cosmosCircuitBreakerMultiRegion`, `cosmosPerPartitionAutomaticFailover` |
| `multimaster-multiregion-session` | 2 regions, Session, multi-write | `cosmosMultiRegion` (×3), `cosmosCircuitBreaker` |

That is 12 of the 20 matrix jobs. The other 8 are the 7 `cosmosAAD*` legs (see below) and `cosmosGSI`,
which already has its own fixed account via `$(gsi-pipeline-uri)`/`$(gsi-pipeline-key)`.

Python needs far fewer accounts than Java's 18 because it does not vary account consistency per leg
and has no thin-client / HTTP-2 / pmerge / Kafka lanes.

Notably the two circuit-breaker lanes need **no dedicated account**: `AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER`
is a client-side SDK setting (`azure/cosmos/_constants.py`, `CIRCUIT_BREAKER_ENABLED_CONFIG`), and
per-partition failures are injected in-process by `tests/_fault_injection_transport.py` rather than
by degrading the real account. Per-partition automatic failover is likewise faked by rewriting the
`GetDatabaseAccount` response. Those legs only need the right account *topology*.

The region difference from the old bicep (Java's accounts are Central US / East US 2; the bicep used
West US 3 / West Central US) is safe: `tests/test_config.py` reads `WRITE_LOCATION` / `READ_LOCATION`
from `client.get_database_account()` at runtime, and no live test pins a region literal.

## How a run binds to an account

Rollout is staged. Today:

1. Each key-auth leg in `live-platform-matrix.json` sets `AccountSelector`. AAD legs deliberately do not.
2. The pipeline still provisions an account per run, as before.
3. `resolve-test-account-steps.yml` runs in `BeforeTestSteps`, which
   `eng/pipelines/templates/steps/build-test.yml` executes in the same job **after** the ARM deployment
   and immediately before the pytest task.
4. `resolve-cosmos-test-account.ps1` reads the JSON secret, looks up the selector and republishes
   `ACCOUNT_HOST` / `ACCOUNT_KEY`, **overwriting** the values the deployment just set. `tests/test_config.py`
   already reads exactly those two names, so no test-side change is needed. Legs with no selector skip
   the step entirely and keep the account they provisioned.

This proves the accounts, the secret and the resolver end to end while leaving the AAD lane untouched.
It does not yet make the key legs survive a tenant rotation, because the deployment still runs.

Next, once that is green: set `DisableAzureResourceCreation: true` so
`eng/pipelines/templates/jobs/live.tests.yml` skips both the deployment and its teardown. That is the
change that actually removes the tenant coupling. It is a stage-level parameter and the AAD legs share
the stage, so it needs one of:

- **Split the pipeline** — a second `tests-aad.yml` with its own matrix, keeping the AAD legs on
  provisioning. Fully repo-local; costs one new ADO pipeline registration.
- **Move AAD onto the fixed accounts** — assign the data-plane role to the current tenant's test
  principal on the `sdk-ci` accounts as part of the rotation runbook. Keeps one pipeline and makes the
  AAD lane rotation-proof too, but needs `azure-sdk-tests-cosmos` granted rights to write
  `sqlRoleAssignments` on the `sdk-ci` resource group.
- **A per-leg runtime gate** — add a `Condition` parameter to
  `eng/common/TestResources/{deploy,remove}-test-resources.yml`. Generic and useful to other repos, but
  it is an azure-sdk-tools change with a sync lag.

`DisableAzureResourceCreation` already exists and defaults to `false`, so the plumbing is in place.

### Why PowerShell and not Java's bash + jq

The Python live matrix runs legs on `windows-2022` and macOS as well as Linux. Neither bash nor jq
can be relied on there. `pwsh` ships on all three hosted images and `ConvertFrom-Json` removes the
jq dependency entirely.

### The double-set convention

Keys are published twice:

```
##vso[task.setvariable variable=_ACCOUNT_KEY;issecret=true]<key>
##vso[task.setvariable variable=ACCOUNT_KEY;issecret=false]<key>
```

The first registers the literal with the log scrubber so it is masked everywhere. The second is what
actually reaches the test process — a variable marked `issecret=true` is deliberately *not*
auto-exported as an environment variable, so on its own the tests would see no key at all. This is
the same trick `eng/common/TestResources/TestResources-Helpers.ps1` uses for ARM outputs.

### What the resolver deliberately does not emit

Account consistency, preferred locations and `AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER` are per-leg
concerns owned by `live-platform-matrix.json`. Emitting them from the resolver would clobber the
matrix values and silently change what a lane tests. `resolve-cosmos-test-account.tests.ps1` asserts
this.

## AAD legs still provision

The `cosmosAAD*` legs are **not** on fixed accounts. `test-resources.bicep` creates a custom
`sqlRoleDefinition` plus a `sqlRoleAssignment` for `testApplicationOid`, and that principal is
tenant-scoped — it changes on every rotation. So `test-resources.bicep` must stay, and those legs set
no `AccountSelector`, which makes `resolve-test-account-steps.yml` skip itself for them (see its
`condition`).

Because the resolver only overrides `ACCOUNT_HOST`/`ACCOUNT_KEY` for legs that name a selector, the
key-auth and AAD lanes coexist in one stage today with no interference.

Note also that `AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER` still arrives as a bicep output while provisioning
is on. When provisioning is switched off it has to move to a per-leg matrix env var — it is a
client-side SDK setting (`azure/cosmos/_constants.py`), not an account property, and the bicep only
echoes the parameter straight back out.

## Running the tests locally

```powershell
pwsh ./sdk/cosmos/pipeline/resolve-cosmos-test-account.tests.ps1
```

No Pester, no modules — plain `pwsh`, matching the zero-dependency posture of the resolver itself.

To see what the resolver would export without ADO logging commands:

```powershell
./sdk/cosmos/pipeline/resolve-cosmos-test-account.ps1 `
  -AccountsJson (Get-Content accounts.json -Raw) `
  -Selector single-session `
  -Local
```

## Rotating the secret

1. Recreate/refresh the accounts with Java's `New-CosmosLiveTestAccounts.ps1`.
2. Regenerate the accounts JSON (schema: Java's `live-test-accounts.schema.json`, `version: 1`).
3. Update `sub-config-cosmos-azure-cloud-test-resources` in the
   `Test Secrets for Cosmos Live Tests - user administered` variable group.
4. Re-run one leg as a smoke test.

No repo change is required, in either language.
