# coding: utf-8

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
import base64
import os
import random
import sys
import time
import unittest

from datetime import datetime
from azure import WindowsAzureError
from azure.http import HTTPError
from azure.servicebus import (
    AuthorizationRule,
    EventHub,
    ServiceBusService,
    )
from util import (
    AzureTestCase,
    credentials,
    getUniqueName,
    set_service_options,
    )

#------------------------------------------------------------------------------


class EventHubServiceTest(AzureTestCase):

    def setUp(self):
        self.sbs = ServiceBusService(
            credentials.getEventHubNamespace(),
            shared_access_key_name=credentials.getEventHubSasKeyName(),
            shared_access_key_value=credentials.getEventHubSasKeyValue(),
            )

        set_service_options(self.sbs)

        self.event_hub_name = getUniqueName('uthub')

    def tearDown(self):
        self.cleanup()
        return super(EventHubServiceTest, self).tearDown()

    def cleanup(self):
        try:
            self.sbs.delete_event_hub(self.event_hub_name)
        except:
            pass

    #--Helpers-----------------------------------------------------------------
    def _create_event_hub(self, hub_name):
        self.sbs.create_event_hub(hub_name, None, True)

    #--Test cases for event hubs ----------------------------------------------
    def test_create_event_hub_no_options(self):
        # Arrange

        # Act
        created = self.sbs.create_event_hub(self.event_hub_name)

        # Assert
        self.assertTrue(created)

    def test_create_event_hub_no_options_fail_on_exist(self):
        # Arrange

        # Act
        created = self.sbs.create_event_hub(self.event_hub_name, None, True)

        # Assert
        self.assertTrue(created)

    def test_create_event_hub_with_options(self):
        # Arrange

        # Act
        hub = EventHub()
        hub.message_retention_in_days = 5
        hub.status = 'Active'
        hub.user_metadata = 'hello world'
        hub.partition_count = 32
        created = self.sbs.create_event_hub(self.event_hub_name, hub)

        # Assert
        self.assertTrue(created)
        created_hub = self.sbs.get_event_hub(self.event_hub_name)
        self.assertEqual(created_hub.name, self.event_hub_name)
        self.assertEqual(created_hub.message_retention_in_days,
                         hub.message_retention_in_days)
        self.assertEqual(created_hub.status, hub.status)
        self.assertEqual(created_hub.partition_count, hub.partition_count)
        self.assertEqual(created_hub.user_metadata, hub.user_metadata)
        self.assertEqual(len(created_hub.partition_ids), hub.partition_count)

    def test_create_event_hub_with_authorization(self):
        # Arrange

        # Act
        hub = EventHub()
        hub.authorization_rules.append(
            AuthorizationRule(
                claim_type='SharedAccessKey',
                claim_value='None',
                rights=['Manage', 'Send', 'Listen'],
                key_name='Key1',
                primary_key='Wli4rewPGuEsLam95nQEwGR+e8b+ynlupZQ7VfjbQnw=',
                secondary_key='jS+lERPBmbBVGJ5JzIwVRtSGYoFUeunRoADNTjwU3jU=',
            )
        )

        created = self.sbs.create_event_hub(self.event_hub_name, hub)

        # Assert
        self.assertTrue(created)
        created_hub = self.sbs.get_event_hub(self.event_hub_name)
        self.assertEqual(created_hub.name, self.event_hub_name)
        self.assertEqual(len(created_hub.authorization_rules), 1)
        self.assertEqual(created_hub.authorization_rules[0].claim_type,
                         hub.authorization_rules[0].claim_type)
        self.assertEqual(created_hub.authorization_rules[0].claim_value,
                         hub.authorization_rules[0].claim_value)
        self.assertEqual(created_hub.authorization_rules[0].key_name,
                         hub.authorization_rules[0].key_name)
        self.assertEqual(created_hub.authorization_rules[0].primary_key,
                         hub.authorization_rules[0].primary_key)
        self.assertEqual(created_hub.authorization_rules[0].secondary_key,
                         hub.authorization_rules[0].secondary_key)

    def test_update_event_hub(self):
        # Arrange
        self._create_event_hub(self.event_hub_name)

        # Act
        hub = EventHub(message_retention_in_days=3)
        result = self.sbs.update_event_hub(self.event_hub_name, hub)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.name, self.event_hub_name)
        self.assertEqual(result.message_retention_in_days,
                         hub.message_retention_in_days)

    def test_update_event_hub_with_authorization(self):
        # Arrange
        self._create_event_hub(self.event_hub_name)

        # Act
        hub = EventHub()
        hub.authorization_rules.append(
            AuthorizationRule(
                claim_type='SharedAccessKey',
                claim_value='None',
                rights=['Manage', 'Send', 'Listen'],
                key_name='Key1',
                primary_key='Wli4rewPGuEsLam95nQEwGR+e8b+ynlupZQ7VfjbQnw=',
                secondary_key='jS+lERPBmbBVGJ5JzIwVRtSGYoFUeunRoADNTjwU3jU=',
            )
        )
        result = self.sbs.update_event_hub(self.event_hub_name, hub)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.name, self.event_hub_name)
        self.assertEqual(len(result.authorization_rules), 1)
        self.assertEqual(result.authorization_rules[0].claim_type,
                         hub.authorization_rules[0].claim_type)
        self.assertEqual(result.authorization_rules[0].claim_value,
                         hub.authorization_rules[0].claim_value)
        self.assertEqual(result.authorization_rules[0].key_name,
                         hub.authorization_rules[0].key_name)
        self.assertEqual(result.authorization_rules[0].primary_key,
                         hub.authorization_rules[0].primary_key)
        self.assertEqual(result.authorization_rules[0].secondary_key,
                         hub.authorization_rules[0].secondary_key)

    def test_get_event_hub_with_existing_event_hub(self):
        # Arrange
        self._create_event_hub(self.event_hub_name)

        # Act
        event_hub = self.sbs.get_event_hub(self.event_hub_name)

        # Assert
        self.assertIsNotNone(event_hub)
        self.assertEqual(event_hub.name, self.event_hub_name)

    def test_get_event_hub_with_non_existing_event_hub(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            resp = self.sbs.get_event_hub(self.event_hub_name)

        # Assert

    def test_delete_event_hub_with_existing_event_hub(self):
        # Arrange
        self._create_event_hub(self.event_hub_name)

        # Act
        deleted = self.sbs.delete_event_hub(self.event_hub_name)

        # Assert
        self.assertTrue(deleted)

    def test_delete_event_hub_with_existing_event_hub_fail_not_exist(self):
        # Arrange
        self._create_event_hub(self.event_hub_name)

        # Act
        deleted = self.sbs.delete_event_hub(self.event_hub_name, True)

        # Assert
        self.assertTrue(deleted)

    def test_delete_event_hub_with_non_existing_event_hub(self):
        # Arrange

        # Act
        deleted = self.sbs.delete_event_hub(self.event_hub_name)

        # Assert
        self.assertFalse(deleted)

    def test_delete_event_hub_with_non_existing_event_hub_fail_not_exist(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.sbs.delete_event_hub(self.event_hub_name, True)

        # Assert

    def test_send_event(self):
        # Arrange
        self._create_event_hub(self.event_hub_name)

        # Act
        result = self.sbs.send_event(self.event_hub_name,
                                     'hello world')
        result = self.sbs.send_event(self.event_hub_name,
                                     'wake up world')
        result = self.sbs.send_event(self.event_hub_name,
                                     'goodbye!')

        # Assert
        self.assertIsNone(result)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
