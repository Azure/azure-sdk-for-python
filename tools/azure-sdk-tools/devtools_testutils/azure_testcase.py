# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import inspect
import logging
import os.path
import sys
import zlib
import pytest
from dotenv import load_dotenv, find_dotenv

from azure_devtools.scenario_tests import (
    ReplayableTest,
    AzureTestError,
    GeneralNameReplacer,
    RequestUrlNormalizer,
    AuthenticationMetadataFilter,
    OAuthRequestResponsesFilter,
)
from azure_devtools.scenario_tests.config import TestConfig
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function

from .azure_unit_test import AzureUnitTest
from .config import TEST_SETTING_FILENAME
from . import mgmt_settings_fake as fake_settings

try:
    # Try to import the AsyncFakeCredential, if we cannot assume it is Python 2
    from .fake_async_credential import AsyncFakeCredential
except SyntaxError:
    pass


class HttpStatusCode(object):
    OK = 200
    Created = 201
    Accepted = 202
    NoContent = 204
    NotFound = 404


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


class AzureTestCase(ReplayableTest, AzureUnitTest):
    def __init__(
        self,
        method_name,
        config_file=None,
        recording_dir=None,
        recording_name=None,
        recording_processors=None,
        replay_processors=None,
        recording_patches=None,
        replay_patches=None,
        **kwargs
    ):
        self.working_folder = os.path.dirname(__file__)
        self.qualified_test_name = get_qualified_method_name(self, method_name)
        self._fake_settings, self._real_settings = self._load_settings()
        self.scrubber = GeneralNameReplacer()
        config_file = config_file or os.path.join(
            self.working_folder, TEST_SETTING_FILENAME
        )
        if not os.path.exists(config_file):
            config_file = None
        load_dotenv(find_dotenv())
        super(AzureTestCase, self).__init__(
            method_name,
            config_file=config_file,
            recording_dir=recording_dir,
            recording_name=recording_name or self.qualified_test_name,
            recording_processors=recording_processors
            or self._get_recording_processors(),
            replay_processors=replay_processors or self._get_replay_processors(),
            recording_patches=recording_patches,
            replay_patches=replay_patches,
            **kwargs
        )

    def _get_recording_processors(self):
        return [
            self.scrubber,
            AuthenticationMetadataFilter(),
            OAuthRequestResponsesFilter(),
            RequestUrlNormalizer(),
        ]

    def _get_replay_processors(self):
        return [RequestUrlNormalizer()]

    def is_playback(self):
        return not self.is_live

    def set_value_to_scrub(self, key, default_value):
        if self.is_live:
            value = self.get_settings_value(key)
            self.scrubber.register_name_pair(value, default_value)
            return value
        else:
            return default_value

    def setUp(self):
        # Every test uses a different resource group name calculated from its
        # qualified test name.
        #
        # When running all tests serially, this allows us to delete
        # the resource group in teardown without waiting for the delete to
        # complete. The next test in line will use a different resource group,
        # so it won't have any trouble creating its resource group even if the
        # previous test resource group hasn't finished deleting.
        #
        # When running tests individually, if you try to run the same test
        # multiple times in a row, it's possible that the delete in the previous
        # teardown hasn't completed yet (because we don't wait), and that
        # would make resource group creation fail.
        # To avoid that, we also delete the resource group in the
        # setup, and we wait for that delete to complete.
        super(AzureTestCase, self).setUp()

    def tearDown(self):
        return super(AzureTestCase, self).tearDown()

    def get_replayable_random_resource_name(self, name):
        """In a replay scenario, (is not live) gives the static moniker.  In the random scenario, gives generated name."""
        if self.is_live:
            created_name = self.create_random_name(name)
            self.scrubber.register_name_pair(created_name, name)
        return name

    @staticmethod
    def await_prepared_test(test_fn):
        """Synchronous wrapper for async test methods. Used to avoid making changes
        upstream to AbstractPreparer, which only awaits async tests that use preparers.
        (Add @AzureTestCase.await_prepared_test decorator to async tests without preparers)

        # Note: this will only be needed so long as we maintain unittest.TestCase in our
        test-class inheritance chain.
        """

        if sys.version_info < (3, 5):
            raise ImportError("Async wrapper is not needed for Python 2.7 code.")

        import asyncio

        @functools.wraps(test_fn)
        def run(test_class_instance, *args, **kwargs):
            trim_kwargs_from_test_function(test_fn, kwargs)
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(test_fn(test_class_instance, **kwargs))

        return run
