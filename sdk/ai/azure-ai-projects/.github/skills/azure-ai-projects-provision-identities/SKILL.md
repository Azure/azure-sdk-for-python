---
name: azure-ai-projects-provision-identities
description: 'Create or re-create four user-assigned managed identities and their reviewed service RBAC for azure-ai-projects. Default: replace the same named, recorded skill-managed set after a fresh deletion plan and explicit approval, rather than reuse its MIs. WHEN: provision identities in a subscription and region; create MI and RBAC; recreate MI and RBAC; reset an identity set; create regional sample identities; verify existing CI identities or legacy bootstrap state. NOT FOR: deploying workloads; unowned identity deletion; changing the CI target; granting IAM-administrator roles.'
argument-hint: 'subscription <GUID> MI name <pattern> in <canonicalRegion> [tenant <GUID>] [pipeline-principal <object-GUID>]'
---

# Create or re-create an identity set

This is an agent-operated workflow, not an unattended deployment script.
Read [the execution contract](./references/provisioning.md) before any Azure operation.
This skill is the sole owner of identity bootstrap and verification. Use its guarded
[entry point](./scripts/Initialize-SharedSampleIdentities.ps1), bundled
[subscription template](./infra/bootstrap.bicep) and [identity module](./infra/identities.bicep).
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
- Accept an MI name pattern containing exactly one literal `{resource}` token.
   Default: `mi-azsdk-sample-{resource}-wus3`—a default only, not a naming restriction.
   Substitute `project`, `account`, `search` and `function` literally (never evaluate
   expressions); every expanded name must match `[A-Za-z0-9][A-Za-z0-9_-]{2,127}`.
   Any valid prefix/suffix is accepted, including `custom_{resource}_blue` in
   `westus3`. Region is explicit input, never parsed from a name. No `SetName` question.
- For an existing set, require its original external ownership/bootstrap state.
   Missing state or ambiguous ownership is a stop, not permission to adopt/delete it.
- Optionally accept a pipeline service-principal **object GUID**, not its client ID.
  Without it, create no pipeline grant.

### Slash-command arguments

Accept natural-language invocations such as
`/azure-ai-projects-provision-identities with subscription <subscription-GUID> and MI name custom_{resource}_blue in westus3`.
If the MI pattern is omitted, use `mi-azsdk-sample-{resource}-wus3` as the default.
Pass the literal value to `-IdentityNamePattern` (alias `-MiName`), and the region
separately to `-Location`. Do not require the user to enter any fixed prefix,
resource group, set name or regional suffix. Replace only `{resource}` with
`project`, `account`, `search` and `function`. A sample suffix such as `wus3` is
ordinary naming text, not an instruction to choose West US 3.

## Procedure

1. Follow Azure tooling/best-practice guidance. Verify target, region, caller and any
   pipeline principal through protected read-only metadata; do not switch identities.
2. Derive the new RG as `rg-azsdk-identities-<first12 SHA256(pattern)>-<region>`
   from the literal UTF-8 pattern and explicit canonical region. Preserve the four
   exact expanded names. Check all four names throughout the target subscription,
   not just the hashed RG; existing/ambiguous/duplicate matches forbid creation.
   If a recorded schema-3 set exists, complete the reviewed
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

For a recorded schema-1 or schema-2 bootstrap, use the same entry point with `-VerifyOnly`, the
original external `StatePath`, matching subscription/tenant, expected caller object
ID and pipeline object/client IDs. The old environment-only subscription/tenant
inputs remain supported only for schema 1. Do not supply `SetName` for schema 1 or a
different region. Schema 2 requires its explicit recorded region/target and retains
its original set-name parameters and IDs (a separate set-name question is unnecessary).
Verification checks the recorded names and grants
without compiling templates, writing state, upgrading its schema or changing any
original bytes/hash/status. Legacy preview and apply are forbidden.

Keep the pipeline's default identity bindings unchanged when running this skill.
New schema-3 identity sets do not automatically start or
retarget live tests. The operator can explicitly select a verified set through the
pipeline's MI name pattern parameter after checking its exact four identities and
regional metadata. Both legacy schemas remain verification-only; do not apply,
upgrade, rewrite, delete or rename those sets. Obsolete schema-2 previews require
a fresh separately reviewed schema-3 dry run at a new state path, never replay.

## Validation

Compile both Bicep assets without deploying. Check frontmatter/name and relative links.
Verify the compiled graph creates exactly one RG, four UAMIs and six project grants,
plus the optional pipeline Foundry User grant—nothing else.
Run all offline `*.Tests.ps1` suites under [tests](./tests) using Pester 4.10.1.
They exercise the real entry point with isolated CLI/HTTP fixtures, arbitrary
literal patterns, legacy-state byte preservation and worker-contract consistency.