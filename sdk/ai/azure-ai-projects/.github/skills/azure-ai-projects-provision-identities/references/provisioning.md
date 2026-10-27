# Execution contract

## Target and names

Use `subscription` and `region` supplied to the skill. Verify the subscription is
Enabled and accessible to the existing caller; resolve its tenant and compare it
with the caller token tenant. Confirm any supplied tenant matches. Never log in,
choose another identity, fall back to another subscription/region, or read `.env`.
Verify `region` is an exact canonical `name` from the target subscription's location
metadata. This verifies an MI/RG location, not Foundry, model or Search availability.

Validate explicit region with `^[a-z][a-z0-9]{0,29}$`. Accept any literal MI name
pattern with exactly one case-sensitive `{resource}` token, provided all four
expanded names match `^[A-Za-z0-9][A-Za-z0-9_-]{2,127}$`. Use string replacement,
never expression evaluation. `mi-azsdk-sample-{resource}-wus3` is the default, NOT
a naming restriction or a legacy-state lookup. `custom_{resource}_blue` in
`westus3`, `{resource}`, and names without hyphens or region suffixes are valid.
Never derive the explicit region from a name or require a `SetName` input.
Use nonzero canonical GUIDs for all identity inputs. Derive:

- New RG: `rg-azsdk-identities-<first12 lowercase SHA256(UTF8(literal pattern))>-<region>`.
- UAMIs: literal substitution of `project`, `account`, `search`, `function` into
  the requested pattern, with no added prefix, hyphens or suffix.
- Owner: a fresh 32-character GUID without hyphens; not a secret or credential.
- Subscription deployment: `azsdk-identities-{first 12 characters of ownerToken}`.

On a provisioning invocation, the default is to **re-create the same named MI/RBAC
set**. Follow [the replacement workflow](./recreation.md) for a recorded skill-managed
schema-3 set that exists; do not silently reuse identities or change the pattern. No deletion
is authorized until that workflow's checks, fresh dry run and exact approval pass.

The guarded creation script rejects an existing RG,
prior apply record or ambiguous existence response. Bicep is an **upsert**, not a
create-only ownership boundary. Re-creation is agent-orchestrated before creation;
there is no script `-Recreate` bypass. Preserve old state; a new generation uses a
new state path only after the old set's deletion is fully verified.

Before a new preview and immediately before create, enumerate the target
subscription's UAMIs through protected paginated ARM GETs. Bind every page to the
same subscription collection, API version and host; reject malformed/duplicate
metadata, pagination loops or scope/filter changes. All four expanded names must
be absent across **every RG**, case-insensitively. In particular, default names
already present in the original legacy RG must never be recreated under a hashed
RG. An absence check is not a distributed lock: the operator must keep the
subscription's identity provisioning quiescent through the approved create.

## Role contract and approval

The project UAMI receives these six roles **at subscription scope**:

| Role | Definition GUID |
| --- | --- |
| Foundry User | `53ca6127-db72-4b80-b1b0-d745d6d5456d` |
| Storage Blob Data Contributor | `ba92f5b4-2d11-453d-a403-e96b0029c9fe` |
| Storage Blob Data Owner | `b7e6dc6d-f1e8-4753-8033-0f276bb0955b` |
| Cosmos DB Operator | `230815da-be43-4aae-9cb4-875f7bd000aa` |
| Search Service Contributor | `7ca78c08-252a-4471-8644-bb5ff32d4ba0` |
| Search Index Data Contributor | `8ebe5a00-799e-43f5-93ac-243d3dce84a7` |

The other three UAMIs have **zero grants**. Optional pipeline principal receives
Foundry User only; verify its enabled service-principal object/client mapping in the
target tenant. Reuse only an exact Foundry User assignment for that object ID at
the target subscription scope, with `principalType=ServicePrincipal` and no condition
or condition version. Record its assignment ID in the plan, retain the verified
principal/assignment parameters, set `createPipelineGrant=false` so the template
does not deploy that assignment, and verify it unchanged afterward. Broader/different
roles or narrower scopes do not satisfy this contract. Never duplicate, update or
relax an existing assignment; ambiguous or conditioned matches require review.

Explain before approval: these roles reach matching **existing and future resources
throughout the subscription**, not just the identity RG or test RGs. Sharing a project
identity reduces workload isolation. The exact Blob Owner condition in the template
restricts only tag read/write and filtering to container names ending `-azureml-agent`.
It omits the original per-workspace prefix; **other Blob Owner operations remain
allowed**. Show the complete condition, not just this summary. If declined, stop;
do not silently substitute an unconditioned role or invent narrower semantics.

Check caller direct/inherited/group role conditions and denies; a general
`roleAssignments/write` action does not prove this request is authorized. Never
grant Owner, User Access Administrator, RBAC Administrator or equivalents to get around
a denial. Preserve all existing Contributor grants and protected-resource checks.

## Preview, apply, reconcile

After CLI guidance, use explicit `--subscription <subscription>` on Azure CLI calls.
Use `az bicep build --file <skill>/infra/bootstrap.bicep --stdout` for compilation.
Keep the reviewed compiled bytes and non-secret parameter file outside Git; never
print token responses or authorization headers. Bound HTTP requests, disallow credential
redirects and suppress raw authentication/error bodies.

Use `az deployment sub validate`, then `az deployment sub what-if` with the recorded
name, explicit location, compiled template and same parameters; request
`--no-pretty-print --result-format FullResourcePayloads` for what-if.
Accept only the new RG, four UAMIs, six project grants and optional seventh grant;
no Modify/Delete/unknown targets. Runtime UAMI principal references can remain unresolved:
review compiled role IDs, scopes, conditions, names and dependencies separately, and
disclose unresolved predictions. Do not equate preview with actual authorization.

Present this fresh preview and obtain exact approval. Record status `Applying`
**before** the single `az deployment sub create`. Use the same reviewed bytes,
parameters, name and target. Record success/failure, capture inventory in either case,
and GET the recorded deployment after an ambiguous response—never blindly resubmit.

Verify RG location/tags; all four identity IDs, tenant, principal/client IDs and tags;
six exact project assignments (including `ServicePrincipal`, scope, condition/version);
zero assignments for reserved identities; and optional pipeline Foundry User. Enumerate
paginated assignments, including descendant and inherited scopes, and reject unexpected
grants on the new identities. Compare immutable IDs with deployment outputs. Existing
pipeline roles remain untouched. Save `Verified` only after all checks pass.

Retain state outside Git. Creating this set does **not** retarget the existing CI:
its default identity selection remains unchanged. An operator must explicitly
select the verified MI name pattern to use a different skill-managed set; live
preflight verifies its actual metadata and regional workload eligibility.
This skill never updates pipeline configuration or queues a test run. No automatic cleanup.

## Single entry point and legacy verification

Use [the guarded script](../scripts/Initialize-SharedSampleIdentities.ps1) for both
new schema-3 sets and verification. New sets require explicit `SubscriptionId`,
`TenantId`, `Location`, `ExpectedCallerPrincipalId` and external `StatePath`;
`IdentityNamePattern` defaults as above. Schema 3 saves the exact pattern, hashed
group, explicit canonical region, four immutable resource IDs, parameters and
compiled hash. Reject target/pattern/group/region drift before Azure or state writes;
optional pipeline object/client IDs must be supplied together. The agent resolves
and confirms metadata and approval before invoking the corresponding script mode.

Existing schema-1 CI state and original schema-2 state are **verification-only**.
Supply the original state and
matching caller/pipeline/target identifiers with `-VerifyOnly`. Only in this legacy
schema-1 mode may subscription/tenant come from the original environment variables.
Schema 1 retains fixed West US 3 names; schema 2 retains its original recorded
set-name, group, region, four IDs and compiled parameters. Schema 2 requires
explicit matching subscription/tenant/region, not inferred naming conventions.
An optional pattern must expand to its original exact names. GETs reconcile
the original recorded deployment if needed; no templates or removed bootstrap
files are required. Preserve every original state byte, hash and status, including
on failure; never upgrade, rewrite, reapply or recreate either legacy set. Reject
obsolete schema-2 `Previewed` apply before any calls/writes; preserve that preview
and require a fresh schema-3 dry run at a new path and a new exact approval.
