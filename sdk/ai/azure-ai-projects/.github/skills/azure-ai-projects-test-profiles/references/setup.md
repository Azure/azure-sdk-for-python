# Manual profile and endpoint pipeline administration

No custom backend is required. ADO Library stores configuration; all test execution remains in pipeline agents. The existing ad-hoc sample-validation pipeline and scripts are unchanged.

## Three independent records

| Record | Storage | Contains |
| --- | --- | --- |
| Test profile, unique per exact pytest node | Non-secret `SAMPLE_TEST_PROFILES_JSON` in a dedicated Library group | Sample path, exact TestId, enabled flag, required environment names and variable references. No pipeline IDs or literal endpoint/secret values. |
| Foundry project | One separate Library variable group per endpoint | Authoritative `FOUNDRY_PROJECT_ENDPOINT`, individually editable value entries, and membership `SAMPLE_TEST_PROFILE_IDS`. |
| Endpoint pipeline | One ADO definition per generated endpoint wrapper | Uses shared code and explicit group/value bindings. No required Run dialog parameters. |

The same profile can be assigned to multiple endpoint groups. A reference such as `AGENT_MODEL_DEPLOYMENT` can resolve differently in each group's values. The profile's main endpoint is always inherited; a profile-level main endpoint override is rejected. `LLM_VALIDATION_PROJECT_ENDPOINT` is a distinct optional reference, not the project's identity.

## 1. Configure a profile manually, with no test execution

Start with the profile example in this skill's assets directory. It illustrates the basic-agent test; collect the exact node for your branch if its name changed. Environment bindings have only these shapes:

```json
{"Name":"FOUNDRY_PROJECT_ENDPOINT","Source":"ProjectEndpoint"}
```

```json
{"Name":"FOUNDRY_MODEL_NAME","Source":"Variable","Variable":"AGENT_MODEL_DEPLOYMENT"}
```

Store real values in Library, never the registry. Required sample and harness names (including an LLM validation endpoint when used) must be represented; runtime preflight fails before live execution if any are missing.

For local non-secret configuration, run from the package root, using paths to your profile document and registry export:

```powershell
$settings = @{
    ProfileFile = 'C:\temp\agent-profile.json'
    RegistryFile = 'C:\temp\test-profiles.json'
}
$preview = & .\.github\skills\azure-ai-projects-test-profiles\scripts\SetTestProfile.ps1 @settings
$preview
# Only after reviewing and approving this save:
& .\.github\skills\azure-ai-projects-test-profiles\scripts\SetTestProfile.ps1 @settings `
    -Run -ConfirmSave -ExpectedDigest $preview.ExpectedDigest
```

There is no `SourceBuildId` requirement and no live-service call. Saving validates schema, not test existence or live functionality. The project runner verifies exact collection before actual execution. Add `Update = $true` to settings for an explicitly reviewed existing TestId replacement. A changed TestId is a new profile; update membership accordingly.

For ADO-native storage, create a **metadata-only** Library group named `azure-ai-projects-test-profiles`. Add a non-secret variable `SAMPLE_TEST_PROFILES_JSON` initialized with `{"Version":1,"Profiles":[]}`. You may edit that JSON directly in **Pipelines > Library**, or replace `RegistryFile` with `RegistryGroupId` in the helper settings. Supply an in-memory token with Library edit access; do not print it. Preview performs GETs, and apply uses GET/recheck/PUT only on that group. It refuses groups holding secret variables. Serialize edits: the recheck detects stale reviews but the Library API has no atomic revision guard against simultaneous administrators.

## 2. Configure one Foundry endpoint group

In **Pipelines > Library > Variable groups**, create a group such as `foundry-project-staging` with:

| Variable | Value to enter in Library |
| --- | --- |
| `FOUNDRY_PROJECT_ENDPOINT` | The real project's HTTPS endpoint, ending `/api/projects/<project>`. |
| `SAMPLE_TEST_PROFILE_IDS` | A JSON array of exact TestId strings assigned to this endpoint. |
| `AGENT_MODEL_DEPLOYMENT` | The model deployment name for this project. |
| `VALIDATION_PROJECT_ENDPOINT` | The endpoint required by the sample harness's LLM validator, if used. |

Mark confidential values secret. They must never be echoed; the runner suppresses environment previews. ADO masks complete secret values, not arbitrary substrings. Do not store personal ADO tokens. Use a service connection's workload identity for Azure authentication; the template retains the existing `azure-sdk-tests` connection.

Keep `SAMPLE_TEST_PROFILES_JSON` only in the registry group and `SAMPLE_TEST_PROFILE_IDS` only in the endpoint group. Avoid duplicate reserved configuration names in other linked groups. Authorize only the relevant pipelines, not Open access for all pipelines. Test-profile admins need registry edit permission; endpoint admins control values and membership. Treat changes to either as privileged because they affect live tests.

Changing a group's value or membership affects future runs, not an in-progress run. Every TestId must exist in the registry, and repeated IDs are rejected. Disabled profiles are skipped. Test-specific references can use different variable names in the same group when two tests require different values for the same environment name.

## 3. Generate and register the endpoint pipeline

Preview the generator with the real endpoint supplied privately in your terminal; the endpoint itself never enters the YAML:

```powershell
$projectSettings = @{
    FoundryProjectEndpoint = $env:FOUNDRY_PROJECT_ENDPOINT
    ProjectVariableGroup = 'foundry-project-staging'
    RegistryVariableGroup = 'azure-ai-projects-test-profiles'
    ValueVariable = @('AGENT_MODEL_DEPLOYMENT', 'VALIDATION_PROJECT_ENDPOINT')
}
& .\.github\skills\azure-ai-projects-test-profiles\scripts\NewTestProjectPipeline.ps1 @projectSettings
# After approval to write the generated wrapper:
& .\.github\skills\azure-ai-projects-test-profiles\scripts\NewTestProjectPipeline.ps1 @projectSettings -Run -ConfirmWrite
```

It writes a small no-parameter wrapper under the package's pipelines/projects directory. Its deterministic `foundry-<endpoint hash>` filename and immutable expected hash bind the definition to one normalized endpoint (including the project path, not just the hostname). A trailing slash does not produce another identity. An existing wrapper is not overwritten without `-Replace`. The generator does not create an ADO definition, start a build, commit, or push.

After a **separately approved publish**, create one ADO definition selecting that wrapper. Set its default branch, authorize both Library groups, the shared 1ES template repositories, agent pool, and existing `azure-sdk-tests` connection. Choose **Run pipeline > Run**. No environment, test selector, or profile ID entry is required at run time. The source branch must contain the referenced exact tests. A changed endpoint group fails the immutable hash check; generate/register a separate endpoint wrapper instead of silently repointing one.

The wrapper explicitly maps listed value variables into the task. This is required for secrets: they are not automatically environment variables and cannot be recovered with a REST GET. Existing value edits need no YAML edit or pipeline recreation. A new referenced variable name requires adding its name with the generator's `-Replace`, reviewing/publishing that wrapper, and authorizing any new resource; there is still no need to recreate the definition. No dynamic group selection based on runtime variables is used.

## 4. Execution and reports

The shared stage installs dependencies once, validates every assigned profile, verifies literal exact node collection, and previews every test with an empty environment file before calling live execution. It never falls back to wildcards. Each profile runs in a new pytest process with its own environment assignment and JUnit file; one profile failure does not prevent other assigned tests. No recordings are written. A fresh JUnit report must contain exactly the assigned executed, passed test; skipped, missing, or collection-only results are failures rather than false success. Profile bindings cannot change Python/pytest controls or recording flags, and inherited pytest option/plugin overrides are rejected. Results, sample log attachments, and a per-profile summary are published in the endpoint run.

The pipeline's 120-minute job limit bounds execution. It does not make tests safe to run concurrently against shared destructive resources. Keep conflicting tests in separate endpoint runs or serialize manual use. Ordinary profile saves do not establish validation history: completed builds and their reports remain the source of execution results.

After a Copilot-started ad-hoc ADO live run completes, the skill asks Add / Update / Skip. It uses the exact resolved node list to produce one metadata profile per selected test. Saving metadata, entering/updating values in the endpoint group, and adding project membership are separately reviewed changes. You can do all three manually without Copilot or any prior run. A completed failed test stays failed; a saved profile must never be described as passing merely because configuration succeeded.

## Optional master

Register tests-projects-master.yml only if you want one Run button for several project pipelines. Its non-secret definition variable `SAMPLE_PROJECT_PIPELINES_JSON` is an array of objects with `DefinitionId` and `SourceBranch` (for example `refs/heads/your-pushed-branch`). Only endpoint wrapper definitions are accepted; duplicates and two definitions pointing at the same endpoint wrapper are rejected before any queues. It forwards no test profiles, endpoints, or environment values: those stay with the endpoint pipelines.

Give the master's project-scoped Build Service identity View build pipeline, View builds, and Queue builds on the endpoint definitions, not edit permission. All target builds are queued before polling, subject to agent capacity. Unknown/failed/canceled results or timeouts fail the master and appear in its summary. No queue POST retries or automatic child cancellations occur; inspect ADO before retrying an ambiguous failure. Endpoint pipelines can always be run independently.

## References

- [ADO Library variable groups and authorization](https://learn.microsoft.com/azure/devops/pipelines/library/variable-groups?view=azure-devops)
- [Variable group update API](https://learn.microsoft.com/rest/api/azure/devops/distributedtask/variablegroups/update?view=azure-devops-rest-7.1)
- [Secret variable environment mapping](https://learn.microsoft.com/azure/devops/pipelines/process/set-secret-variables?view=azure-devops)
- [Template parameters versus runtime variable availability](https://learn.microsoft.com/azure/devops/pipelines/process/template-expressions?view=azure-devops)
