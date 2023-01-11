from azure.mgmt.msi import ManagedServiceIdentityClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.keyvault.keys import KeyClient


def create_managed_identity(
    msi_client: ManagedServiceIdentityClient, msi_name, rg_name, location
):
    msi = msi_client.user_assigned_identities.create_or_update(
        rg_name, msi_name, {"location": location}
    )
    return msi


def create_key_vault(
    kv_client: KeyVaultManagementClient,
    akv_name,
    rg_name,
    location,
    msi,
    tenant_id,
    object_id,
):
    resource_poller = kv_client.vaults.begin_create_or_update(
        rg_name,
        akv_name,
        {
            "location": location,
            "properties": {
                "sku": {"name": "standard", "family": "A"},
                "tenant_id": tenant_id,
                "enable_soft_delete": True,
                "enable_purge_protection": True,
                "enabled_for_deployment": True,
                "enabled_for_disk_encryption": True,
                "enabled_for_template_deployment": True,
                "access_policies": [
                    {
                        "tenant_id": tenant_id,
                        "object_id": object_id,
                        "permissions": {"keys": ["all"], "secrets": ["all"]},
                    },
                    {
                        "tenant_id": msi.tenant_id,
                        "object_id": msi.principal_id,
                        "permissions": {"keys": ["all"]},
                    },
                ],
            },
        },
    )
    akv = resource_poller.result()
    return akv


def create_key(akv, credential, key_name):
    key_client = KeyClient(akv.properties.vault_uri, credential)
    key = key_client.create_rsa_key(key_name)
    return key
