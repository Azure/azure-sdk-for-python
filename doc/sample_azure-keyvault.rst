KeyVault
========

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the client
-----------------

The following code creates an instance of the client.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on handling Azure Active Directory authentication with the Python SDK, and creating a ``Credentials`` instance.

.. important:: You must specific `resource="https://vault.azure.net"` while authenticating to get a valid token

.. code:: python

    from azure.keyvault import KeyVaultClient
    from azure.common.credentials import UserPassCredentials
    
    # See above for details on creating different types of AAD credentials
    credentials = UserPassCredentials(
        'user@domain.com',  # Your user
        'my_password',      # Your password
        resource="https://vault.azure.net"
    )

    client = KeyVaultClient(
        credentials
    )

Access policies
---------------

Some operations require the correct access policies for your credentials.

If you get an "Unauthorized" error, please add the correct access policies 
to this credentials using the Azure Portal, the Azure CLI or the :doc:`Key Vault Management SDK itself <sample_azure-mgmt-keyvault>`

Example
-------

.. code:: python

    # Create a key
    key_bundle = client.create_key(KEY_VAULT_URI, 'FirstKey', 'RSA')
    key_id = key_vault_id.parse_key_id(key_bundle.key.kid)

    # Update a key without version
    client.update_key(key_id.base_id, key_attributes={'enabled': False})

    # Update a key with version
    client.update_key(key_id.id, key_attributes={'enabled': False})

    # Delete my key
    client.delete_key(KEY_VAULT_URI, 'FirstKey')

    # Create a secret
    secret_bundle = client.set_secret(KEY_VAULT_URI, 'FirstSecret', 'Hush, that is secret!!')
    secret_id = key_vault_id.parse_secret_id(secret_bundle.id)

    # Update a secret without version
    client.update_key(secret_id.base_id, secret_attributes={'enabled': False})

    # Update a secret with version
    client.update_key(secret_id.id, secret_attributes={'enabled': False})

    # Delete my secret
    client.delete_secret(KEY_VAULT_URI, 'FirstSecret')
