# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. A managed HSM (https://docs.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli)
#
# 2. azure-keyvault-administration and azure-identity libraries (pip install these)
#
# 3. Set environment variable MANAGED_HSM_URL with the URL of your managed HSM and AZURE_CLIENT_ID with the ID of a
#    service principal
#    
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates role definition and assignment operations for Managed HSM
#
# 1. List existing role definitions (list_role_definitions)
#
# 2. Create a role definition (set_role_definition)
#
# 3. Update a role definition (set_role_definition)
#
# 4. Get a role definition (get_role_definition)
#
# 5. List existing role assignments (list_role_assignments)
#
# 6. Create a role assignment (create_role_assignment)
#
# 7. Get a role assignment (get_role_assignment)
#
# 8. Delete a role assignment (delete_role_assignment)
#
# 9. Delete a role definition (delete_role_definition)
# ----------------------------------------------------------------------------------------------------------

# Instantiate an access control client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
# [START create_an_access_control_client]
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient

MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]
credential = DefaultAzureCredential()
client = KeyVaultAccessControlClient(vault_url=MANAGED_HSM_URL, credential=credential)
# [END create_an_access_control_client]

# Let's first see what role definitions are defined in the Managed HSM at the global scope.
print("\n.. List existing role definitions")
# [START list_role_definitions]
from azure.keyvault.administration import KeyVaultRoleScope

role_definitions = client.list_role_definitions(scope=KeyVaultRoleScope.GLOBAL)
for definition in role_definitions:
    print(f"Role name: {definition.role_name}; Role definition name: {definition.name}")
# [START list_role_definitions]

# Let's create a custom role definition. This role permits creating keys in a Managed HSM.
# We'll provide a friendly role name and let a unique role definition name (a UUID) be generated for us.
print("\n.. Create a role definition")
# [START create_a_role_definition]
from azure.keyvault.administration import KeyVaultDataAction, KeyVaultPermission, KeyVaultRoleScope

role_name = "customRole"
scope = KeyVaultRoleScope.GLOBAL
permissions = [KeyVaultPermission(data_actions=[KeyVaultDataAction.CREATE_HSM_KEY])]
role_definition = client.set_role_definition(scope=scope, role_name=role_name, permissions=permissions)
# [END create_a_role_definition]
print(f"Role definition '{role_definition.role_name}' created successfully.")

# Let's update our role definition to allow reading keys, but not allow creating keys.
# To update an existing definition, pass the name keyword argument to set_role_definition. This is the unique name
# of the role definition, which is stored in KeyVaultRoleDefinition.name.
print("\n.. Update a role definition")
# [START update_a_role_definition]
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
# [END update_a_role_definition]
print(f"Role definition '{updated_definition.role_name}' updated successfully.")

# We can now fetch the created definition to verify that it was created as expected.
print("\n.. Get a role definition")
# [START get_a_role_definition]
fetched_definition = client.get_role_definition(scope=scope, name=unique_definition_name)
# [END get_a_role_definition]
print(f"Role defintion '{fetched_definition.role_name}' fetched successfully.")

# Now let's list existing role assignments in the Managed HSM.
print("\n.. List role assignments")
# [START list_role_assignments]
from azure.keyvault.administration import KeyVaultRoleScope

role_assignments = client.list_role_assignments(KeyVaultRoleScope.GLOBAL)
for assignment in role_assignments:
    print(f"Role assignment name: {assignment.name}")
    print(f"Principal ID associated with this assignment: {assignment.properties.principal_id}")
# [END list_role_assignments]

# Now let's create a role assignment to apply our role definition to our service principal.
# Since we don't provide the name keyword argument to create_role_assignment, a unique role assignment name (a UUID)
# is generated for us.
print("\n.. Create a role assignment")
principal_id = os.environ["AZURE_CLIENT_ID"]
definition_id = updated_definition.id
# [START create_a_role_assignment]
from azure.keyvault.administration import KeyVaultRoleScope

scope = KeyVaultRoleScope.GLOBAL
role_assignment = client.create_role_assignment(scope=scope, definition_id=definition_id, principal_id=principal_id)
print(f"Role assignment {role_assignment.name} created successfully.")
# [END create_a_role_assignment]

# We can now fetch the role assignment to verify that it was created correctly.
print("\n.. Get a role assignment")
# [START get_a_role_assignment]
fetched_assignment = client.get_role_assignment(scope=scope, name=role_assignment.name)
print(f"Role assignment for principal {fetched_assignment.properties.principal_id} fetched successfully.")
# [END get_a_role_assignment]

# Let's delete the role assignment.
print("\n.. Delete a role assignment")
# [START delete_a_role_assignment]
client.delete_role_assignment(scope=scope, name=role_assignment.name)
# [END delete_a_role_assignment]
print("Role assignment deleted successfully.")

# Finally, let's delete the role definition as well.
print("\n.. Delete a role definition")
# [START delete_a_role_definition]
client.delete_role_definition(scope=scope, name=unique_definition_name)
# [END delete_a_role_definition]
print("Role definition deleted successfully.")
