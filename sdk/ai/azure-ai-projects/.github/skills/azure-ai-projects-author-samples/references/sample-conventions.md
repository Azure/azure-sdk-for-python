# azure-ai-projects sample conventions

Use nearby files as the final authority. Good anchors are [`sample_agent_basic.py`](../../../../samples/agents/sample_agent_basic.py), its [async mirror](../../../../samples/agents/sample_agent_basic_async.py), and the [skills CRUD pair](../../../../samples/skills/).

## Shape and naming

- Put `sample_<workflow>.py` beside related features and use `sample_<workflow>_async.py` for the async mirror.
- Start with the package copyright header and a module docstring containing `DESCRIPTION`, `USAGE`, install prerequisites, and every required/optional environment variable.
- Load `.env` with `python-dotenv`; read required values with `os.environ[...]` and optional values with `os.environ.get(...)`.
- Import sync credentials/client from `azure.identity` and `azure.ai.projects`; async variants come from their `.aio` namespaces. Import models from the public `azure.ai.projects.models` surface.
- Prefer one coherent workflow with useful progress/result output. Iterate pageable results with `for` or `async for`, and `await` every async service call.

## Lifetime and parity

Use credential and client context managers. When creating service resources, retain identifiers and clean them up in `finally` so partial failures do not leak resources. Sync and async samples should demonstrate the same scenario, parameters, output, and cleanup unless the API exists in only one client.

The sample executor imports the module and calls `main()` when present. A guarded sync `main()` and an `asyncio.run(main())` async entry point are both supported. Match the closest neighboring pair rather than restyling an existing sample unnecessarily.

## Updating existing samples

For a renamed/changed API, search every sample call site and update it in place. Preserve the scenario unless the old behavior no longer exists. Do not import `_operations`, `_models`, `_patch`, or other implementation modules to bypass the public surface.

Python samples intentionally include preview features; state preview status in the description and use the existing `.beta` access pattern when applicable.

## Recorded sample harness

[`test_samples.py`](../../../../tests/samples/test_samples.py) and [`test_samples_async.py`](../../../../tests/samples/test_samples_async.py) auto-discover many folders. Add unrecorded files to the appropriate `samples_to_skip` list with a specific reason. Whitelist-based `samples_to_test` blocks require explicit opt-in instead.

If a new folder needs output validation, also update [`llm_instructions.py`](../../../../tests/samples/llm_instructions.py) and its folder mapping. Add required sanitized environment defaults through the narrowest preparer and mapping helper; never put live values in source.
