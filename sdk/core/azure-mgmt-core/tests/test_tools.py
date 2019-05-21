#--------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. 
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#--------------------------------------------------------------------------

import unittest
import json
try:
    from unittest import mock
except ImportError:
    import mock

import requests
import httpretty

from msrestazure.azure_configuration import AzureConfiguration
from msrestazure.tools import parse_resource_id, is_valid_resource_id, resource_id, is_valid_resource_name

class TestTools(unittest.TestCase):

    @httpretty.activate
    @mock.patch('time.sleep', return_value=None)
    def test_register_rp_hook(self, time_sleep):
        """Protocol:
        - We call the provider and get a 409 provider error
        - Now we POST register provider and get "Registering"
        - Now we GET register provider and get "Registered"
        - We call again the first endpoint and this time this succeed
        """

        provider_url = ("https://management.azure.com/"
                        "subscriptions/12345678-9abc-def0-0000-000000000000/"
                        "resourceGroups/clitest.rg000001/"
                        "providers/Microsoft.Sql/servers/ygserver123?api-version=2014-04-01")

        provider_error = ('{"error":{"code":"MissingSubscriptionRegistration", '
                          '"message":"The subscription registration is in \'Unregistered\' state. '
                          'The subscription must be registered to use namespace \'Microsoft.Sql\'. '
                          'See https://aka.ms/rps-not-found for how to register subscriptions."}}')

        provider_success = '{"success": true}'

        httpretty.register_uri(httpretty.PUT,
                               provider_url,
                               responses=[
                                   httpretty.Response(body=provider_error, status=409),
                                   httpretty.Response(body=provider_success),
                               ],
                               content_type="application/json")

        register_post_url = ("https://management.azure.com/"
                             "subscriptions/12345678-9abc-def0-0000-000000000000/"
                             "providers/Microsoft.Sql/register?api-version=2016-02-01")

        register_post_result = {
            "registrationState":"Registering"
        }

        register_get_url = ("https://management.azure.com/"
                            "subscriptions/12345678-9abc-def0-0000-000000000000/"
                            "providers/Microsoft.Sql?api-version=2016-02-01")

        register_get_result = {
            "registrationState":"Registered"
        }

        httpretty.register_uri(httpretty.POST,
                               register_post_url,
                               body=json.dumps(register_post_result),
                               content_type="application/json")

        httpretty.register_uri(httpretty.GET,
                               register_get_url,
                               body=json.dumps(register_get_result),
                               content_type="application/json")

        configuration = AzureConfiguration(None)
        register_rp_hook = configuration.hooks[0]

        session = requests.Session()
        def rp_cb(r, *args, **kwargs):
            kwargs.setdefault("msrest", {})["session"] = session
            return register_rp_hook(r, *args, **kwargs)
        session.hooks['response'].append(rp_cb)

        response = session.put(provider_url)
        self.assertTrue(response.json()['success'])

    @httpretty.activate
    @mock.patch('time.sleep', return_value=None)
    def test_register_failed(self, time_sleep):
        """Protocol:
        - We call the provider and get a 409 provider error
        - Now we POST register provider and get "Registering"
        - This POST failed
        """

        provider_url = ("https://management.azure.com/"
                        "subscriptions/12345678-9abc-def0-0000-000000000000/"
                        "resourceGroups/clitest.rg000001/"
                        "providers/Microsoft.Sql/servers/ygserver123?api-version=2014-04-01")

        provider_error = ('{"error":{"code":"MissingSubscriptionRegistration", '
                          '"message":"The subscription registration is in \'Unregistered\' state. '
                          'The subscription must be registered to use namespace \'Microsoft.Sql\'. '
                          'See https://aka.ms/rps-not-found for how to register subscriptions."}}')

        provider_success = '{"success": true}'

        httpretty.register_uri(httpretty.PUT,
                               provider_url,
                               responses=[
                                   httpretty.Response(body=provider_error, status=409),
                                   httpretty.Response(body=provider_success),
                               ],
                               content_type="application/json")

        register_post_url = ("https://management.azure.com/"
                             "subscriptions/12345678-9abc-def0-0000-000000000000/"
                             "providers/Microsoft.Sql/register?api-version=2016-02-01")

        httpretty.register_uri(httpretty.POST,
                               register_post_url,
                               status=409,
                               content_type="application/json")

        configuration = AzureConfiguration(None)
        register_rp_hook = configuration.hooks[0]

        session = requests.Session()
        def rp_cb(r, *args, **kwargs):
            kwargs.setdefault("msrest", {})["session"] = session
            return register_rp_hook(r, *args, **kwargs)
        session.hooks['response'].append(rp_cb)

        response = session.put(provider_url)
        self.assertEqual(409, response.status_code)

    def test_resource_parse(self):
        """
        Tests resource id parsing, reforming, and validation.
        """
        tests = [
            {
                'resource_id': '/subscriptions/fakesub/resourcegroups/testgroup/providers'
                               '/Microsoft.Storage/storageAccounts/foo/providers'
                               '/Microsoft.Authorization/locks/bar',
                'expected': {
                    'name': 'foo',
                    'type': 'storageAccounts',
                    'namespace': 'Microsoft.Storage',
                    'child_name_1': 'bar',
                    'child_namespace_1': 'Microsoft.Authorization',
                    'child_type_1': 'locks',
                    'child_parent_1': 'storageAccounts/foo/providers/Microsoft.Authorization/',
                    'resource_group': 'testgroup',
                    'subscription': 'fakesub',
                }
            },
            {
                'resource_id': '/subscriptions/fakesub/resourcegroups/testgroup/providers'
                               '/Microsoft.Storage/storageAccounts/foo'
                               '/locks/bar',
                'expected': {
                    'name': 'foo',
                    'type': 'storageAccounts',
                    'namespace': 'Microsoft.Storage',
                    'child_name_1': 'bar',
                    'child_type_1': 'locks',
                    'child_parent_1': 'storageAccounts/foo/',
                    'resource_group': 'testgroup',
                    'subscription': 'fakesub',
                }
            },
            {
                'resource_id': '/subscriptions/fakesub/resourcegroups/testgroup/providers'
                               '/Microsoft.Storage/storageAccounts/foo/providers'
                               '/Microsoft.Authorization/locks/bar/providers/Microsoft.Network/'
                               'nets/gc',
                'expected': {
                    'name': 'foo',
                    'type': 'storageAccounts',
                    'namespace': 'Microsoft.Storage',
                    'child_name_1': 'bar',
                    'child_namespace_1': 'Microsoft.Authorization',
                    'child_type_1': 'locks',
                    'child_parent_1': 'storageAccounts/foo/providers/Microsoft.Authorization/',
                    'child_name_2': 'gc',
                    'child_namespace_2': 'Microsoft.Network',
                    'child_type_2': 'nets',
                    'child_parent_2': 'storageAccounts/foo/providers/Microsoft.Authorization/'
                                      'locks/bar/providers/Microsoft.Network/',
                    'resource_group': 'testgroup',
                    'subscription': 'fakesub',
                }
            },
            {
                'resource_id': '/subscriptions/fakesub/resourcegroups/testgroup/providers'
                               '/Microsoft.Storage/storageAccounts/foo'
                               '/locks/bar/nets/gc',
                'expected': {
                    'name': 'foo',
                    'type': 'storageAccounts',
                    'namespace': 'Microsoft.Storage',
                    'child_name_1': 'bar',
                    'child_type_1': 'locks',
                    'child_parent_1': 'storageAccounts/foo/',
                    'child_name_2': 'gc',
                    'child_type_2': 'nets',
                    'child_parent_2': 'storageAccounts/foo/locks/bar/',
                    'resource_group': 'testgroup',
                    'subscription': 'fakesub',
                }
            },
            {
                'resource_id': '/subscriptions/mySub/resourceGroups/myRg/providers/'
                               'Microsoft.Provider1/resourceType1/name1',
                'expected': {
                    'subscription': 'mySub',
                    'resource_group': 'myRg',
                    'namespace': 'Microsoft.Provider1',
                    'type': 'resourceType1',
                    'name': 'name1',
                    'resource_parent': '',
                    'resource_namespace': 'Microsoft.Provider1',
                    'resource_type': 'resourceType1',
                    'resource_name': 'name1'
                }
            },
            {
                'resource_id': '/subscriptions/mySub/resourceGroups/myRg/providers/'
                               'Microsoft.Provider1/resourceType1/name1/resourceType2/name2',
                'expected': {
                    'subscription': 'mySub',
                    'resource_group': 'myRg',
                    'namespace': 'Microsoft.Provider1',
                    'type': 'resourceType1',
                    'name': 'name1',
                    'child_namespace_1': None,
                    'child_type_1': 'resourceType2',
                    'child_name_1': 'name2',
                    'child_parent_1': 'resourceType1/name1/',
                    'resource_parent': 'resourceType1/name1/',
                    'resource_namespace': 'Microsoft.Provider1',
                    'resource_type': 'resourceType2',
                    'resource_name': 'name2'
                }
            },
            {
                'resource_id': '/subscriptions/00000/resourceGroups/myRg/providers/'
                               'Microsoft.RecoveryServices/vaults/vault_name/backupFabrics/'
                               'fabric_name/protectionContainers/container_name/'
                               'protectedItems/item_name/recoveryPoint/recovery_point_guid',
                'expected': {
                    'subscription': '00000',
                    'resource_group': 'myRg',
                    'namespace': 'Microsoft.RecoveryServices',
                    'type': 'vaults',
                    'name': 'vault_name',
                    'child_type_1': 'backupFabrics',
                    'child_name_1': 'fabric_name',
                    'child_parent_1': 'vaults/vault_name/',
                    'child_type_2': 'protectionContainers',
                    'child_name_2': 'container_name',
                    'child_parent_2': 'vaults/vault_name/backupFabrics/fabric_name/',
                    'child_type_3': 'protectedItems',
                    'child_name_3': 'item_name',
                    'child_parent_3': 'vaults/vault_name/backupFabrics/fabric_name/'
                                      'protectionContainers/container_name/',
                    'child_type_4': 'recoveryPoint',
                    'child_name_4': 'recovery_point_guid',
                    'child_parent_4': 'vaults/vault_name/backupFabrics/fabric_name/'
                                      'protectionContainers/container_name/protectedItems/'
                                      'item_name/',
                    'resource_parent': 'vaults/vault_name/backupFabrics/fabric_name/'
                                       'protectionContainers/container_name/protectedItems/'
                                       'item_name/',
                    'resource_namespace': 'Microsoft.RecoveryServices',
                    'resource_type': 'recoveryPoint',
                    'resource_name': 'recovery_point_guid'
                }
            },
            {
                'resource_id': '/subscriptions/mySub/resourceGroups/myRg/providers/'
                               'Microsoft.Provider1/resourceType1/name1/resourceType2/name2/'
                               'providers/Microsoft.Provider3/resourceType3/name3',
                'expected': {
                    'subscription': 'mySub',
                    'resource_group': 'myRg',
                    'namespace': 'Microsoft.Provider1',
                    'type': 'resourceType1',
                    'name': 'name1',
                    'child_namespace_1': None,
                    'child_type_1': 'resourceType2',
                    'child_name_1': 'name2',
                    'child_parent_1' : 'resourceType1/name1/',
                    'child_namespace_2': 'Microsoft.Provider3',
                    'child_type_2': 'resourceType3',
                    'child_name_2': 'name3',
                    'child_parent_2': 'resourceType1/name1/resourceType2/name2/'
                                      'providers/Microsoft.Provider3/',
                    'resource_parent': 'resourceType1/name1/resourceType2/name2/'
                                       'providers/Microsoft.Provider3/',
                    'resource_namespace': 'Microsoft.Provider1',
                    'resource_type': 'resourceType3',
                    'resource_name': 'name3'
                }
            },
            {
                'resource_id': '/subscriptions/fakesub/providers/Microsoft.Authorization'
                               '/locks/foo',
                'expected': {
                    'name': 'foo',
                    'type': 'locks',
                    'namespace': 'Microsoft.Authorization',
                    'subscription': 'fakesub',
                }
            },
            {
                'resource_id': '/Subscriptions/fakesub/providers/Microsoft.Authorization'
                               '/locks/foo',
                'expected': {
                    'name': 'foo',
                    'type': 'locks',
                    'namespace': 'Microsoft.Authorization',
                    'subscription': 'fakesub',
                }
            },
            {
                'resource_id': '/subscriptions/mySub/resourceGroups/myRg',
                'expected': {
                    'subscription': 'mySub',
                    'resource_group': 'myRg'
                }
            }
        ]
        for test in tests:
            self.assertTrue(is_valid_resource_id(test['resource_id']))
            kwargs = parse_resource_id(test['resource_id'])
            for key in test['expected']:
                try:
                    self.assertEqual(kwargs[key], test['expected'][key])
                except KeyError:
                    self.assertTrue(key not in kwargs and test['expected'][key] is None)

        invalid_ids = [
            '/subscriptions/fakesub/resourceGroups/myRg/type1/name1',
            '/subscriptions/fakesub/resourceGroups/myRg/providers/Microsoft.Provider/foo',
            '/subscriptions/fakesub/resourceGroups/myRg/providers/namespace/type/name/type1'
        ]
        for invalid_id in invalid_ids:
            self.assertFalse(is_valid_resource_id(invalid_id))

        tests = [
            {
                'resource_id': '/subscriptions/fakesub/resourcegroups/testgroup/providers'
                               '/Microsoft.Storage/storageAccounts/foo/providers'
                               '/Microsoft.Authorization/locks/bar',
                'id_args': {
                    'name': 'foo',
                    'type': 'storageAccounts',
                    'namespace': 'Microsoft.Storage',
                    'child_name_1': 'bar',
                    'child_namespace_1': 'Microsoft.Authorization',
                    'child_type_1': 'locks',
                    'resource_group': 'testgroup',
                    'subscription': 'fakesub',
                }
            },
            {
                'resource_id': '/subscriptions/fakesub/resourcegroups/testgroup/providers'
                               '/Microsoft.Storage/storageAccounts/foo'
                               '/locks/bar',
                'id_args': {
                    'name': 'foo',
                    'type': 'storageAccounts',
                    'namespace': 'Microsoft.Storage',
                    'child_name_1': 'bar',
                    'child_type_1': 'locks',
                    'resource_group': 'testgroup',
                    'subscription': 'fakesub',
                }
            },
            {
                'resource_id': '/subscriptions/mySub/resourceGroups/myRg/providers/'
                               'Microsoft.Provider1/resourceType1/name1/resourceType2/name2/'
                               'providers/Microsoft.Provider3/resourceType3/name3',
                'id_args': {
                    'subscription': 'mySub',
                    'resource_group': 'myRg',
                    'namespace': 'Microsoft.Provider1',
                    'type': 'resourceType1',
                    'name': 'name1',
                    'child_type_1': 'resourceType2',
                    'child_name_1': 'name2',
                    'child_namespace_2': 'Microsoft.Provider3',
                    'child_type_2': 'resourceType3',
                    'child_name_2': 'name3'
                }
            },
            {
                'resource_id': '/subscriptions/mySub/resourceGroups/myRg/'
                               'providers/Microsoft.Provider1',
                'id_args': {
                    'subscription': 'mySub',
                    'resource_group': 'myRg',
                    'namespace': 'Microsoft.Provider1'
                }
            },
            {
                'resource_id': '/subscriptions/mySub/resourceGroups/myRg',
                'id_args': {
                    'subscription': 'mySub',
                    'resource_group': 'myRg'
                }
            },
            {
                'resource_id': '/subscriptions/mySub/resourceGroups/myRg/'
                               'providers/Microsoft.Provider1/resourceType1/name1/resourceType2/'
                               'name2/providers/Microsoft.Provider3',
                'id_args': {
                    'subscription': 'mySub',
                    'resource_group': 'myRg',
                    'namespace': 'Microsoft.Provider1',
                    'type': 'resourceType1',
                    'name': 'name1',
                    'child_type_1': 'resourceType2',
                    'child_name_1': 'name2',
                    'child_namespace_2': 'Microsoft.Provider3'
                }
            },
            {
                'resource_id': '/subscriptions/mySub/resourceGroups/myRg/'
                               'providers/Microsoft.Provider1/resourceType1/name1',
                'id_args': {
                    'subscription': 'mySub',
                    'resource_group': 'myRg',
                    'namespace': 'Microsoft.Provider1',
                    'type': 'resourceType1',
                    'name': 'name1',
                    'child_type_1': None,
                    'child_name_1': 'name2',
                    'child_namespace_2': 'Microsoft.Provider3'
                }
            },
            {
                'resource_id': '/subscriptions/mySub/resourceGroups/myRg',
                'id_args': {
                    'subscription': 'mySub',
                    'resource_group': 'myRg'
                }
            }
        ]
        for test in tests:
            rsrc_id = resource_id(**test['id_args'])
            self.assertEqual(rsrc_id.lower(), test['resource_id'].lower())

    def test_is_resource_name(self):
        invalid_names = [
            '',
            'knights/ni',
            'spam&eggs',
            'i<3you',
            'a' * 261,
        ]

        for test in invalid_names:
            assert not is_valid_resource_name(test)

        valid_names = [
            'abc-123',
            ' ',  # no one said it had to be a good resource name.
            'a' * 260,
        ]

        for test in valid_names:
            assert is_valid_resource_name(test)


if __name__ == "__main__":
    unittest.main()
