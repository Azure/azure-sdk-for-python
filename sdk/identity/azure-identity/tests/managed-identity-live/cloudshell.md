# Testing azure-identity in Azure Cloud Shell

# Open Azure Cloud Shell
https://shell.azure.com/

# Create an Azure Key Vault

## set environment variables to simplify copy-pasting
- RESOURCE_GROUP
  - name of an Azure resource group
  - must be unique in the Azure subscription
  - e.g. 'cloudshell-identity-test'
- KEY_VAULT_NAME
  - 3-24 alphanumeric characters
  - must begin with a letter
  - must be globally unique

## create a resource group
```sh
az group create -n $RESOURCE_GROUP --location westus2
```

## create the Key Vault
```sh
az keyvault create -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --sku standard
```

The tests expect the vault's URI in an environment variable:
```sh
export AZURE_IDENTITY_TEST_VAULT_URL=$(az keyvault show -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --query properties.vaultUri | tr -d '"')
```

# Run the tests

## Acquire the latest code
This may take several minutes:
```sh
git clone https://github.com/azure/azure-sdk-for-python --single-branch --branch master --depth 1
```

## Change working directory
```sh
cd azure-sdk-for-python/sdk/identity/azure-identity
```


## Create virtual environments
The Azure SDK supports Python 2.7 and 3.5.3+. Python 2 and 3 should be installed
in your Cloud Shell. However, the Python 3 version may be less than 3.5.3. Check
this with `python3 -V`. If the version is less than 3.5.3, run tests with Python
2 only.

### Python 2.7
```sh
virtualenv -p python2 ~/venv2
```

### Python 3
If your shell has at least Python 3.5.3 available, create a virtual environment
for it:
```sh
virtualenv -p python3 ~/venv3
```

## For each virtual environment:

### Activate
For example:
```sh
source ~/venv2/bin/activate
```

### Install packages
```sh
pip install -r dev_requirements.txt .
```

### Run tests
```sh
pytest ./tests -vrs -m cloudshell
```

### Deactivate
```sh
deactivate
```

# Delete Azure resources
After running tests, delete the resources provisioned earlier:
```sh
az group delete -n $RESOURCE_GROUP -y --no-wait
```
