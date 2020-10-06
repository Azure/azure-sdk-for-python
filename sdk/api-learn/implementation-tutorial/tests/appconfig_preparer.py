# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from collections import namedtuple
import functools
import os
import datetime
import time
from functools import partial

from devtools_testutils import AzureMgmtPreparer, FakeResource
from azure.mgmt.appconfiguration import AppConfigurationManagementClient

class AppConfigPreparer(AzureMgmtPreparer):
    def __init__(self, name_prefix='',
                    use_cache=False,
                    random_name_length=75,
                    sku='Standard_LRS',
                    location='westus',
                    parameter_name='appconfig_account',
                    resource_group_parameter_name='resource_group',
                    disable_recording=True,
                    playback_fake_resource=None,
                    client_kwargs=None,
                    random_name_enabled=True):
        super(AppConfigPreparer, self).__init__(
            name_prefix,
            random_name_length,
            playback_fake_resource=playback_fake_resource,
            disable_recording=disable_recording,
            client_kwargs=client_kwargs,
            random_name_enabled=random_name_enabled
        )
        self.location = location
        self.sku = sku
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.appconfig_key = ''
        self.appconfig_account_name = ''
        self.appconfig_url = ''
        self.appconfig_conn_str = ''
        self.resource_moniker = self.name_prefix
        self.use_cache = use_cache
        if random_name_enabled:
            self.resource_moniker += "appconfigname"

        self.set_cache(use_cache, sku, location)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(AppConfigurationManagementClient)
            group = self._get_resource_group(**kwargs)

            self.test_class_instance.scrubber.register_name_pair(
                name,
                self.resource_moniker
            )
        else:
            self.resource = FakeResource(name=name, id=name)
            self.appconfig_conn_str = "Endpoint=https://fake_app_config.azconfig-test.io;Id=0-l4-s0:h5htBaY5Z1LwFz50bIQv;Secret=bgyvBgwsQIw0s8myrqJJI3nLrj81M/kzSgSuP4BBoVg="
            # self.

        return {
            self.parameter_name: self.resource,
            'app_config_url': self.appconfig_url,
            'app_config_conn_str': self.appconfig_conn_str
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            self.client.namespaces.delete(group.name, name, polling=False)

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an app configuration a resource group is required. Please add ' \
                       'decorator @{} in front of this service bus preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

CachedAppConfigPreparer = functools.partial(AppConfigPreparer, use_cache=True)