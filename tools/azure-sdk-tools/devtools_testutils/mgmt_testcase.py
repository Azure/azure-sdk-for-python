# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import inspect
import re
import six
import os.path
import zlib

from azure_devtools.scenario_tests import AbstractPreparer, GeneralNameReplacer
from azure_devtools.scenario_tests.utilities import is_text_payload


class HttpStatusCode(object):
    OK = 200
    Created = 201
    Accepted = 202
    NoContent = 204
    NotFound = 404


def get_resource_name(name_prefix, identifier):
    # Append a suffix to the name, based on the fully qualified test name
    # We use a checksum of the test name so that each test gets different
    # resource names, but each test will get the same name on repeat runs,
    # which is needed for playback.
    # Most resource names have a length limit, so we use a crc32
    checksum = zlib.adler32(identifier) & 0xFFFFFFFF
    name = "{}{}".format(name_prefix, hex(checksum)[2:]).rstrip("L")
    if name.endswith("L"):
        name = name[:-1]
    return name


def get_qualified_method_name(obj, method_name):
    # example of qualified test name:
    # test_mgmt_network.test_public_ip_addresses
    _, filename = os.path.split(inspect.getsourcefile(type(obj)))
    module_name, _ = os.path.splitext(filename)
    return "{0}.{1}".format(module_name, method_name)


class AzureMgmtPreparer(AbstractPreparer):
    def __init__(
        self,
        name_prefix,
        random_name_length,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=False,
    ):
        super(AzureMgmtPreparer, self).__init__(name_prefix, random_name_length, disable_recording=disable_recording)
        self.client = None
        self.resource = playback_fake_resource
        self.client_kwargs = client_kwargs or {}
        self.random_name_enabled = random_name_enabled

    @property
    def is_live(self):
        return self.test_class_instance.is_live

    def create_random_name(self):
        if self.random_name_enabled:
            return super(AzureMgmtPreparer, self).create_random_name()
        return self.test_class_instance.get_preparer_resource_name(self.name_prefix)

    @property
    def moniker(self):
        """Override moniker generation for backwards compatibility.

        azure-devtools preparers, by default, generate "monikers" which replace
        resource names in request URIs by tacking on a resource count to
        name_prefix. By contrast, SDK tests used the fully qualified (module + method)
        test name and the hashing process in get_resource_name.

        This property override implements the SDK test name generation so that
        the URIs don't change and tests don't need to be re-recorded.
        """
        if not self.resource_moniker:
            self.resource_moniker = self.random_name
        return self.resource_moniker

    def create_mgmt_client(self, client_class, **kwargs):
        return self.test_class_instance.create_mgmt_client(client_class, **kwargs)


class RENameReplacer(GeneralNameReplacer):
    def __init__(self):
        super(RENameReplacer, self).__init__()
        self.patterns = []

    def register_pattern_pair(self, expr, new):
        self.patterns.append((expr, new))

    def process_request(self, request):
        request = super(RENameReplacer, self).process_request(request)
        for expr, new in self.patterns:
            if is_text_payload(request) and request.body:
                if isinstance(request.body, dict):
                    continue

                body = six.ensure_str(request.body)
                for old in re.findall(expr, body):
                    request.body = body.replace(old, new)
        return request

    def process_response(self, response):
        response = super(RENameReplacer, self).process_response(response)
        for expr, new in self.patterns:
            if is_text_payload(response) and response["body"]["string"]:
                if isinstance(response["body"]["string"], bytes):
                    body = response["body"]["string"].decode("utf8", "backslashreplace")
                else:
                    body = response["body"]["string"]

                for old in re.findall(expr, body):
                    body = body.replace(old, new)

                if isinstance(response["body"]["string"], bytes):
                    response["body"]["string"] = body.encode("utf8", "backslashreplace")
                else:
                    response["body"]["string"] = body
        return response
