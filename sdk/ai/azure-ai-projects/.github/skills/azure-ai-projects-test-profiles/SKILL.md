---
name: azure-ai-projects-test-profiles
description: 'Configure independent azure-ai-projects test profiles and manually runnable pipelines per Foundry project endpoint. WHEN: create test profile without running; add/update profile after ADO live validation; manually edit test configuration; create endpoint test pipeline; run saved project tests. One profile per exact pytest node, values in ADO Library, no custom backend. DO NOT USE FOR: recording tests; authoring samples; other packages.'
argument-hint: 'Exact test ID; add/update/configure project pipeline; no prior run required'
---

# Independent test profiles and endpoint pipelines

Profiles do not contain pipeline IDs, endpoint values, credentials, or build prerequisites. See [manual administration and setup](./references/setup.md). All assets stay under azure-ai-projects; do not commit, push, create ADO resources, or run live services without separate approval.

## Configure a profile without running

1. Obtain the **exact package-relative pytest node**, including its parameterized case, and exact sample path. Use the original validation preview when available. Optional collection with the existing resolver is offline; never run a live test merely to configure a profile. Wildcard requests must become one profile per selected exact node.
2. Prepare one non-secret profile using [the example](./assets/profile.example.json): `TestId`, `SamplePath`, `Enabled`, and `Environment`. Include `FOUNDRY_PROJECT_ENDPOINT` with `Source: ProjectEndpoint`; other names use `Source: Variable` and a Library variable reference. No literal values or secrets belong in this file. The registry is keyed uniquely by exact TestId, not by a user alias or build ID.
3. Preview [SetTestProfile.ps1](./scripts/SetTestProfile.ps1) with `-ProfileFile` and either `-RegistryFile` or `-RegistryGroupId`. Existing TestIds require `-Update`; new TestIds must not use it. Local preview has no network; ADO preview makes GET requests only using a token held in `AZURE_DEVOPS_BEARER_TOKEN` or `-BearerToken`. Never print tokens or request secret values through chat.
4. Show the profile, environment **names/references**, and preview digest. Ask the question tool for explicit save approval. Repeat identical inputs with `-Run -ConfirmSave -ExpectedDigest <preview digest>`. Saving never collects/runs tests, recreates pipelines, or changes endpoint values. Changes since preview require fresh review. The ADO registry group must be metadata-only; serialize administration because variable groups do not provide atomic compare-and-swap revisions.
5. Report Add/Update and `Execution: Not run (configuration only)`. Past test results remain in their ADO builds; a configuration save never establishes live-test success.

## Bind profiles to a project pipeline

1. In ADO Library, create/select one separate variable group for the project. It contains the authoritative `FOUNDRY_PROJECT_ENDPOINT`, `SAMPLE_TEST_PROFILE_IDS` JSON array of exact TestIds, and each referenced value. Mark sensitive entries secret and authorize only the appropriate endpoint pipeline. Values are ordinary individually editable group entries, not encoded profile snapshots.
2. Preview [NewTestProjectPipeline.ps1](./scripts/NewTestProjectPipeline.ps1) with the endpoint, group names, and `-ValueVariable` names. It derives one deterministic wrapper path from the normalized endpoint; it never puts the URL or values in source. Ask approval before `-Run -ConfirmWrite`; existing wrappers require an explicitly reviewed `-Replace`.
3. The generated no-parameter wrapper uses the shared endpoint stage template. Creating its ADO definition, authorizing groups/service connection, and publishing the wrapper are separate approved operations. After setup, **Run pipeline > Run** executes all enabled assigned profiles without retyping configuration. A conflicting endpoint fails rather than silently retargeting tests.
4. Existing group values and membership may be edited in Library without recreating the pipeline. A newly referenced variable name needs an explicit wrapper mapping and separately approved publish; do not imply secret variables are automatically exported or fetched by REST.

## After a skill-started ADO run

Once ADO is confirmed completed, report its actual result and ask **Add new test profile / Update existing test profile / Skip**. Use the exact nodes and original effective names to prepare independent metadata profiles; map values to the chosen project group instead of importing `.env` wholesale. Collect/update endpoint values in Library through the user's approved administration workflow, never in source or chat. Saving a profile and assigning it to a project are separate decisions. For failed builds preserve the failure in the report; saving must not imply the test passed. Unknown/timed-out builds do not trigger the prompt. Respect Skip.

An optional master uses [InvokeTestProjectsMaster.ps1](./scripts/InvokeTestProjectsMaster.ps1) to queue endpoint pipeline IDs/branches only. It stores no test profiles or environment values. The endpoint pipelines remain independently manually runnable; ADO jobs themselves do not display Copilot dialogs.