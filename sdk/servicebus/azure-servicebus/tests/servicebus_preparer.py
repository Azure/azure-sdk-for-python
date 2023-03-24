import functools
import os
import time
import datetime
import logging

from azure.core.exceptions import HttpResponseError
from azure_devtools.scenario_tests import AzureTestError, ReservedResourceNameError
from azure.mgmt.resource import ResourceManagementClient

from azure.mgmt.servicebus import ServiceBusManagementClient
from azure.mgmt.servicebus.models import SBQueue, SBSubscription, AccessRights, SBAuthorizationRule

from azure_devtools.scenario_tests.exceptions import AzureTestError

from devtools_testutils import (
    AzureMgmtPreparer, FakeResource, get_region_override, add_general_regex_sanitizer
)

from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM

SERVICEBUS_DEFAULT_AUTH_RULE_NAME = 'RootManageSharedAccessKey'
SERVICEBUS_NAMESPACE_PARAM = 'servicebus_namespace'
SERVICEBUS_TOPIC_PARAM = 'servicebus_topic'
SERVICEBUS_SUBSCRIPTION_PARAM = 'servicebus_subscription'
SERVICEBUS_QUEUE_PARAM = 'servicebus_queue'
SERVICEBUS_AUTHORIZATION_RULE_PARAM = 'servicebus_authorization_rule'
SERVICEBUS_QUEUE_AUTHORIZATION_RULE_PARAM = 'servicebus_queue_authorization_rule'
SERVICEBUS_ENDPOINT_SUFFIX = os.environ.get('SERVICEBUS_ENDPOINT_SUFFIX', '.servicebus.windows.net')
BASE_URL = os.environ.get("SERVICEBUS_RESOURCE_MANAGER_URL", "https://management.azure.com/")
CREDENTIAL_SCOPES = [f"{BASE_URL}.default"]
LOCATION = get_region_override('westus')


class ServiceBusResourceGroupPreparer(AzureMgmtPreparer):
    def __init__(
        self,
        name_prefix="",
        use_cache=False,
        random_name_length=75,
        parameter_name=RESOURCE_GROUP_PARAM,
        parameter_name_for_location="location",
        location=LOCATION,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=False,
        delete_after_tag_timedelta=datetime.timedelta(hours=8),
    ):
        super(ServiceBusResourceGroupPreparer, self).__init__(
            name_prefix,
            random_name_length,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
            random_name_enabled=random_name_enabled,
        )
        self.location = location
        self.parameter_name = parameter_name
        self.parameter_name_for_location = parameter_name_for_location
        env_value = os.environ.get("AZURE_RESOURCEGROUP_NAME", None)
        self._need_creation = True
        if env_value:
            self.resource_random_name = env_value
            self._need_creation = False
        if self.random_name_enabled:
            self.resource_moniker = self.name_prefix + "rgname"
        self.set_cache(use_cache, parameter_name, name_prefix)
        self.delete_after_tag_timedelta = delete_after_tag_timedelta

    def _prefix_name(self, name):
        name = "rgpy-" + name
        if len(name) > 90:
            name = name[:90]
        return name

    def create_resource(self, name, **kwargs):
        if self.is_live and self._need_creation:
            self.client = self.create_mgmt_client(ResourceManagementClient, base_url=BASE_URL, credential_scopes=CREDENTIAL_SCOPES)
            parameters = {"location": self.location}
            expiry = datetime.datetime.utcnow() + self.delete_after_tag_timedelta
            parameters["tags"] = {"DeleteAfter": expiry.replace(microsecond=0).isoformat()}

            parameters["tags"]["BuildId"] = os.environ.get("BUILD_BUILDID", "local")
            parameters["tags"]["BuildJob"] = os.environ.get("AGENT_JOBNAME", "local")
            parameters["tags"]["BuildNumber"] = os.environ.get("BUILD_BUILDNUMBER", "local")
            parameters["tags"]["BuildReason"] = os.environ.get("BUILD_REASON", "local")
            try:
                # Prefixing all RGs created here with 'rgpy-' for tracing purposes
                name = self._prefix_name(name)
                logging.info(
                    "Attempting to create a Resource Group with name {} and parameters {}".format(name, parameters)
                )
                self.resource = self.client.resource_groups.create_or_update(name, parameters)
            except Exception as ex:
                if "ReservedResourceName" in str(ex):
                    raise ReservedResourceNameError(name)
                raise
        else:
            self.resource = self.resource or FakeResource(
                name=name,
                id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/" + name,
            )
        if name != self.moniker:
            try:
                self.test_class_instance.scrubber.register_name_pair(name, self.moniker)
            # tests using the test proxy don't have a scrubber instance
            except AttributeError:
                add_general_regex_sanitizer(regex=name, value=self.moniker)
        return {
            self.parameter_name: self.resource,
            self.parameter_name_for_location: self.location,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live and self._need_creation:
            name = self._prefix_name(name)
            try:
                if "wait_timeout" in kwargs:
                    azure_poller = self.client.resource_groups.begin_delete(name)
                    azure_poller.wait(kwargs.get("wait_timeout"))
                    if azure_poller.done():
                        return
                    raise AzureTestError("Timed out waiting for resource group to be deleted.")
                else:
                    self.client.resource_groups.begin_delete(name, polling=False).result()
            except HttpResponseError as err:
                logging.info("Failed to delete resource group with name {}".format(name))
                logging.info("{}".format(err))
                pass


# Service Bus Namespace Preparer and its shorthand decorator
class ServiceBusNamespacePreparer(AzureMgmtPreparer):
    def __init__(self,
                 name_prefix='',
                 use_cache=False,
                 sku='Standard', location=LOCATION,
                 parameter_name=SERVICEBUS_NAMESPACE_PARAM,
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None, random_name_enabled=True):
        super(ServiceBusNamespacePreparer, self).__init__(name_prefix, 24,
                                                          random_name_enabled=random_name_enabled,
                                                          disable_recording=disable_recording,
                                                          playback_fake_resource=playback_fake_resource,
                                                          client_kwargs=client_kwargs)
        self.location = location
        self.sku = sku
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.connection_string = ''
        if random_name_enabled:
            self.resource_moniker = self.name_prefix + "sbname"

        self.set_cache(use_cache, sku, location)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(ServiceBusManagementClient, base_url=BASE_URL, credential_scopes=CREDENTIAL_SCOPES)
            group = self._get_resource_group(**kwargs)
            retries = 4
            for i in range(retries):
                try:
                    namespace_async_operation = self.client.namespaces.begin_create_or_update(
                        group.name,
                        name,
                        {
                            'sku': {'name': self.sku},
                            'location': self.location,
                        }
                    )
                    self.resource = namespace_async_operation.result()
                    break
                except Exception as ex:
                    error = "The requested resource {} does not exist".format(group.name)
                    not_found_error = "Operation returned an invalid status code 'Not Found'"
                    if (error not in str(ex) and not_found_error not in str(ex)) or i == retries - 1:
                        raise
                    time.sleep(3)

            key = self.client.namespaces.list_keys(group.name, name, SERVICEBUS_DEFAULT_AUTH_RULE_NAME)
            self.connection_string = key.primary_connection_string
            self.key_name = key.key_name
            self.primary_key = key.primary_key

            self.test_class_instance.scrubber.register_name_pair(
                name,
                self.resource_moniker
            )
        else:
            self.resource = FakeResource(name=name, id=name)
            self.connection_string = f"Endpoint=sb://{name}{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessKeyName=test;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
            self.key_name = SERVICEBUS_DEFAULT_AUTH_RULE_NAME
            self.primary_key = 'ZmFrZV9hY29jdW50X2tleQ=='
        return {
            self.parameter_name: self.resource,
            '{}_connection_string'.format(self.parameter_name): self.connection_string,
            '{}_key_name'.format(self.parameter_name): self.key_name,
            '{}_primary_key'.format(self.parameter_name): self.primary_key,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            self.client.namespaces.delete(group.name, name)

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a service bus a resource group is required. Please add ' \
                       'decorator @{} in front of this service bus preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))


# Shared base class for service bus sub-resources that require a namespace and RG to exist.
class _ServiceBusChildResourcePreparer(AzureMgmtPreparer):
    def __init__(self,
                 name_prefix='',
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 servicebus_namespace_parameter_name=SERVICEBUS_NAMESPACE_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None, random_name_enabled=True):
        super(_ServiceBusChildResourcePreparer, self).__init__(name_prefix, 24,
                                                               random_name_enabled=random_name_enabled,
                                                               disable_recording=disable_recording,
                                                               playback_fake_resource=playback_fake_resource,
                                                               client_kwargs=client_kwargs)
        self.resource_group_parameter_name = resource_group_parameter_name
        self.servicebus_namespace_parameter_name = servicebus_namespace_parameter_name

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create this service bus child resource service bus a resource group is required. Please add ' \
                       'decorator @{} in front of this service bus preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_namespace(self, **kwargs):
        try:
            return kwargs.get(self.servicebus_namespace_parameter_name)
        except KeyError:
            template = 'To create this service bus child resource a service bus namespace is required. Please add ' \
                       'decorator @{} in front of this service bus preparer.'
            raise AzureTestError(template.format(ServiceBusNamespacePreparer.__name__))


class ServiceBusTopicPreparer(_ServiceBusChildResourcePreparer):
    def __init__(self,
                 name_prefix='',
                 use_cache=False,
                 parameter_name=SERVICEBUS_TOPIC_PARAM,
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 servicebus_namespace_parameter_name=SERVICEBUS_NAMESPACE_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None, random_name_enabled=True):
        super(ServiceBusTopicPreparer, self).__init__(name_prefix,
                                                     random_name_enabled=random_name_enabled,
                                                     resource_group_parameter_name=resource_group_parameter_name,
                                                     servicebus_namespace_parameter_name=servicebus_namespace_parameter_name,
                                                     disable_recording=disable_recording,
                                                     playback_fake_resource=playback_fake_resource,
                                                     client_kwargs=client_kwargs)
        self.parameter_name = parameter_name
        if random_name_enabled:
            self.resource_moniker = self.name_prefix + "sbtopic"
        self.set_cache(use_cache)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(ServiceBusManagementClient, base_url=BASE_URL, credential_scopes=CREDENTIAL_SCOPES)
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            retries = 4
            for i in range(retries):
                try:
                    self.resource = self.client.topics.create_or_update(
                        group.name,
                        namespace.name,
                        name,
                        {}
                    )
                    break
                except Exception as ex:
                    error = "The requested resource {} does not exist".format(namespace)
                    not_found_error = "Operation returned an invalid status code 'Not Found'"
                    if (error not in str(ex) and not_found_error not in str(ex)) or i == retries - 1:
                        raise
                    time.sleep(3)

            self.test_class_instance.scrubber.register_name_pair(
                name,
                self.resource_moniker
            )
        else:
            self.resource = FakeResource(name=name, id=name)
        return {
            self.parameter_name: self.resource,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            self.client.topics.delete(group.name, namespace.name, name)


class ServiceBusSubscriptionPreparer(_ServiceBusChildResourcePreparer):
    def __init__(self,
                 name_prefix='',
                 use_cache=False,
                 parameter_name=SERVICEBUS_SUBSCRIPTION_PARAM,
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 servicebus_namespace_parameter_name=SERVICEBUS_NAMESPACE_PARAM,
                 servicebus_topic_parameter_name=SERVICEBUS_TOPIC_PARAM,
                 requires_session=False,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None, random_name_enabled=True):
        super(ServiceBusSubscriptionPreparer, self).__init__(name_prefix,
                                                     random_name_enabled=random_name_enabled,
                                                     resource_group_parameter_name=resource_group_parameter_name,
                                                     servicebus_namespace_parameter_name=servicebus_namespace_parameter_name,
                                                     disable_recording=disable_recording,
                                                     playback_fake_resource=playback_fake_resource,
                                                     client_kwargs=client_kwargs)
        self.servicebus_topic_parameter_name = servicebus_topic_parameter_name
        self.parameter_name = parameter_name
        if random_name_enabled:
            self.resource_moniker = self.name_prefix + "sbsub"
        self.set_cache(use_cache, requires_session)
        self.requires_session=requires_session
        if random_name_enabled:
            self.resource_moniker = self.name_prefix + "sbqueue"

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(ServiceBusManagementClient, base_url=BASE_URL, credential_scopes=CREDENTIAL_SCOPES)
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            topic = self._get_topic(**kwargs)
            retries = 4
            for i in range(retries):
                try:
                    self.resource = self.client.subscriptions.create_or_update(
                        group.name,
                        namespace.name,
                        topic.name,
                        name,
                        SBSubscription(
                            requires_session=self.requires_session
                        )
                    )
                    break
                except Exception as ex:
                    error = "The requested resource {} does not exist".format(namespace)
                    not_found_error = "Operation returned an invalid status code 'Not Found'"
                    if (error not in str(ex) and not_found_error not in str(ex)) or i == retries - 1:
                        raise
                    time.sleep(3)

            self.test_class_instance.scrubber.register_name_pair(
                name,
                self.resource_moniker
            )
        else:
            self.resource = FakeResource(name=name, id=name)
        return {
            self.parameter_name: self.resource,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            topic = self._get_topic(**kwargs)
            self.client.subscriptions.delete(group.name, namespace.name, topic.name, name)

    def _get_topic(self, **kwargs):
        try:
            return kwargs.get(self.servicebus_topic_parameter_name)
        except KeyError:
            template = 'To create this service bus subscription a service bus topic is required. Please add ' \
                       'decorator @{} in front of this service bus preparer.'
            raise AzureTestError(template.format(ServiceBusTopicPreparer.__name__))


class ServiceBusQueuePreparer(_ServiceBusChildResourcePreparer):
    def __init__(self,
                 name_prefix='',
                 use_cache=False,
                 requires_duplicate_detection=False,
                 dead_lettering_on_message_expiration=False,
                 requires_session=False,
                 lock_duration='PT30S',
                 parameter_name=SERVICEBUS_QUEUE_PARAM,
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 servicebus_namespace_parameter_name=SERVICEBUS_NAMESPACE_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None, random_name_enabled=True):
        super(ServiceBusQueuePreparer, self).__init__(name_prefix,
                                                     random_name_enabled=random_name_enabled,
                                                     resource_group_parameter_name=resource_group_parameter_name,
                                                     servicebus_namespace_parameter_name=servicebus_namespace_parameter_name,
                                                     disable_recording=disable_recording,
                                                     playback_fake_resource=playback_fake_resource,
                                                     client_kwargs=client_kwargs)
        self.parameter_name = parameter_name
        self.set_cache(use_cache, requires_duplicate_detection, dead_lettering_on_message_expiration, requires_session, lock_duration)

        # Queue parameters
        self.requires_duplicate_detection=requires_duplicate_detection
        self.dead_lettering_on_message_expiration=dead_lettering_on_message_expiration
        self.requires_session=requires_session
        self.lock_duration=lock_duration
        if random_name_enabled:
            self.resource_moniker = self.name_prefix + "sbqueue"

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(ServiceBusManagementClient, base_url=BASE_URL, credential_scopes=CREDENTIAL_SCOPES)
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            retries = 4
            for i in range(retries):
                try:
                    self.resource = self.client.queues.create_or_update(
                        group.name,
                        namespace.name,
                        name,
                        SBQueue(
                            lock_duration=self.lock_duration,
                            requires_duplicate_detection = self.requires_duplicate_detection,
                            dead_lettering_on_message_expiration = self.dead_lettering_on_message_expiration,
                            requires_session = self.requires_session)
                    )
                    break
                except Exception as ex:
                    error = "The requested resource {} does not exist".format(namespace)
                    not_found_error = "Operation returned an invalid status code 'Not Found'"
                    if (error not in str(ex) and not_found_error not in str(ex)) or i == retries - 1:
                        raise
                    time.sleep(3)

            self.test_class_instance.scrubber.register_name_pair(
                name,
                self.resource_moniker
            )
        else:
            self.resource = FakeResource(name=name, id=name)
        return {
            self.parameter_name: self.resource,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            self.client.queues.delete(group.name, namespace.name, name)


class ServiceBusNamespaceAuthorizationRulePreparer(_ServiceBusChildResourcePreparer):
    def __init__(self,
                 name_prefix='',
                 use_cache=False,
                 access_rights=[AccessRights.manage, AccessRights.send, AccessRights.listen],
                 parameter_name=SERVICEBUS_AUTHORIZATION_RULE_PARAM,
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 servicebus_namespace_parameter_name=SERVICEBUS_NAMESPACE_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None, random_name_enabled=True):
        super(ServiceBusNamespaceAuthorizationRulePreparer, self).__init__(name_prefix,
                                                     random_name_enabled=random_name_enabled,
                                                     resource_group_parameter_name=resource_group_parameter_name,
                                                     servicebus_namespace_parameter_name=servicebus_namespace_parameter_name,
                                                     disable_recording=disable_recording,
                                                     playback_fake_resource=playback_fake_resource,
                                                     client_kwargs=client_kwargs)
        self.parameter_name = parameter_name
        self.access_rights = access_rights
        if random_name_enabled:
            self.resource_moniker = self.name_prefix + "sbnameauth"
        self.set_cache(use_cache, access_rights)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(ServiceBusManagementClient, base_url=BASE_URL, credential_scopes=CREDENTIAL_SCOPES)
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            retries = 4
            for i in range(retries):
                try:
                    self.resource = self.client.namespaces.create_or_update_authorization_rule(
                        group.name,
                        namespace.name,
                        name,
                        SBAuthorizationRule(rights=self.access_rights)
                    )
                    break
                except Exception as ex:
                    error = "The requested resource {} does not exist".format(namespace)
                    not_found_error = "Operation returned an invalid status code 'Not Found'"
                    if (error not in str(ex) and not_found_error not in str(ex)) or i == retries - 1:
                        raise
                    time.sleep(3)

            key = self.client.namespaces.list_keys(group.name, namespace.name, name)
            connection_string = key.primary_connection_string

            self.test_class_instance.scrubber.register_name_pair(
                name,
                self.resource_moniker
            )
        else:
            self.resource = FakeResource(name=name, id=name)
            connection_string = 'https://microsoft.com'
        return {
            self.parameter_name: self.resource,
            '{}_connection_string'.format(self.parameter_name): connection_string,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            self.client.namespaces.delete_authorization_rule(group.name, namespace.name, name)


class ServiceBusQueueAuthorizationRulePreparer(_ServiceBusChildResourcePreparer):
    def __init__(self,
                 name_prefix='',
                 use_cache=False,
                 access_rights=[AccessRights.manage, AccessRights.send, AccessRights.listen],
                 parameter_name=SERVICEBUS_QUEUE_AUTHORIZATION_RULE_PARAM,
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 servicebus_namespace_parameter_name=SERVICEBUS_NAMESPACE_PARAM,
                 servicebus_queue_parameter_name=SERVICEBUS_QUEUE_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None, random_name_enabled=True):
        super(ServiceBusQueueAuthorizationRulePreparer, self).__init__(name_prefix,
                                                     random_name_enabled=random_name_enabled,
                                                     resource_group_parameter_name=resource_group_parameter_name,
                                                     servicebus_namespace_parameter_name=servicebus_namespace_parameter_name,
                                                     disable_recording=disable_recording,
                                                     playback_fake_resource=playback_fake_resource,
                                                     client_kwargs=client_kwargs)
        self.parameter_name = parameter_name
        self.access_rights = access_rights
        self.servicebus_queue_parameter_name = servicebus_queue_parameter_name
        if random_name_enabled:
            self.resource_moniker = self.name_prefix + "sbqueueauth"
        self.set_cache(use_cache, access_rights)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(ServiceBusManagementClient, base_url=BASE_URL, credential_scopes=CREDENTIAL_SCOPES)
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            queue = self._get_queue(**kwargs)
            retries = 4
            for i in range(retries):
                try:
                    self.resource = self.client.queues.create_or_update_authorization_rule(
                        group.name,
                        namespace.name,
                        queue.name,
                        name,
                        SBAuthorizationRule(rights=self.access_rights)
                    )
                    break
                except Exception as ex:
                    error = "The requested resource {} does not exist".format(namespace)
                    not_found_error = "Operation returned an invalid status code 'Not Found'"
                    if (error not in str(ex) and not_found_error not in str(ex)) or i == retries - 1:
                        raise
                    time.sleep(3)

            key = self.client.queues.list_keys(group.name, namespace.name, queue.name, name)
            connection_string = key.primary_connection_string

            self.test_class_instance.scrubber.register_name_pair(
                name,
                self.resource_moniker
            )
        else:
            self.resource = FakeResource(name=name, id=name)
            connection_string = 'https://microsoft.com'
        return {
            self.parameter_name: self.resource,
            '{}_connection_string'.format(self.parameter_name): connection_string,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            namespace = self._get_namespace(**kwargs)
            queue = self._get_queue(**kwargs)
            self.client.queues.delete_authorization_rule(group.name, namespace.name, queue.name, name)

    def _get_queue(self, **kwargs):
        try:
            return kwargs.get(self.servicebus_queue_parameter_name)
        except KeyError:
            template = 'To create this service bus queue authorization rule a service bus queue is required. Please add ' \
                       'decorator @{} in front of this service bus preparer.'
            raise AzureTestError(template.format(ServiceBusQueuePreparer.__name__))


CachedServiceBusResourceGroupPreparer = functools.partial(ServiceBusResourceGroupPreparer, use_cache=True, random_name_enabled=True)
CachedServiceBusNamespacePreparer = functools.partial(ServiceBusNamespacePreparer, use_cache=True)
CachedServiceBusQueuePreparer = functools.partial(ServiceBusQueuePreparer, use_cache=True)
CachedServiceBusTopicPreparer = functools.partial(ServiceBusTopicPreparer, use_cache=True)
CachedServiceBusSubscriptionPreparer = functools.partial(ServiceBusSubscriptionPreparer, use_cache=True)
