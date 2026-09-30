# azure-search-documents samples

Samples run live against a search service. Create `Set-LiveSampleEnvironment.ps1` from the release resources to set the env vars the samples read, keeping secrets out of it. Run commands from `sdk/search/azure-search-documents/` using the `venv` alias from `SKILL.md`:

```powershell
cd sdk/search/azure-search-documents
. .\.github\skills\azure-search-documents\scripts\Set-LiveSampleEnvironment.ps1
venv python samples/sample_knowledge_source_file_preview.py
```

## Adding new samples

This checklist is mandatory for every sample change. Do not add or update samples without checking each item below.

1. Gather the three release inputs first: the sample requirements, `.http` calls, and the resources to run against. Ask before editing if any is missing or ambiguous.
2. Name the file after the scenario from the requirements: `sample_<scenario>[_preview][_async].py`.
3. Build the file body: a DESCRIPTION/USAGE docstring, `run_tag`-based resource names so reruns don't collide, and the demonstrated calls and their SDK imports wrapped in `# [START <name>]` / `# [END <name>]` tags with id = file name.
4. Mirror each scenario's `.http` calls as the source of truth for the SDK flow: same operations (one SDK method per verb + route), call order, parameters, body fields, headers, and options, using SDK models instead of raw JSON; only swap in hotel data. If a starter value fails live, change only that value, not the call shape.
5. Keep the full SDK flow visible inside the tags, down to credential and client construction; push setup and cleanup into `sample_utils.py` helpers. Helper-only data may use compact dicts; the demonstrated scenario may not.
6. Mirror each sync sample in async; only async clients, `async with`, `await`, iteration, and cleanup differ.
