---
name: Dotnet-to-Python test mapping
description: Map an Azure SDK for .NET test case to its equivalent Azure SDK for Python test (same service area), then implement or update the Python test under sdk/.../tests. Use when a user provides a .NET test file path/URL and asks for the corresponding Python test.
---

## Purpose
You help translate a single Azure SDK for .NET test scenario into the equivalent Azure SDK for Python test file under this repo.

## When to use
Use this skill when the user:
- links to a .NET test file (GitHub URL or local path), and
- asks to find/create/update the equivalent Python test in Python SDK folder

## Inputs you should request (only if missing)
Only ask the user for extra inputs when you truly cannot derive them from repo search.
1. Confirmation that the .NET test is valid and can run successfully in **live mode**.
2. If user does not provide a Python SDK repo folder, otherwise infer the correct package and tests folder.

## Workflow
1. **Identify the .NET test intent**
   - Read the test class and methods.
   - Summarize required resources, operations, and assertions.

2. **Locate the Python package & tests folder**
   - If the user did not provide a specific Python SDK folder under `sdk/`, do NOT ask them to provide one by default.
   - Instead, infer it using the techniques in "How to map .NET -> Python package (best signal: HTTP path)".
   - Find the matching Python management/data-plane package under `sdk/`.
   - Verify the target tests folder exists; if it doesn’t, find the closest existing `tests` folder pattern in that package.

3. **Find an existing Python analogue**
   - Search by scenario keywords, operation names, resource types, and test naming patterns.
   - Prefer updating/extending an existing scenario test over creating a new one.

4. **Implement the Python test**
   - Follow the package's existing test patterns (fixtures, recorded tests, naming conventions).
   - Keep changes minimal and scoped to the scenario.

5. **Validate**
   - Run the package tests (or at minimum the new/updated test file) in the existing test harness.

## How to map .NET -> Python package (best signal: HTTP path)
The most reliable mapping between a generated .NET SDK folder and a generated Python SDK folder is the HTTP request path, because both SDKs are generated from the same source (Swagger/TypeSpec). That means the operations typically share the same REST paths.

### Steps
1. **Find the REST path in the .NET generated code**
   - Locate the generated collection/client method for the operation used in the test.
   - In Azure SDK for .NET generated code, the REST path is commonly surfaced as a `Request Path` annotation/comment (or an attribute nearby).
   - Example `Request Path` annotation:
     - https://github.com/Azure/azure-sdk-for-net/blob/a89fe22c07d5dd2303ff4cf45e726d3d16c57f5b/sdk/network/Azure.ResourceManager.Network/src/Generated/AdminRuleGroupCollection.cs#L58-L59

2. **Search for that path in this Python repo**
   - Take the path string (the part after the host, e.g. `/subscriptions/{subscriptionId}/...`).
   - Search the Python repo for the same path. Likely hits include:
     - Generated client operation files under `sdk/<service>/<package>/azure/mgmt/.../operations/` (mgmt-plane)
     - Generated REST/operation specs in the codegen output
     - Test recordings referencing the URL path
   - Once you find the matching Python package folder under `sdk/`, the target test folder is usually:
     - `sdk/<service>/<package>/tests` (data-plane patterns vary), or
     - `sdk/<service>/<package>/tests` / `sdk/<service>/<package>/tests/recordings` (mgmt-plane common)

3. **Confirm by quick sanity checks**
   - The Python package’s namespace should match the service (e.g., `azure.mgmt.network`).
   - The operations/classes should mention the same resource type names used in the .NET test.
   - Prefer the package that already has scenario tests and recordings for similar resources.

### Fallbacks (if the path search is noisy)
- Search by resource type segments in the path (e.g., `Microsoft.Network`, `adminRuleGroups`, `routeTables`).
- Search by operation name used in the .NET test and map to Python operations modules.
- Use service folder heuristics (`sdk/network/` vs `sdk/resources/`), then narrow to `azure-mgmt-*` packages.

## Example mapping
- .NET: `sdk/resources/Azure.ResourceManager.Resources/tests/Scenario/DataBoundaryOperationsTests.cs`
- Python target folder: `sdk/resources/azure-mgmt-resource/tests`
- Python analogue: `sdk/resources/azure-mgmt-resource/tests/test_data_boundary_scenario_test.py`
