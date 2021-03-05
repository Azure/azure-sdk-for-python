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

from azure_devtools.scenario_tests import AzureTestError, ReservedResourceNameError

from azure.mgmt.resource import ResourceManagementClient

from . import AzureMgmtPreparer


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
        delete_after_tag_timedelta=datetime.timedelta(days=1),
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

    def create_resource(self, name, **kwargs):
        if self.is_live and self._need_creation:
            self.client = self.create_mgmt_client(ResourceManagementClient)
            parameters = {"location": self.location}
            if self.delete_after_tag_timedelta:
                expiry = datetime.datetime.utcnow() + self.delete_after_tag_timedelta
                parameters["tags"] = {
                    "DeleteAfter": expiry.replace(microsecond=0).isoformat()
                }
            try:
                self.resource = self.client.resource_groups.create_or_update(
                    name, parameters
                )
            except Exception as ex:
                if "ReservedResourceName" in str(ex):
                    raise ReservedResourceNameError(name)
                raise
        else:
            self.resource = self.resource or FakeResource(
                name=name,
                id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/"
                + name,
            )
        if name != self.moniker:
            self.test_class_instance.scrubber.register_name_pair(name, self.moniker)
        return {
            self.parameter_name: self.resource,
            self.parameter_name_for_location: self.location,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live and self._need_creation:
            try:
                if "wait_timeout" in kwargs:
                    azure_poller = self.client.resource_groups.delete(name)
                    azure_poller.wait(kwargs.get("wait_timeout"))
                    if azure_poller.done():
                        return
                    raise AzureTestError(
                        "Timed out waiting for resource group to be deleted."
                    )
                else:
                    self.client.resource_groups.delete(name, polling=False)
            except Exception:
                pass


RandomNameResourceGroupPreparer = functools.partial(
    ResourceGroupPreparer, random_name_enabled=True
)
CachedResourceGroupPreparer = functools.partial(
    ResourceGroupPreparer, use_cache=True, random_name_enabled=True
)
