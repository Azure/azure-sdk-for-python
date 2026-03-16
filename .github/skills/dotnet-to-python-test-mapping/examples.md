## Example prompt

"Help .NET SDK test case https://github.com/Azure/azure-sdk-for-net/blob/f77ff48fb510bd60ea8c2cfbb8d3fa301f5d4f54/sdk/resources/Azure.ResourceManager.Resources/tests/Scenario/DataBoundaryOperationsTests.cs to python test case under folder C:/dev/azure-sdk-for-python/sdk/resources/azure-mgmt-resource/tests"

## Expected behavior

1. Ask the user to confirm the .NET test passes in live mode.
2. Confirm the .NET folder maps to `sdk/resources/azure-mgmt-resource/tests`.
3. Locate the Python analogue (e.g., `test_data_boundary_scenario_test.py`).
4. Implement/update the Python test with minimal changes and run the relevant test command.
