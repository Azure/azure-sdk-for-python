#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import requests

def iterate_generic(self, items_func):
    list_result = self.list(None)
    for obj in items_func(list_result):
        yield obj

    while list_result.next_link:
        list_result = self.list_next(
            list_result.next_link,
        )
        for obj in items_func(list_result):
            yield obj

def iterate_resource_groups(self):
    '''Iterate through all the resource groups.'''
    def get_items(result):
        return result.resource_groups
    return iterate_generic(self, get_items)

def iterate_providers(self):
    def get_items(result):
        return result.providers
    return iterate_generic(self, get_items)


class Subscription(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

def get_subscriptions(auth_token):
    response = requests.get(
        'https://management.azure.com/subscriptions',
        params={'api-version': '2014-01-01'},
        headers={'authorization': 'Bearer {}'.format(auth_token)},
    )
    if response.ok:
        result = response.json()
        return [Subscription(item['subscriptionId'], item['displayName']) for item in result['value']]
    else:
        return []

class Tenant(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

def get_tenants(auth_token):
    response = requests.get(
        'https://management.azure.com/tenants',
        params={'api-version': '2014-01-01'},
        headers={'authorization': 'Bearer {}'.format(auth_token)},
    )
    if response.ok:
        result = response.json()
        return [item['tenantId'] for item in result['value']]
    else:
        return []
