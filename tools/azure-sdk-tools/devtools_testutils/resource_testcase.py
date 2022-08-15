# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from collections import namedtuple
import functools
import os
import datetime
import logging

from azure_devtools.scenario_tests import AzureTestError, ReservedResourceNameError

from azure.mgmt.resource import ResourceManagementClient

from . import AzureMgmtPreparer
from .sanitizers import add_general_regex_sanitizer


logging.getLogger().setLevel(logging.INFO)


RESOURCE_GROUP_PARAM = "resource_group"


FakeResource = namedtuple("FakeResource", ["name", "id"])


class ResourceGroupPreparer(AzureMgmtPreparer):
    def __init__(
        self,
        name_prefix="",
        use_cache=False,
        random_name_length=75,
        parameter_name=RESOURCE_GROUP_PARAM,
        parameter_name_for_location="location",
        location="westus",
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=False,
        delete_after_tag_timedelta=datetime.timedelta(hours=8),
    ):
        super(ResourceGroupPreparer, self).__init__(
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
        name = u"rgpy-" + name
        if len(name) > 90:
            name = name[:90]
        return name

    def create_resource(self, name, **kwargs):
        if self.is_live and self._need_creation:
            self.client = self.create_mgmt_client(ResourceManagementClient)
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
            except Exception as err:  # NOTE: some track 1 libraries do not have azure-core installed. Cannot use HttpResponseError here
                logging.info("Failed to delete resource group with name {}".format(name))
                logging.info("{}".format(err))
                pass


RandomNameResourceGroupPreparer = functools.partial(ResourceGroupPreparer, random_name_enabled=True)
CachedResourceGroupPreparer = functools.partial(ResourceGroupPreparer, use_cache=True, random_name_enabled=True)
