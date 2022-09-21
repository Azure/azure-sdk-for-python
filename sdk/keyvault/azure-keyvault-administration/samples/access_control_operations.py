# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.keyvault.administration import (
    KeyVaultAccessControlClient,
    KeyVaultDataAction,
    KeyVaultPermission,
    KeyVaultRoleScope,
)
from azure.identity import DefaultAzureCredential

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. A managed HSM (https://docs.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli)
#
# 2. azure-keyvault-administration and azure-identity libraries (pip install these)
#
# 3. Set environment variable MANAGED_HSM_URL with the URL of your managed HSM
#    
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates role definition and assignment operations for Managed HSM
#
# 1. Create a role definition (set_role_definition)
#
# 2. Update a role definition (set_role_definition)
#
# 3. Create a role assignment (create_role_assignment)
#
# 4. Delete a role assignment (delete_role_assignment)
#
# 5. Delete a role definition (delete_role_definition)
# ----------------------------------------------------------------------------------------------------------

MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]

# Instantiate an access control client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
credential = DefaultAzureCredential()
client = KeyVaultAccessControlClient(vault_url=MANAGED_HSM_URL, credential=credential)

# Let's first create a custom role definition. This role permits creating keys in a Managed HSM.
# We'll provide a friendly role name, and let a unique role definition name (a GUID) be generated for us.
print("\n.. Create a role definition")
role_name = "customRole"
scope = KeyVaultRoleScope.GLOBAL
permissions = [KeyVaultPermission(data_actions=[KeyVaultDataAction.CREATE_HSM_KEY])]
role_definition = client.set_role_definition(scope=scope, role_name=role_name, permissions=permissions)
print("Role definition '{}' created successfully.".format(role_definition.role_name))

# Let's update our role definition to allow reading keys, but not allow creating keys.
# To update an existing definition, pass the name keyword argument to set_role_definition. This is the unique name
# of the role definition, which is stored in KeyVaultRoleDefinition.name.
print("\n.. Update a role definition")
new_permissions = [
    KeyVaultPermission(
        data_actions=[KeyVaultDataAction.READ_HSM_KEY],
        not_data_actions=[KeyVaultDataAction.CREATE_HSM_KEY]
    )
]
unique_definition_name = role_definition.name
updated_definition = client.set_role_definition(
    scope=scope, name=unique_definition_name, role_name=role_name, permissions=new_permissions
)
print("Role definition '{}' updated successfully.".format(updated_definition.role_name))

# Now let's create a role assignment to apply our role definition to our service principal.
# Since we don't provide the name keyword argument to create_role_definition, a unique role assignment name (a GUID)
# is generated for us.
print("\n.. Create a role assignment")
principal_id = os.environ["AZURE_CLIENT_ID"]
definition_id = updated_definition.id
role_assignment = client.create_role_assignment(scope=scope, definition_id=definition_id, principal_id=principal_id)
print("Role assignment created successfully.")

# Let's delete the role assignment.
print("\n.. Delete a role assignment")
client.delete_role_assignment(scope=scope, name=role_assignment.name)
print("Role assignment deleted successfully.")

# Finally, let's delete the role definition as well.
print("\n.. Delete a role definition")
client.delete_role_definition(scope=scope, name=definition_id)
print("Role definition deleted successfully.")
