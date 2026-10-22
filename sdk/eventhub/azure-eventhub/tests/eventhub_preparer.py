# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# This EventHubs resource preparer is for future use after the tests are all compatible with
# The resource preparer.

import functools

from azure.mgmt.eventhub import EventHubManagementClient
from azure.mgmt.eventhub.models import Eventhub, AccessRights

from devtools_testutils import ResourceGroupPreparer, AzureMgmtPreparer, AzureTestError, FakeResource

from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM

EVENTHUB_DEFAULT_AUTH_RULE_NAME = "RootManageSharedAccessKey"
EVENTHUB_NAMESPACE_PARAM = "eventhub_namespace"
EVENTHUB_PARAM = "eventhub"
EVENTHUB_AUTHORIZATION_RULE_PARAM = "eventhub_authorization_rule"


# Service Bus Namespace Preparer and its shorthand decorator
class EventHubNamespacePreparer(AzureMgmtPreparer):
    def __init__(
        self,
        name_prefix="",
        use_cache=False,
        sku="Standard",
        location="westus",
        parameter_name=EVENTHUB_NAMESPACE_PARAM,
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=True,
    ):
        super(EventHubNamespacePreparer, self).__init__(
            name_prefix,
            24,
            random_name_enabled=random_name_enabled,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
        )
        self.location = location
        self.sku = sku
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.connection_string = ""
        if random_name_enabled:
            self.resource_moniker = self.name_prefix + "ehname"

        self.set_cache(use_cache, sku, location)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(EventHubManagementClient)  # type: EventHubManagementClient
            group = self._get_resource_group(**kwargs)
            namespace_async_operation = self.client.namespaces.begin_create_or_update(
                group.name,
                name,
                {
                    "sku": {"name": self.sku},
                    "location": self.location,
                },
            )
            self.resource = namespace_async_operation.result()

            key = self.client.namespaces.list_keys(group.name, name, EVENTHUB_DEFAULT_AUTH_RULE_NAME)
            self.connection_string = key.primary_connection_string
            self.key_name = key.key_name
            self.primary_key = key.primary_key
        else:
            self.resource = FakeResource(name=name, id=name)
            self.connection_string = "Endpoint=sb://{}.servicebus.windows.net/;SharedAccessKeyName=test;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=".format(
                name
            )
            self.key_name = EVENTHUB_DEFAULT_AUTH_RULE_NAME
            self.primary_key = "ZmFrZV9hY29jdW50X2tleQ=="
        return {
            self.parameter_name: self.resource,
            "{}_connection_string".format(self.parameter_name): self.connection_string,
            "{}_key_name".format(self.parameter_name): self.key_name,
            "{}_primary_key".format(self.parameter_name): self.primary_key,
            "{}_management_client".format(self.parameter_name): self.client,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            self.client.namespaces.begin_delete(group.name, name).wait()

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = (
                "To create an event hub a resource group is required. Please add "
                "decorator @{} in front of this event hub preparer."
            )
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))


# Shared base class for event hub sub-resources that require a namespace and RG to exist.
class _EventHubChildResourcePreparer(AzureMgmtPreparer):
    def __init__(
        self,
        name_prefix="",
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        eventhub_namespace_parameter_name=EVENTHUB_NAMESPACE_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=True,
    ):
        super(_EventHubChildResourcePreparer, self).__init__(
            name_prefix,
            24,
            random_name_enabled=random_name_enabled,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
        )
        self.resource_group_parameter_name = resource_group_parameter_name
        self.eventhub_namespace_parameter_name = eventhub_namespace_parameter_name

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = (
                "To create this event hub child resource event hub a resource group is required. Please add "
                "decorator @{} in front of this event hub preparer."
            )
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_namespace(self, **kwargs):
        try:
            return kwargs.get(self.eventhub_namespace_parameter_name)
        except KeyError:
            template = (
                "To create this event hub child resource a event hub namespace is required. Please add "
                "decorator @{} in front of this event hub preparer."
            )
            raise AzureTestError(template.format(EventHubNamespacePreparer.__name__))


class EventHubPreparer(_EventHubChildResourcePreparer):
    def __init__(
        self,
        name_prefix="",
        use_cache=False,
        parameter_name=EVENTHUB_PARAM,
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        eventhub_namespace_parameter_name=EVENTHUB_NAMESPACE_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=True,
    ):
        super(EventHubPreparer, self).__init__(
            name_prefix,
            random_name_enabled=random_name_enabled,
            resource_group_parameter_name=resource_group_parameter_name,
            eventhub_namespace_parameter_name=eventhub_namespace_parameter_name,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
        )
        self.parameter_name = parameter_name
        if random_name_enabled:
            self.resource_moniker = self.name_prefix + "eventhub"
        self.set_cache(use_cache)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(EventHubManagementClient)
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            self.resource = self.client.event_hubs.create_or_update(group.name, namespace.name, name, {})
        else:
            self.resource = FakeResource(name=name, id=name)
        return {
            self.parameter_name: self.resource,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            self.client.event_hubs.delete(group.name, namespace.name, name, polling=False)


class EventHubNamespaceAuthorizationRulePreparer(_EventHubChildResourcePreparer):
    def __init__(
        self,
        name_prefix="",
        use_cache=False,
        access_rights=[AccessRights.manage, AccessRights.send, AccessRights.listen],
        parameter_name=EVENTHUB_AUTHORIZATION_RULE_PARAM,
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        eventhub_namespace_parameter_name=EVENTHUB_NAMESPACE_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=True,
    ):
        super(EventHubNamespaceAuthorizationRulePreparer, self).__init__(
            name_prefix,
            random_name_enabled=random_name_enabled,
            resource_group_parameter_name=resource_group_parameter_name,
            eventhub_namespace_parameter_name=eventhub_namespace_parameter_name,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
        )
        self.parameter_name = parameter_name
        self.access_rights = access_rights
        if random_name_enabled:
            self.resource_moniker = self.name_prefix + "sbnameauth"
        self.set_cache(use_cache, access_rights)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(EventHubManagementClient)
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            self.resource = self.client.namespaces.create_or_update_authorization_rule(
                group.name, namespace.name, name, self.access_rights
            )

            key = self.client.namespaces.list_keys(group.name, namespace.name, name)
            connection_string = key.primary_connection_string
        else:
            self.resource = FakeResource(name=name, id=name)
            connection_string = "https://microsoft.com"
        return {
            self.parameter_name: self.resource,
            "{}_connection_string".format(self.parameter_name): connection_string,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            self.client.namespaces.delete_authorization_rule(group.name, namespace.name, name, polling=False)


class EventHubAuthorizationRulePreparer(_EventHubChildResourcePreparer):
    def __init__(
        self,
        name_prefix="",
        use_cache=False,
        access_rights=[AccessRights.manage, AccessRights.send, AccessRights.listen],
        parameter_name=EVENTHUB_AUTHORIZATION_RULE_PARAM,
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        eventhub_namespace_parameter_name=EVENTHUB_NAMESPACE_PARAM,
        eventhub_parameter_name=EVENTHUB_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=True,
    ):
        super(EventHubAuthorizationRulePreparer, self).__init__(
            name_prefix,
            random_name_enabled=random_name_enabled,
            resource_group_parameter_name=resource_group_parameter_name,
            eventhub_namespace_parameter_name=eventhub_namespace_parameter_name,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
        )
        self.parameter_name = parameter_name
        self.access_rights = access_rights
        self.eventhub_parameter_name = eventhub_parameter_name
        if random_name_enabled:
            self.resource_moniker = self.name_prefix + "evnethubauth"
        self.set_cache(use_cache, access_rights)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(EventHubManagementClient)
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            eventhub = self._get_eventhub(**kwargs)
            self.resource = self.client.event_hubs.create_or_update_authorization_rule(
                group.name, namespace.name, eventhub.name, name, self.access_rights
            )

            key = self.client.event_hubs.list_keys(group.name, namespace.name, eventhub.name, name)
            connection_string = key.primary_connection_string
        else:
            self.resource = FakeResource(name=name, id=name)
            connection_string = "https://microsoft.com"
        return {
            self.parameter_name: self.resource,
            "{}_connection_string".format(self.parameter_name): connection_string,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            eventhub = self._get_eventhub(**kwargs)
            self.client.event_hubs.delete_authorization_rule(
                group.name, namespace.name, eventhub.name, name, polling=False
            )

    def _get_eventhub(self, **kwargs):
        try:
            return kwargs.get(self.eventhub_parameter_name)
        except KeyError:
            template = (
                "To create this event hub authorization rule a event hub is required. Please add "
                "decorator @{} in front of this event hub preparer."
            )
            raise AzureTestError(template.format(EventHubPreparer.__name__))


CachedEventHubNamespacePreparer = functools.partial(EventHubNamespacePreparer, use_cache=True)
CachedEventHubPreparer = functools.partial(EventHubPreparer, use_cache=True)
