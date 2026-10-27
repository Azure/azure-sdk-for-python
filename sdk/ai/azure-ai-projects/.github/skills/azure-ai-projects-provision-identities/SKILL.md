---
name: azure-ai-projects-provision-identities
description: 'Create or re-create four user-assigned managed identities and their reviewed service RBAC for azure-ai-projects. Default: replace the same named, recorded skill-managed set after a fresh deletion plan and explicit approval, rather than reuse its MIs. WHEN: provision identities in a subscription and region; create MI and RBAC; recreate MI and RBAC; reset an identity set; create regional sample identities; verify existing CI identities or legacy bootstrap state. NOT FOR: deploying workloads; unowned identity deletion; changing the CI target; granting IAM-administrator roles.'
argument-hint: 'subscription=<GUID> region=<canonical-region> set-name=<stable-name> [tenant=<GUID>] [pipeline-principal=<object-GUID>]'
---

# Create or re-create an identity set

This is an agent-operated workflow, not an unattended deployment script.
Read [the execution contract](./references/provisioning.md) before any Azure operation.
This skill is the sole owner of identity bootstrap and verification. Use its guarded
[entry point](./scripts/Initialize-SharedSampleIdentities.ps1), bundled
[subscription template](./assets/bootstrap.bicep) and [identity module](./assets/identities.bicep).
The live-test pipeline only consumes existing identities; it never invokes bootstrap.

**Default on every provisioning invocation: re-create the same named set and its MI
RBAC, not reuse existing MIs or silently choose a fresh name.** If the set is absent,
create it. If the recorded skill-managed set exists, follow the
[replacement workflow](./references/recreation.md) first. Re-creation changes all
client/principal IDs even though resource IDs/names stay the same. Never start
deletion without a fresh exact dry run and explicit approval. A user request to
verify only remains read-only. This skill definition is not approval to delete any
particular existing set.

## Inputs

- Require an explicit **subscription GUID** and **canonical region**. Resolve and confirm
  the target tenant using that subscription, never the active-account default.
- Require a confirmed stable `setName` (lowercase letters/digits/hyphens, 1–24
   characters). Ask if omitted; never pick a new random name to avoid replacement.
- For an existing set, require its original external ownership/bootstrap state.
   Missing state or ambiguous ownership is a stop, not permission to adopt/delete it.
- Optionally accept a pipeline service-principal **object GUID**, not its client ID.
  Without it, create no pipeline grant.

## Procedure

1. Follow Azure tooling/best-practice guidance. Verify target, region, caller and any
   pipeline principal through protected read-only metadata; do not switch identities.
2. Derive the exact RG and four identity names. If they exist, complete the reviewed
   replacement workflow; never use the create script to upsert an existing set.
   Preserve the old state and use a new state path for the replacement generation.
   Compile the bundled assets;
   save non-secret parameters, owner token, compiled-template hash and deployment name
   outside the repository. Run ARM validation and full-payload what-if.
3. Present the exact identities, roles, scopes and Blob Owner condition. Explain the
   subscription-wide access and ask for **explicit approval for this exact plan**.
   Previous approvals for another set/subscription/region never transfer.
4. After approval, recheck absence and unchanged inputs/template; capture inventory
   baseline, mark the attempt before writing, then create **once** from the reviewed
   compiled bytes. Capture inventory on success or failure. Never retry an ambiguous create.
5. Verify deployment outputs, immutable identity metadata, ownership and every exact
   grant using GETs. Persist verified resource IDs and principal/client IDs; retain the
   permanent resources until the next explicitly approved skill re-creation. Stop
   on any mismatch; no failure-triggered cleanup, repair or blind retry.

No workloads, secrets, federation, Contributor changes or IAM-administrator grants.
Do not change pipeline mappings or claim workload/region compatibility from MI success.

## Verify existing CI identities

For a recorded schema-1 bootstrap, use the same entry point with `-VerifyOnly`, the
original external `StatePath`, matching subscription/tenant, expected caller object
ID and pipeline object/client IDs. The old environment-only subscription/tenant
inputs remain supported for this verification mode. Do not supply `SetName` or a
different region. Verification checks the original fixed West US 3 names and grants
without compiling templates, writing state, upgrading its schema or changing any
original bytes/hash/status. Legacy preview and apply are forbidden.

Keep the pipeline's default identity bindings unchanged when running this skill.
New schema-2 identity sets use different names and do not automatically start or
retarget live tests. The operator can explicitly select a verified set through the
pipeline's project MI name parameter after checking its target and regional
eligibility. Legacy schema-1 state remains verification-only; the generic
re-creation workflow must not delete or rename that fixed CI set.

## Validation

Compile both Bicep assets without deploying. Check frontmatter/name and relative links.
Verify the compiled graph creates exactly one RG, four UAMIs and six project grants,
plus the optional pipeline Foundry User grant—nothing else.
Run the [offline Pester suite](./tests/Initialize-SharedSampleIdentities.Tests.ps1)
using Pester 4.10.1; it exercises the real entry point with isolated CLI/HTTP fixtures,
including legacy-state byte preservation and worker-contract consistency.