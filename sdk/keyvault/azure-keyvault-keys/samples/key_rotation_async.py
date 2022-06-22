# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys import KeyRotationLifetimeAction, KeyRotationPolicy, KeyRotationPolicyAction
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

    # Set the key's automated rotation policy to rotate the key two months after the key was created.
    # If you pass an empty KeyRotationPolicy() as the `policy` parameter, the rotation policy will be set to the
    # default policy. Any keyword arguments will update specified properties of the policy.
    actions = [KeyRotationLifetimeAction(KeyRotationPolicyAction.rotate, time_after_create="P2M")]
    updated_policy = await client.update_key_rotation_policy(
        key_name, KeyRotationPolicy(), expires_in="P90D", lifetime_actions=actions
    )
    assert updated_policy.expires_in == "P90D"

    # The updated policy should have the specified lifetime action
    policy_action = None
    for i in range(len(updated_policy.lifetime_actions)):
        if updated_policy.lifetime_actions[i].action == KeyRotationPolicyAction.rotate:
            policy_action = updated_policy.lifetime_actions[i]
    assert policy_action, "The specified action should exist in the key rotation policy"
    assert policy_action.time_after_create == "P2M", "The action should have the specified time_after_create"
    assert policy_action.time_before_expiry is None, "The action shouldn't have a time_before_expiry"
    print(
        "\nCreated a new key rotation policy: {} after {}".format(policy_action.action, policy_action.time_after_create)
    )

    # Get the key's current rotation policy
    current_policy = await client.get_key_rotation_policy(key_name)
    policy_action = None
    for i in range(len(current_policy.lifetime_actions)):
        if current_policy.lifetime_actions[i].action == KeyRotationPolicyAction.rotate:
            policy_action = current_policy.lifetime_actions[i]
    print("\nCurrent rotation policy: {} after {}".format(policy_action.action, policy_action.time_after_create))

    # Update the key's automated rotation policy to notify 10 days before the key expires
    new_actions = [KeyRotationLifetimeAction(KeyRotationPolicyAction.notify, time_before_expiry="P10D")]
    # To preserve an existing rotation policy, pass in the existing policy as the `policy` parameter.
    # Any property specified as a keyword argument will be overridden completely by the provided value.
    # In this case, the rotate action we created earlier will be removed from the policy.
    new_policy = await client.update_key_rotation_policy(key_name, current_policy, lifetime_actions=new_actions)
    assert new_policy.expires_in == "P90D", "The key's expiry time should have been preserved"

    # The updated policy should include the new notify action
    notify_action = None
    for i in range(len(new_policy.lifetime_actions)):
        if new_policy.lifetime_actions[i].action == KeyRotationPolicyAction.notify:
            notify_action = new_policy.lifetime_actions[i]

    assert notify_action, "The specified action should exist in the key rotation policy"
    assert notify_action.time_after_create is None, "The action shouldn't have a time_after_create"
    assert notify_action.time_before_expiry == "P10D", "The action should have the specified time_before_expiry"
    print("\nNew policy action: {} {} before expiry".format(notify_action.action, notify_action.time_before_expiry))

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
