#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
from collections import namedtuple
import inspect
import os.path
import zlib

from azure_devtools.scenario_tests import (
    ReplayableTest, AzureTestError,
    AbstractPreparer, GeneralNameReplacer,
    OAuthRequestResponsesFilter, DeploymentNameReplacer,
    RequestUrlNormalizer
)
from .config import TEST_SETTING_FILENAME
from . import mgmt_settings_fake as fake_settings


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
    checksum = zlib.adler32(identifier) & 0xffffffff
    name = '{}{}'.format(name_prefix, hex(checksum)[2:]).rstrip('L')
    if name.endswith('L'):
        name = name[:-1]
    return name


def get_qualified_method_name(obj, method_name):
    # example of qualified test name:
    # test_mgmt_network.test_public_ip_addresses
    _, filename = os.path.split(inspect.getsourcefile(type(obj)))
    module_name, _ = os.path.splitext(filename)
    return '{0}.{1}'.format(module_name, method_name)


class AzureMgmtTestCase(ReplayableTest):
    def __init__(self, method_name, config_file=None,
                 recording_dir=None, recording_name=None,
                 recording_processors=None, replay_processors=None,
                 recording_patches=None, replay_patches=None):
        self.working_folder = os.path.dirname(__file__)
        self.qualified_test_name = get_qualified_method_name(self, method_name)
        self._fake_settings, self._real_settings = self._load_settings()
        self.region = 'westus'
        self.scrubber = GeneralNameReplacer()
        config_file = config_file or os.path.join(self.working_folder, TEST_SETTING_FILENAME)
        if not os.path.exists(config_file):
            config_file = None
        super(AzureMgmtTestCase, self).__init__(
            method_name,
            config_file=config_file,
            recording_dir=recording_dir,
            recording_name=recording_name or self.qualified_test_name,
            recording_processors=recording_processors or self._get_recording_processors(),
            replay_processors=replay_processors or self._get_replay_processors(),
            recording_patches=recording_patches,
            replay_patches=replay_patches,
        )

    @property
    def settings(self):
        if self.is_live:
            if self._real_settings:
                return self._real_settings
            else:
                raise AzureTestError('Need a mgmt_settings_real.py file to run tests live.')
        else:
            return self._fake_settings

    def _load_settings(self):
        try:
            from . import mgmt_settings_real as real_settings
            return fake_settings, real_settings
        except ImportError:
            return fake_settings, None

    def _get_recording_processors(self):
        return [
            self.scrubber,
            OAuthRequestResponsesFilter(),
            # DeploymentNameReplacer(), Not use this one, give me full control on deployment name
            RequestUrlNormalizer()
        ]

    def _get_replay_processors(self):
        return [
            RequestUrlNormalizer()
        ]

    def is_playback(self):
        return not self.is_live

    def _setup_scrubber(self):
        constants_to_scrub = ['SUBSCRIPTION_ID', 'AD_DOMAIN', 'TENANT_ID', 'CLIENT_OID', 'ADLA_JOB_ID']
        for key in constants_to_scrub:
            if hasattr(self.settings, key) and hasattr(self._fake_settings, key):
                self.scrubber.register_name_pair(getattr(self.settings, key),
                                                 getattr(self._fake_settings, key))

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
        self._setup_scrubber()
        super(AzureMgmtTestCase, self).setUp()

    def tearDown(self):
        return super(AzureMgmtTestCase, self).tearDown()

    def create_basic_client(self, client_class, **kwargs):
        # Whatever the client, if credentials is None, fail
        with self.assertRaises(ValueError):
            client = client_class(
                credentials=None,
                **kwargs
            )

        # Real client creation
        client = client_class(
            credentials=self.settings.get_credentials(),
            **kwargs
        )
        if self.is_playback():
            client.config.long_running_operation_timeout = 0
        client.config.enable_http_logger = True
        return client

    def create_mgmt_client(self, client_class, **kwargs):
        # Whatever the client, if subscription_id is None, fail
        with self.assertRaises(ValueError):
            self.create_basic_client(
                client_class,
                subscription_id=None,
                **kwargs
            )

        return self.create_basic_client(
            client_class,
            subscription_id=self.settings.SUBSCRIPTION_ID,
            **kwargs
        )

    def create_random_name(self, name):
        return get_resource_name(name, self.qualified_test_name.encode())

    def get_resource_name(self, name):
        """Alias to create_random_name for back compatibility."""
        return self.create_random_name(name)

    def get_preparer_resource_name(self, prefix):
        """Random name generation for use by preparers.

        If prefix is a blank string, use the fully qualified test name instead.
        This is what legacy tests do for resource groups."""
        return self.get_resource_name(prefix or self.qualified_test_name.replace('.', '_'))


class AzureMgmtPreparer(AbstractPreparer):
    def __init__(self, name_prefix, random_name_length,
                 disable_recording=True,
                 playback_fake_resource=None,
                 client_kwargs=None):
        super(AzureMgmtPreparer, self).__init__(name_prefix, random_name_length,
                                                disable_recording=disable_recording)
        self.client = None
        self.resource = playback_fake_resource
        self.client_kwargs = client_kwargs or {}

    @property
    def is_live(self):
        return self.test_class_instance.is_live

    def create_random_name(self):
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

    def create_mgmt_client(self, client_class):
        return client_class(
            credentials=self.test_class_instance.settings.get_credentials(),
            subscription_id=self.test_class_instance.settings.SUBSCRIPTION_ID,
            **self.client_kwargs
        )
