# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import inspect
import os.path
import zlib

from .config import TEST_SETTING_FILENAME, TestConfig


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


def is_live():
    """A module version of is_live, that could be used in pytest marker."""
    if not hasattr(is_live, "_cache"):
        config_file = os.path.join(os.path.dirname(__file__), TEST_SETTING_FILENAME)
        if not os.path.exists(config_file):
            config_file = None
        is_live._cache = TestConfig(config_file=config_file).record_mode
    return is_live._cache


def get_region_override(default="westus"):
    region = os.environ.get("RESOURCE_REGION", None) or default
    if not region:
        raise ValueError(
            "Region should not be None; set a non-empty-string region to either the RESOURCE_REGION environment variable or the default parameter to this function."
        )
    return region


def _is_autorest_v3(client_class):
    """Is this client a autorest v3/track2 one?

    Could be refined later if necessary.
    """
    args = inspect.getfullargspec(client_class.__init__).args
    return "credential" in args
