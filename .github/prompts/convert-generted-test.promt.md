# Azure SDK Test Conversion Guide

## Goal
Convert generated test cases into complete, runnable test cases that pass live testing.

## Project Structure
This guide assumes the following package folder structure:
```
<package-root>/
├── generated_tests/          # Source: Generated test files
├── tests/                    # Target: Working test files
│   ├── conftest.py          # Test configuration
│   └── data/                # ARM templates (created if needed)
├── dev_requirements.txt     # Development dependencies
└── setup.py                # Package setup
```

## Key Principles
- **Source**: Generated test files are located in `generated_tests/`
- **Target**: All working test cases must be placed in `tests/`
- **Configuration**: `conftest.py` is located in the same `tests/` folder

---

## Phase 1: Environment Setup

### Step 1: Configure Environment Variables
1. **Check for `.env` file** in the repository root
2. **If missing**, create `.env` with the following content:
   ```env
   AZURE_TEST_RUN_LIVE=true
   AZURE_TEST_USE_CLI_AUTH=true
   AZURE_SUBSCRIPTION_ID=<YOUR_AZURE_SUBSCRIPTION_ID>
   AZURE_TENANT_ID=<YOUR_AZURE_TENANT_ID>
   ```
3. **Prompt user** to fill in actual values for subscription ID and tenant ID and wait for user to confirm until they complete.

### Step 2: Set Up Virtual Environment
1. **Check for `.venv` folder** in repository root
2. **If missing**, create virtual environment:
   ```bash
   python -m venv .venv
   ```
3. **Activate** the virtual environment:
   - **Windows**: `.venv\Scripts\activate`
   - **Linux/macOS**: `source .venv/bin/activate`
   
   > **Note**: Activation only needs to be done once per session

4. **Install Azure CLI** (if not present):
   ```bash
   pip install azure-cli
   ```
   > **Note**: Installation may take several minutes but is only required once

5. **Authenticate with Azure**:
   ```bash
   az login
   ```

### Step 3: Identify Source Test File
1. **Ask user** for the generated test file name in `generated_tests/`
2. **Create target test file** in `tests/` folder:
   - If no file named `{TEST_FILE}_test.py` exists, create it
   - Copy content from the generated test file

### Step 4: Prepare Test Infrastructure
1. **Remove skip decorators**: Delete `@pytest.mark.skip` from test methods

2. **Update dependencies**: Add `azure-mgmt-resource-bicep` to `dev_requirements.txt` if missing

3. **Add deployment helper** to `conftest.py` if the `deployment_resource` function doesn't exist:

   ```python
   # conftest.py
   import os
   import json
   from typing import Dict
   from azure.mgmt.resource.deployments import DeploymentsMgmtClient

   def deployment_resource(
       deployments_client: DeploymentsMgmtClient,
       template_name: str,
       resource_group_name: str,
       deployment_name: str,
       parameters: Dict[str, str]
   ) -> None:
       """Deploy an ARM template resource for testing purposes.
       
       This function loads an ARM template from the local data directory and deploys it
       to Azure using the provided deployment client. The deployment is performed in
       incremental mode.
       
       Args:
           deployments_client: The Azure Resource Manager deployments client used to
               create or update the deployment.
           template_name: The name of the ARM template file located in the 'data'
               subdirectory relative to this conftest.py file.
           resource_group_name: The name of the Azure resource group where the
               deployment will be created.
           deployment_name: The name to assign to the deployment operation.
           parameters: A dictionary of parameter names and values to pass to the
               ARM template during deployment.
       
       Returns:
           None: The function waits for the deployment to complete but does not
           return the deployment result.
       """
       template_path = os.path.join(os.path.dirname(__file__), "data", template_name)
       with open(template_path, 'r') as template_file:
           template = json.load(template_file)
       
       # Deploy the ARM template
       deployments_client.deployments.begin_create_or_update(
           resource_group_name=resource_group_name,
           deployment_name=deployment_name,
           parameters={
               "properties": {
                   "template": template,
                   "parameters": {k: {"value": v} for k, v in parameters.items()},
                   "mode": "Incremental"
               }
           }
       ).result()
   ```

4. **Install package and dependencies**:
   ```bash
   cd <package-root>  # Navigate to folder containing setup.py
   pip install -e .   # Install package in editable mode
   pip install -r dev_requirements.txt  # Install development dependencies
   ```

5. **Create data directory**: Create `tests/data/` folder if it doesn't exist

---

## Phase 2: Test Execution and Fixing

### Execution Strategy
- **Fix one test case at a time** to ensure focused debugging
- **Run each test individually** to isolate issues
- **Iteratively fix and rerun** until all tests pass

### Step 5: Test Execution Loop
For **each test case** in the target test file:

1. **Run the test**:
   ```bash
   pytest tests/{test_file_name}.py::{test_method_name} -v
   ```

2. **If test fails**:
   - Analyze error message
   - Apply appropriate fix (see `Adding ARM Template Resources` section if resources needed)
   - Rerun the same test case

3. **Repeat until test passes**, then move to next test case

### Adding ARM Template Resources

#### When Resource Creation is Needed:

**1. Add Deployment Client to Test Class**

If `deployments_client` is not defined in the test class `setup_method`:

```python
from azure.mgmt.resource.deployments import DeploymentsMgmtClient
from conftest import deployment_resource

class TestXxxOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        # ...existing setup code...
        self.deployments_client = self.create_mgmt_client(DeploymentsMgmtClient)
```

**2. Create ARM Template File**

Create an ARM template file under `tests/data/` with a name matching the test case (e.g., `test_xxx.json`)

**3. Update Test Method**

Modify the test case to deploy required resources before testing:

```python
class TestXxxOperations(AzureMgmtRecordedTestCase):

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_xxx(self, resource_group):
        # Define resource names
        deployment_name = "networkManagerDeployment"
        network_manager_name = "testNetworkManager"
        network_group_name = "testNetworkGroup"
        security_config_name = "testSecurityConfig"
        
        # Deploy the ARM template to create prerequisite resources
        deployment_resource(
            deployments_client=self.deployments_client,
            resource_group_name=resource_group.name,
            deployment_name=deployment_name,
            template_name="test_xxx.json",
            parameters={
                "networkManagerName": network_manager_name,
                "networkGroupName": network_group_name,
                "securityConfigurationName": security_config_name,
            }
        )
        
        # ...rest of test logic...
```

> **Important**: 
- Ensure parameter keys in the `parameters` dictionary exactly match the variable names expected by your ARM template file.
- Run command in virtual environment
- Follow this guideline Step by Step.
- ONLY change according to error message for live test result.




