
import unittest
from devtools_testutils import AzureTestCase, ResourceGroupPreparer, PowerShellPreparer
import functools
import json
import cryptography
import base64
from azure.security.attestation.v2020_10_01 import AttestationClient

shared_uks_base_uri='https://shareduks.uks.test.attest.azure.net'

AttestationPreparer = functools.partial(
    PowerShellPreparer, 
    "attestation",
    serializedPolicySigningKey1 = "junk",
    policySigningCertificate0='more junk',
    ATTESTATION_AZURE_AUTHORITY_HOST='xxx',
    ATTESTATION_RESOURCE_GROUP='yyyy',
    policySigningKey0='keyvalue',
    policySigningCertificate1='xxx',
    ATTESTATION_SUBSCRIPTION_ID='xxx',
    isolatedSigningKey='xxxx',
    serializedIsolatedSigningKey='yyyy',
    serializedPolicySigningKey0='xxxx',
    locationShortName='xxx',
    ATTESTATION_ENVIRONMENT='AzureCloud',
    policySigningKey2='xxxx',
    isolatedSIgningCertificate='xxxx',
    serializedPolicySigningKey2='xxx',
    ATTESTATION_SERVICE_MANAGEMENT_URL='xxx',
    ATTESTATION_LOCATION='xxxx',
    policySigningKey1='xxxx',
    ATTESTATION_CLIENT_ID='xxxx',
    ATTESTATION_CLIENT_SECRET='secret',
    ATTESTATION_TENANT_ID='tenant',
    policySigningCertificate2='cert2',
    ISOLATED_ATTESTATION_URL='xxx',
    AAD_ATTESTATION_URL='yyy',
    ATTESTATION_RESOURCE_MANAGER_URL='resourcemanager'
)

class UnitTestUtils(AttestationPreparer):
    def __init__(self):
        pass

    @AttestationClient
    @staticmethod
    def AadClient():
        """
        docstring
        """
        preparer = AttestationPreparer
        credential = preparer.get_credential(AttestationClient)
        baseUri = preparer.AAD_ATTESTATION_URL
        attest_client = preparer.create_client_from_credential(AttestationClient, credential=credential, tenant_base_url=baseUri)
        return attest_client

    @AttestationClient
    @staticmethod
    def IsolatedClient():
        """
        docstring
        """
        preparer = AttestationPreparer
        credential = preparer.get_credential(AttestationClient)
        baseUri = preparer.ISOLATED_ATTESTATION_URL
        attest_client = preparer.create_client_from_credential(AttestationClient, credential=credential, tenant_base_url=baseUri)
        return attest_client

    @AttestationClient
    @staticmethod
    def SharedClient():
        """
        docstring
        """
        preparer = AttestationPreparer
        credential = preparer.get_credential(AttestationClient)
        attest_client = preparer.create_client_from_credential(AttestationClient, credential=credential, tenant_base_url=shared_uks_base_uri)
        return attest_client
