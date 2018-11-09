import uuid
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer, StorageAccountPreparer
from keyvault_preparer import KeyVaultPreparer
from keyvault_testcase import KeyvaultTestCase
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters
from azure.keyvault.models import StorageAccountAttributes


class KeyVaultSecretTest(KeyvaultTestCase):

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='kvsa1')
    @KeyVaultPreparer()
    def test_e2e(self, vault, storage_account, resource_group, **kwargs):
        # find the role definition for "Storage Account Key Operator Service Role"
        filter_str = 'roleName eq \'Storage Account Key Operator Service Role\''
        authorization_mgmt_client = self.create_mgmt_client(AuthorizationManagementClient)
        role_id = list(authorization_mgmt_client.role_definitions.list(scope='/', filter=filter_str))[0].id

        # create a role assignment granting the key vault service principal this role
        role_params = RoleAssignmentCreateParameters(role_definition_id=role_id,
                                                     # the Azure Key Vault service id
                                                     principal_id='93c27d83-f79b-4cb2-8dd4-4aa716542e74')

        if not self.is_live:
            sa_id = '{}/providers/Microsoft.Storage/storageAccounts/{}'.format(resource_group.id, storage_account.name)
        else:
            sa_id = storage_account.id

        authorization_mgmt_client.role_assignments.create(scope=sa_id,
                                                          role_assignment_name='d7607bd3-a467-4a14-ab5f-f4b016ffbfff',
                                                          parameters=role_params)


        # add the storage account to the vault using the users KeyVaultClient
        attributes = StorageAccountAttributes(enabled=True)
        self.client.set_storage_account(vault_base_url=vault.properties.vault_uri,
                                        storage_account_name=storage_account.name,
                                        resource_id=sa_id,
                                        active_key_name='key1',
                                        auto_regenerate_key=True,
                                        regeneration_period='P30D',
                                        storage_account_attributes=attributes)

        # update active key for the storage account
        self.client.update_storage_account(vault_base_url=vault.properties.vault_uri,
                                           storage_account_name=storage_account.name,
                                           active_key_name='key2')

        self.client.regenerate_storage_account_key(vault_base_url=vault.properties.vault_uri,
                                                   storage_account_name=storage_account.name,
                                                   key_name='key1')

        self.create_account_sas_definition(storage_account.name, vault.properties.vault_uri)

        self.create_blob_sas_defintion(storage_account.name, vault.properties.vault_uri)

        self.get_sas_definitions(storage_account.name, vault.properties.vault_uri)

        self.client.delete_storage_account(vault_base_url=vault.properties.vault_uri,
                                           storage_account_name=storage_account.name)


    def create_account_sas_definition(self, storage_account_name, vault_url):
        """
        Creates an account sas definition, to manage storage account and its entities.
        """
        from azure.storage.common import SharedAccessSignature, CloudStorageAccount
        from azure.keyvault.models import SasTokenType, SasDefinitionAttributes
        from azure.keyvault import SecretId

        # To create an account sas definition in the vault we must first create the template. The
        # template_uri for an account sas definition is the intended account sas token signed with an arbitrary key.
        # Use the SharedAccessSignature class from azure.storage.common to create a account sas token
        sas = SharedAccessSignature(account_name=storage_account_name,
                                    # don't sign the template with the storage account key use key 00000000
                                    account_key='00000000')
        account_sas_template = sas.generate_account(services='bfqt',  # all services blob, file, queue and table
                                                    resource_types='sco',  # all resources service, template, object
                                                    permission='acdlpruw',
                                                    # all permissions add, create, list, process, read, update, write
                                                    expiry='2020-01-01')  # expiry will be ignored and validity period will determine token expiry

        # use the created template to create a sas definition in the vault
        attributes = SasDefinitionAttributes(enabled=True)
        sas_def = self.client.set_sas_definition(vault_base_url=vault_url,
                                                          storage_account_name=storage_account_name,
                                                          sas_definition_name='acctall',
                                                          template_uri=account_sas_template,
                                                          sas_type=SasTokenType.account,
                                                          validity_period='PT2H',
                                                          sas_definition_attributes=attributes)

        # When the sas definition is created a corresponding managed secret is also created in the vault, the. This
        # secret is used to provision sas tokens according to the sas definition.  Users retrieve the sas token
        # via the get_secret method.

        # get the secret id from the returned SasDefinitionBundle
        sas_secret_id = SecretId(uri=sas_def.secret_id)
        # call get_secret and the value of the returned SecretBundle will be a newly issued sas token
        acct_sas_token = self.client.get_secret(vault_base_url=sas_secret_id.vault,
                                                         secret_name=sas_secret_id.name,
                                                         secret_version=sas_secret_id.version).value

        # create the cloud storage account object
        cloud_storage_account = CloudStorageAccount(account_name=storage_account_name,
                                                    sas_token=acct_sas_token)

        # create a blob with the account sas token
        blob_service = cloud_storage_account.create_block_blob_service()
        blob_service.create_container('blobcontainer')
        blob_service.create_blob_from_text(container_name='blobcontainer',
                                           blob_name='blob1',
                                           text=u'test blob1 data')

    def create_blob_sas_defintion(self, storage_account_name, vault_url):
        """
        Creates a service SAS definition with access to a blob container.
        """

        from azure.storage.blob import BlockBlobService, ContainerPermissions
        from azure.keyvault.models import SasTokenType, SasDefinitionAttributes
        from azure.keyvault import SecretId

        # create the blob sas definition template
        # the sas template uri for service sas definitions contains the storage entity url with the template token
        # this sample demonstrates constructing the template uri for a blob container, but a similar approach can
        # be used for all other storage service, i.e. File, Queue, Table

        # create a template sas token for the container
        service = BlockBlobService(account_name=storage_account_name,
                                   # don't sign the template with the storage account key use key 00000000
                                   account_key='00000000')
        permissions = ContainerPermissions(read=True, write=True, delete=True, list=True)
        temp_token = service.generate_container_shared_access_signature(container_name='blobcontainer',
                                                                        permission=permissions,
                                                                        expiry='2020-01-01')

        # use the BlockBlobService to construct the template uri for the container sas definition
        blob_sas_template_uri = service.make_container_url(container_name='blobcontainer',
                                                           protocol='https',
                                                           sas_token=temp_token)
        # create the sas definition in the vault
        attributes = SasDefinitionAttributes(enabled=True)
        blob_sas_def = self.client.set_sas_definition(vault_base_url=vault_url,
                                                               storage_account_name=storage_account_name,
                                                               sas_definition_name='blobcontall',
                                                               template_uri=blob_sas_template_uri,
                                                               sas_type=SasTokenType.service,
                                                               validity_period='PT2H',
                                                               sas_definition_attributes=attributes)

        # use the sas definition to provision a sas token and use it to  create a BlockBlobClient
        # which can interact with blobs in the container

        # get the secret_id of the container sas definition and get the token from the vault as a secret
        sas_secret_id = SecretId(uri=blob_sas_def.secret_id)
        blob_sas_token = self.client.get_secret(vault_base_url=sas_secret_id.vault,
                                                         secret_name=sas_secret_id.name,
                                                         secret_version=sas_secret_id.version).value
        service = BlockBlobService(account_name=storage_account_name,
                                   sas_token=blob_sas_token)
        service.create_blob_from_text(container_name='blobcontainer',
                                      blob_name='blob2',
                                      text=u'test blob2 data')
        blobs = list(service.list_blobs(container_name='blobcontainer'))

        for blob in blobs:
            service.delete_blob(container_name='blobcontainer',
                                blob_name=blob.name)

    def get_sas_definitions(self, storage_account_name, vault_url):
        """
        List the sas definitions for the storage account, and get each.
        """
        from azure.keyvault import StorageSasDefinitionId

        # list the sas definitions for the storage account
        print('list and get sas definitions for the managed storage account')
        sas_defs = list(self.client.get_sas_definitions(vault_base_url=vault_url,
                                                                 storage_account_name=storage_account_name,
                                                                 maxresults=5))

        # for each sas definition parse the id and get the SasDefinitionBundle
        for s in sas_defs:
            sas_def_id = StorageSasDefinitionId(uri=s.id)
            sas_def = self.client.get_sas_definition(vault_base_url=sas_def_id.vault,
                                                              storage_account_name=sas_def_id.account_name,
                                                              sas_definition_name=sas_def_id.sas_definition)
            print(sas_def_id.sas_definition, sas_def.template_uri)

