# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import division
from datetime import datetime, timedelta
from dateutil.tz import tzutc, tzoffset
import uuid

from azure.core.credentials import AccessToken, AzureNamedKeyCredential
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.data.tables import (
    generate_account_sas,
    AccountSasPermissions,
    ResourceTypes,
    EntityProperty,
    EdmType,
    TableEntity,
)

SLEEP_DELAY = 30

TEST_TABLE_PREFIX = 'pytablesync'

class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args):
        return self.token


class TableTestCase(object):

    def connection_string(self, account, key):
        return "DefaultEndpointsProtocol=https;AccountName=" + account + ";AccountKey=" + str(key) + ";EndpointSuffix=core.windows.net"

    def account_url(self, account, endpoint_type):
        """Return an url of storage account.

        :param str storage_account: Storage account name
        :param str storage_type: The Storage type part of the URL. Should be "table", or "cosmos", etc.
        """
        try:
            if endpoint_type == "table":
                return account.primary_endpoints.table.rstrip("/")
            if endpoint_type == "cosmos":
                return "https://{}.table.cosmos.azure.com".format(account.name)
            else:
                raise ValueError("Unknown storage type {}".format(storage_type))
        except AttributeError: # Didn't find "primary_endpoints"
            if endpoint_type == "table":
                return 'https://{}.{}.core.windows.net'.format(account, endpoint_type)
            if endpoint_type == "cosmos":
                return "https://{}.table.cosmos.azure.com".format(account)

    def generate_sas_token(self):
        fake_key = 'a'*30 + 'b'*30

        return '?' + generate_account_sas(
            credential = AzureNamedKeyCredential(name="fakename", key=fake_key),
            resource_types = ResourceTypes(object=True),
            permission = AccountSasPermissions(read=True,list=True),
            start = datetime.now() - timedelta(hours = 24),
            expiry = datetime.now() + timedelta(days = 8)
        )

    def generate_fake_token(self):
        return FakeTokenCredential()

    def _get_table_reference(self, prefix=TEST_TABLE_PREFIX):
        table_name = self.get_resource_name(prefix)
        return table_name

    def _create_table(self, ts, prefix=TEST_TABLE_PREFIX, table_list=None):
        table_name = self._get_table_reference(prefix)
        try:
            table = ts.create_table(table_name)
            if table_list is not None:
                table_list.append(table)
        except ResourceExistsError:
            table = ts.get_table_client(table_name)
        return table

    def _delete_table(self, ts, table):
        if table is None:
            return
        ts.delete_table(table.name)

    def _delete_all_tables(self, ts):
        for table in ts.list_tables():
            ts.delete_table(table.name)

    def _create_pk_rk(self, pk, rk):
        try:
            pk = pk if pk is not None else self.get_resource_name('pk').decode('utf-8')
            rk = rk if rk is not None else self.get_resource_name('rk').decode('utf-8')
        except AttributeError:
            pk = pk if pk is not None else self.get_resource_name('pk')
            rk = rk if rk is not None else self.get_resource_name('rk')
        return pk, rk

    def _create_random_base_entity_dict(self):
        """
        Creates a dict-based entity with only pk and rk.
        """
        partition, row = self._create_pk_rk(None, None)
        return {
            'PartitionKey': partition,
            'RowKey': row,
        }

    def _create_random_entity_dict(self, pk=None, rk=None):
        """
        Creates a dictionary-based entity with fixed values, using all
        of the supported data types.
        """
        partition, row = self._create_pk_rk(pk, rk)
        properties = {
            'PartitionKey': partition,
            'RowKey': row,
            'age': 39,
            'sex': u'male',
            'married': True,
            'deceased': False,
            'optional': None,
            'ratio': 3.1,
            'evenratio': 3.0,
            'large': 933311100,
            'Birthday': datetime(1973, 10, 4, tzinfo=tzutc()),
            'birthday': datetime(1970, 10, 4, tzinfo=tzutc()),
            'binary': b'binary',
            'other': EntityProperty(20, EdmType.INT32),
            'clsid': uuid.UUID('c9da6455-213d-42c9-9a79-3e9149a57833')
        }
        return TableEntity(**properties)

    def _create_updated_entity_dict(self, partition, row):
        '''
        Creates a dictionary-based entity with fixed values, with a
        different set of values than the default entity. It
        adds fields, changes field values, changes field types,
        and removes fields when compared to the default entity.
        '''
        return {
            'PartitionKey': partition,
            'RowKey': row,
            'age': u'abc',
            'sex': u'female',
            'sign': u'aquarius',
            'birthday': datetime(1991, 10, 4, tzinfo=tzutc())
        }

    def _assert_default_entity(self, entity):
        '''
        Asserts that the entity passed in matches the default entity.
        '''
        assert entity['age'] ==  39
        assert entity['sex'] ==  'male'
        assert entity['married'] ==  True
        assert entity['deceased'] ==  False
        assert not "optional" in entity
        assert entity['ratio'] ==  3.1
        assert entity['evenratio'] ==  3.0
        assert entity['large'] ==  933311100
        assert entity['Birthday'] == datetime(1973, 10, 4, tzinfo=tzutc())
        assert entity['birthday'] == datetime(1970, 10, 4, tzinfo=tzutc())
        assert entity['binary'].value ==  b'binary'
        assert entity['other'] ==  20
        assert entity['clsid'] ==  uuid.UUID('c9da6455-213d-42c9-9a79-3e9149a57833')
        assert entity.metadata['etag']
        assert entity.metadata['timestamp']

class ResponseCallback(object):
    def __init__(self, status=None, new_status=None):
        self.status = status
        self.new_status = new_status
        self.first = True
        self.count = 0

    def override_first_status(self, response):
        if self.first and response.http_response.status_code == self.status:
            response.http_response.status_code = self.new_status
            self.first = False
        self.count += 1

    def override_status(self, response):
        if response.http_response.status_code == self.status:
            response.http_response.status_code = self.new_status
        self.count += 1


class RetryCounter(object):
    def __init__(self):
        self.count = 0

    def simple_count(self, retry_context):
        self.count += 1
