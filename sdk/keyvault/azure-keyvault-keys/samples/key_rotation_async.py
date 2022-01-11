# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys import KeyRotationLifetimeAction, KeyRotationPolicyAction
from azure.keyvault.keys.aio import KeyClient

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-keys and azure-identity libraries (pip install these)
#
# 3. Set environment variable VAULT_URL with the URL of your key vault
#
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. To authenticate a service principal with
#    environment variables, set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID
#    (See https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys#authenticate-the-client)
#
# 5. Key rotation permissions for your service principal in your vault
#
# ----------------------------------------------------------------------------------------------------------
# Sample - creates and updates a key's automated rotation policy, and rotates a key on-demand
#
# 1. Create a new key rotation policy (update_key_rotation_policy)
#
# 2. Get a key's current rotation policy (get_key_rotation_policy)
#
# 3. Update a key's rotation policy (update_key_rotation_policy)
#
# 4. Rotate a key on-demand (rotate_key)
#
# 5. Delete a key (delete_key)
# ----------------------------------------------------------------------------------------------------------

async def run_sample():
    # Instantiate a key client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = KeyClient(vault_url=VAULT_URL, credential=credential)

    # First, create a key
    key_name = "rotation-sample-key"
    key = await client.create_rsa_key(key_name)
    print("\nCreated a key; new version is {}".format(key.properties.version))

    # Set the key's automated rotation policy to rotate the key two months after the key was created
    actions = [KeyRotationLifetimeAction(KeyRotationPolicyAction.ROTATE, time_after_create="P2M")]
    updated_policy = await client.update_key_rotation_policy(key_name, lifetime_actions=actions)

    # The created policy should only have one action
    assert len(updated_policy.lifetime_actions) == 1, "There should be exactly one rotation policy action"
    policy_action = updated_policy.lifetime_actions[0]
    print(
        "\nCreated a new key rotation policy: {} after {}".format(policy_action.action, policy_action.time_after_create)
    )

    # Get the key's current rotation policy
    current_policy = await client.get_key_rotation_policy(key_name)
    policy_action = current_policy.lifetime_actions[0]
    print("\nCurrent rotation policy: {} after {}".format(policy_action.action, policy_action.time_after_create))

    # Update the key's automated rotation policy to notify 30 days before the key expires
    new_actions = [KeyRotationLifetimeAction(KeyRotationPolicyAction.NOTIFY, time_before_expiry="P30D")]
    # You may also specify the duration after which the newly rotated key will expire
    # In this example, any new key versions will expire after 90 days
    new_policy = await client.update_key_rotation_policy(key_name, expires_in="P90D", lifetime_actions=new_actions)

    # The updated policy should only have one action
    assert len(new_policy.lifetime_actions) == 1, "There should be exactly one rotation policy action"
    policy_action = new_policy.lifetime_actions[0]
    print(
        "\nUpdated rotation policy: {} {} before expiry".format(policy_action.action, policy_action.time_before_expiry)
    )

    # Finally, you can rotate a key on-demand by creating a new version of the key
    rotated_key = await client.rotate_key(key_name)
    print("\nRotated the key on-demand; new version is {}".format(rotated_key.properties.version))

    # To clean up, delete the key
    await client.delete_key(key_name)
    print("\nDeleted the key")

    await credential.close()
    await client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sample())
    loop.close()
