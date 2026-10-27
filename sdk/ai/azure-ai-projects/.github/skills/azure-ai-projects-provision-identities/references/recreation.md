# Re-create the same named MI/RBAC set

This is the default **agent-operated provisioning workflow**, not a script switch
or an automatic delete on failure. On each provisioning invocation, create four
new UAMIs and the six project service-role assignments. Keep the requested
subscription, explicit region, literal MI name pattern, RG name and identity
resource names unchanged. For schema 3 the RG is bound to the pattern's UTF-8
SHA256 first 12 lowercase hex characters and the explicit region, not parsed names.
If the set does not yet exist, follow the normal creation workflow directly.
Explicit verify-only requests do not re-create anything.

## Before any deletion

1. Require the exact subscription, tenant, canonical region, literal name pattern and
   original external **schema-3** state. Verify its deployment outputs, owner tags,
   immutable identity IDs and exact role assignments using the guarded script's
   `-VerifyOnly`. Preserve an immutable copy of the old state outside Git. A missing,
   failed, partial or ambiguous baseline must be reconciled before replacement;
   names/tags alone never authorize adoption or deletion. Legacy schema-1 CI state
   and original schema-2 state remain verification-only: stop rather than applying,
   upgrading, rewriting or deleting either legacy set. Obsolete schema-2 previews
   cannot authorize a replacement; require a fresh separately reviewed plan.
2. Verify the same authorized caller's effective create/delete and role-assignment
   permissions, including conditions and denies. Never switch identities or use
   alternate roles to evade a denial. Follow Azure tooling/best-practice guidance.
3. Ensure no pipeline run or other operation is using this set. Check all four
   identities' attached resources/references and any federated credentials. Include
   dependencies outside the identity RG and cross-subscription consumers. A scan of
   only the identity RG or an incomplete inventory does not establish safety. If a
   dependency exists, visibility is incomplete, or a consumer cannot be proven idle
   and detached, stop for a separate migration/detachment plan; do not detach it here.
4. Enumerate the identity RG's resources, nested resources, locks, deployments and
   grants. It must contain only the four recorded UAMIs and their known bootstrap
   deployment records. Reject extra resources, federated credentials, extra grants
   or locks; do not remove protections or recursively delete an unknown resource.
   Enumerate paginated subscription/parent grants as in the verification contract.
5. Compile and check the replacement assets and caller/provider/region prerequisites
   without deploying. Save a separate non-secret replacement manifest containing:
   exact old ownership/IDs; six old project assignment IDs/principals/scopes/conditions;
   four identity IDs; exact RG ID; preserved pipeline assignment IDs; replacement
   parameters/template hash; old/new state paths; and phase `Previewed`. No wildcards
   or name-only deletion targets. The old bootstrap state is not a deletion journal.
6. Present a **dry-run deletion list** (six project assignments, four identities,
   then the empty owned identity RG) and replacement creation plan. Explain that
   every client/principal ID changes, existing credentials and downstream grants
   will not transfer, subscription-wide service access is being restored for the
   new project identity, and an interruption may leave the set unavailable. ARM
   what-if in Incremental mode does **not** preview these deletes. Obtain explicit
   approval for this exact deletion/re-creation plan; never treat an earlier broad
   request, `-Apply`, or this skill definition as approval for the concrete targets.

## Approved replacement

1. Recheck unchanged ownership, dependency absence, grants, template hash and
   quiescence immediately before writing. Capture inventory baseline. Record the
   replacement manifest as `Deleting` before the first deletion.
2. Delete **only the six exact old project-UAMI assignment IDs** from the manifest,
   using the explicit subscription and protected Azure operations. Verify each is
   absent. Do not select by role name alone or remove any assignment belonging to
   another principal. Preserve the pipeline principal's Foundry User, Contributor
   and every unrelated grant; the pipeline identity itself is not being re-created.
3. Delete each of the four exact recorded UAMI resource IDs once. Verify absence
   and recheck the RG contains no remaining resources before deleting the exact
   owned RG. Verify RG absence. Do not retry an ambiguous delete: GET-reconcile the
   recorded targets and stop if the result cannot be established. Do not delete the
   old subscription deployment record or the original state file.
4. Record phase `Deleted`. Use a **new external state path**, fresh owner token and
   deployment name for the same literal pattern/explicit region through the guarded create entry
   point. Never delete or reset the old state to bypass replay protection. Run the
   subscription-bound absence check for all four names across every RG, normal
   ARM validation and full-payload what-if against the now-absent targets.
   Compare the exact scope/resources/role condition/template to the approved plan;
   require new approval on any material drift. Save a separate preview before apply.
5. Record phase `Creating`, then invoke the guarded create once with the approved
   preview. Preserve exact existing pipeline Foundry User via its reuse mode, not
   delete/re-create. GET-reconcile ambiguous results; never repeat a create, restore
   old identities, widen grants or select another set as an automatic fallback.
6. Capture inventory after every attempted replacement, including on failure.
   Verify all new outputs, owner tags, six exact project grants, zero reserved grants
   and unchanged pipeline assignments with `-VerifyOnly`. New client/principal IDs
   must differ from the original generation while resource IDs/names remain equal.
   Persist the new verified state/metadata outside Git and mark the replacement
   manifest `Verified`. On failure record `Failed` plus completed phases and stop;
   report unavailable/remaining resources, never claim rollback or completion.

Re-creation never retargets the live-test pipeline, deploys workloads, updates
consumer bindings or deletes separately retained projects. Such changes require
separate review. Normal live-test runs continue to reuse their configured MIs;
they do not invoke this destructive skill workflow.
