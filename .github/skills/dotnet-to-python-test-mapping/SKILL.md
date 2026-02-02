---
name: Dotnet-to-Python test mapping
description: Map an Azure SDK for .NET test case to its equivalent Azure SDK for Python test (same service area), then implement or update the Python test under sdk/.../tests. Use when a user provides a .NET test file path/URL and asks for the corresponding Python test.
---

## Purpose
You help translate a single Azure SDK for .NET test scenario into the equivalent Azure SDK for Python test file under this repo.

## When to use
Use this skill when the user:
- links to a .NET test file (GitHub URL or local path), and
- asks to find/create/update the equivalent Python test in `C:/dev/azure-sdk-for-python/sdk/.../tests`.

## Inputs you should request (only if missing)
1. Confirmation that the .NET test is valid and can run successfully in **live mode**.
2. Confirmation that the .NET test's service area/folder maps to the proposed Python package folder.

## Workflow
1. **Identify the .NET test intent**
   - Read the test class and methods.
   - Summarize required resources, operations, and assertions.

2. **Locate the Python package & tests folder**
   - Find the matching Python management/data-plane package under `sdk/`.
   - Verify the target tests folder exists.

3. **Find an existing Python analogue**
   - Search by scenario keywords, operation names, resource types, and test naming patterns.
   - Prefer updating/extending an existing scenario test over creating a new one.

4. **Implement the Python test**
   - Follow the package's existing test patterns (fixtures, recorded tests, naming conventions).
   - Keep changes minimal and scoped to the scenario.

5. **Validate**
   - Run the package tests (or at minimum the new/updated test file) in the existing test harness.

## Example mapping
- .NET: `sdk/resources/Azure.ResourceManager.Resources/tests/Scenario/DataBoundaryOperationsTests.cs`
- Python target folder: `sdk/resources/azure-mgmt-resource/tests`
- Python analogue: `sdk/resources/azure-mgmt-resource/tests/test_data_boundary_scenario_test.py`
