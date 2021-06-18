# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import functools
from devtools_testutils import PowerShellPreparer


AttestationPreparer = functools.partial(
            PowerShellPreparer, "attestation",
#            attestation_azure_authority_host='xxx',
#            attestation_resource_group='yyyy',
#            attestation_subscription_id='xxx',
#            attestation_environment='AzureCloud',
            attestation_policy_signing_key0='keyvalue',
            attestation_policy_signing_key1='keyvalue',
            attestation_policy_signing_key2='keyvalue',
            attestation_policy_signing_certificate0='more junk',
            attestation_policy_signing_certificate1='more junk',
            attestation_policy_signing_certificate2='more junk',
            attestation_serialized_policy_signing_key0="junk",
            attestation_serialized_policy_signing_key1="junk",
            attestation_serialized_policy_signing_key2="junk",
            attestation_serialized_isolated_signing_key='yyyy',
            attestation_isolated_signing_key='xxxx',
            attestation_isolated_signing_certificate='xxxx',
            attestation_service_management_url='https://management.core.windows.net/',
            attestation_location_short_name='wus', # Note: This must match the short name in the fake resources.
            attestation_client_id='xxxx',
            attestation_client_secret='secret',
            attestation_tenant_id='tenant',
            attestation_isolated_url='https://fakeresource.wus.attest.azure.net',
            attestation_aad_url='https://fakeresource.wus.attest.azure.net',
#            attestation_resource_manager_url='https://resourcemanager/zzz'
        )
