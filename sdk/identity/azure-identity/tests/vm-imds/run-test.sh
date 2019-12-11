#!/bin/bash

set -e

set -x

cd azure-sdk-for-python/sdk/identity/azure-identity/tests/managed-identity-live

AZURE_IDENTITY_TEST_VAULT_URL=https://chlowe.vault.azure.net $1 -m pytest -vrs --log-level=DEBUG
