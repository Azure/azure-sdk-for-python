# Test Azure Identity in Azure VM

## Prerequisite tools
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest)

## Azure resources
This test requires instances of these Azure resources:
- Azure Key Vault
- Azure Managed Identity
  - with secrets/set and secrets/delete permission for the Key Vault
- Azure Virtual Machine with system-assigned identity
- Azure Virtual Machine with user-assigned identity
  - don't use the same VM twice

The rest of this section is a walkthrough of deploying these resources.

## Setup

### Set environment variables to simplify copy-pasting
- RESOURCE_GROUP
  - name of an Azure resource group
  - must be unique in the Azure subscription
  - e.g. 'identity-test-rg'
- VM_NAME_SYSTEM_ASSIGNED
  - name of an Azure Virtual machine with a system-assigned identity
  - must be unique in the resource group
  - e.g. 'identity-test-vm-system'
- VM_NAME_USER_ASSIGNED
  - name of an Azure Virtual machine with a user-assigned identity
  - must be unique in the resource group
  - e.g. 'identity-test-vm-user'
- MANAGED_IDENTITY_NAME
  - name of the user-assigned identity
  - 3-128 alphanumeric characters
  - must be unique in the resource group
- KEY_VAULT_NAME
  - 3-24 alphanumeric characters
  - must begin with a letter
  - must be globally unique

### Create resource group
```sh
az group create -n $RESOURCE_GROUP --location westus2
```

### Create managed identity
Create the identity:
```sh
az identity create \
    -n $MANAGED_IDENTITY_NAME \
    -g $RESOURCE_GROUP \
    -l westus2
```

### Create virtual machines
With system-assigned identity:
```sh
az vm create \
    -n $VM_NAME_SYSTEM_ASSIGNED \
    -g $RESOURCE_GROUP \
    --image Canonical:0001-com-ubuntu-server-focal:20_04-lts-gen2:latest \
    --assign-identity \
    --size Standard_DS1_v2 \
    --generate-ssh-keys
```

With user-assigned identity:
```sh
az vm create \
    -n $VM_NAME_USER_ASSIGNED \
    -g $RESOURCE_GROUP \
    --image Canonical:0001-com-ubuntu-server-focal:20_04-lts-gen2:latest \
    --assign-identity $(az identity show -g $RESOURCE_GROUP -n $MANAGED_IDENTITY_NAME -o tsv --query id) \
    --size Standard_DS1_v2 \
    --generate-ssh-keys
```

Note: If an error occurs like: `'Following SKUs have failed for Capacity Restrictions: Standard_DS1_v2' is currently not available in location 'westus2'`, try again with a different zone by specifying `--zone 2` or `--zone 3`.

### Create a key vault:
```sh
az keyvault create -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --sku standard
```

Allow the VM with system-assigned identity to access the key vault's secrets:
```sh
az keyvault set-policy -n $KEY_VAULT_NAME \
    --object-id $(az vm show -n $VM_NAME_SYSTEM_ASSIGNED -g $RESOURCE_GROUP --query identity.principalId -o tsv) \
    --secret-permissions list
```

Do the same for the user-assigned identity:
```sh
az keyvault set-policy -n $KEY_VAULT_NAME \
    --object-id $(az identity show -g $RESOURCE_GROUP -n $MANAGED_IDENTITY_NAME --query principalId -o tsv) \
    --secret-permissions list
```

## Install dependencies

### Gather VM IDs
```sh
export VM_ID_SYSTEM_ASSIGNED=$(az vm show -g $RESOURCE_GROUP -n $VM_NAME_SYSTEM_ASSIGNED -o tsv --query id) \
       VM_ID_USER_ASSIGNED=$(az vm show -g $RESOURCE_GROUP -n $VM_NAME_USER_ASSIGNED -o tsv --query id) && \
export VM_IDS="$VM_ID_SYSTEM_ASSIGNED $VM_ID_USER_ASSIGNED"
```

### Install prerequisites
```sh
echo -e `az vm run-command invoke \
    --ids $VM_IDS \
    --command-id RunShellScript \
    --scripts "sudo apt update && sudo apt install python3-pip -y --no-install-recommends && \
               git clone https://github.com/Azure/azure-sdk-for-python.git --depth 1 --single-branch --branch main /sdk && \
               cd /sdk/sdk/identity/azure-identity/tests/managed-identity-live && \
               pip3 install setuptools wheel && \
               pip3 install -r requirements.txt"`
```

## Run tests
Do this for each VM, that is to say, once passing `--ids $VM_ID_SYSTEM_ASSIGNED` and again
passing `--ids $VM_ID_USER_ASSIGNED`:

```sh
echo -e `az vm run-command invoke \
    --ids $VM_ID_SYSTEM_ASSIGNED \
    --command-id RunShellScript \
    --scripts "cd /sdk/sdk/identity/azure-identity/tests/managed-identity-live && \
               export AZURE_IDENTITY_TEST_VAULT_URL=https://$KEY_VAULT_NAME.vault.azure.net && \
               export AZURE_TEST_RUN_LIVE=true && \
               export AZURE_SKIP_LIVE_RECORDING=true && \
               python3 -m pytest -v --log-level=DEBUG"`
```

Successful test output looks like this:
```
============================= test session starts ==============================
platform linux -- Python 3.8.10, pytest-7.2.0, pluggy-1.0.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /sdk, configfile: setup.cfg
plugins: asyncio-0.20.1, cov-4.0.0
asyncio: mode=strict
collecting ... collected 4 items

test_cloud_shell.py::test_cloud_shell_live SKIPPED (Cloud Shell MSI ...)  [ 25%]
test_cloud_shell_async.py::test_cloud_shell_live SKIPPED (Cloud Shell...) [ 50%]
test_managed_identity_live.py::test_managed_identity_live PASSED          [ 75%]
test_managed_identity_live_async.py::test_managed_identity_live PASSED    [100%]

========================= 2 passed, 2 skipped in 0.54s =========================
```
`test_managed_identity_live` must pass. Other tests may be skipped. No test may fail.

## Delete Azure resources
```sh
az group delete -n $RESOURCE_GROUP -y --no-wait
```
