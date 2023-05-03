# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-keys and azure-identity libraries (pip install these)
#
# 3. Set environment variable VAULT_URL with the URL of your key vault
#    
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
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
# 5. Delete a key (begin_delete_key)
# ----------------------------------------------------------------------------------------------------------

# Instantiate a key client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = KeyClient(vault_url=VAULT_URL, credential=credential)

# First, create a key
key = client.create_rsa_key("rotation-sample-key")
print(f"\nCreated a key; new version is {key.properties.version}")

# [START update_a_rotation_policy]
from azure.keyvault.keys import KeyRotationLifetimeAction, KeyRotationPolicy, KeyRotationPolicyAction

# Here we set the key's automated rotation policy to rotate the key two months after the key was created.
# If you pass an empty KeyRotationPolicy() as the `policy` parameter, the rotation policy will be set to the
# default policy. Any keyword arguments will update specified properties of the policy.
actions = [KeyRotationLifetimeAction(KeyRotationPolicyAction.rotate, time_after_create="P2M")]
updated_policy = client.update_key_rotation_policy(
    "rotation-sample-key", policy=KeyRotationPolicy(), expires_in="P90D", lifetime_actions=actions
)
assert updated_policy.expires_in == "P90D"
# [END update_a_rotation_policy]

# The updated policy should have the specified lifetime action
policy_action = None
for i in range(len(updated_policy.lifetime_actions)):
    if updated_policy.lifetime_actions[i].action == KeyRotationPolicyAction.rotate:
        policy_action = updated_policy.lifetime_actions[i]
assert policy_action, "The specified action should exist in the key rotation policy"
assert policy_action.time_after_create == "P2M", "The action should have the specified time_after_create"
assert policy_action.time_before_expiry is None, "The action shouldn't have a time_before_expiry"
print(f"\nCreated a new key rotation policy: {policy_action.action} after {policy_action.time_after_create}")

# Get the key's current rotation policy
current_policy = client.get_key_rotation_policy("rotation-sample-key")
policy_action = None
for i in range(len(current_policy.lifetime_actions)):
    if current_policy.lifetime_actions[i].action == KeyRotationPolicyAction.rotate:
        policy_action = current_policy.lifetime_actions[i]
print(f"\nCurrent rotation policy: {policy_action.action} after {policy_action.time_after_create}")

# Update the key's automated rotation policy to notify 10 days before the key expires
new_actions = [KeyRotationLifetimeAction(KeyRotationPolicyAction.notify, time_before_expiry="P10D")]
# To preserve an existing rotation policy, pass in the existing policy as the `policy` parameter.
# Any property specified as a keyword argument will be overridden completely by the provided value.
# In this case, the rotate action we created earlier will be removed from the policy.
new_policy = client.update_key_rotation_policy("rotation-sample-key", current_policy, lifetime_actions=new_actions)
assert new_policy.expires_in == "P90D", "The key's expiry time should have been preserved"

# The updated policy should include the new notify action
notify_action = None
for i in range(len(new_policy.lifetime_actions)):
    if new_policy.lifetime_actions[i].action == KeyRotationPolicyAction.notify:
        notify_action = new_policy.lifetime_actions[i]

assert notify_action, "The specified action should exist in the key rotation policy"
assert notify_action.time_after_create is None, "The action shouldn't have a time_after_create"
assert notify_action.time_before_expiry == "P10D", "The action should have the specified time_before_expiry"
print(f"\nNew policy action: {notify_action.action} {notify_action.time_before_expiry} before expiry\n")

# Finally, you can rotate a key on-demand by creating a new version of the key
# [START rotate_key]
rotated_key = client.rotate_key("rotation-sample-key")
print(f"Rotated the key on-demand; new version is {rotated_key.properties.version}")
# [END rotate_key]

# To clean up, delete the key
client.begin_delete_key("rotation-sample-key")
print("\nDeleted the key")
