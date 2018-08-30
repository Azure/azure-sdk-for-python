#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
from azure.profiles import ProfileDefinition, KnownProfiles
from azure.profiles.multiapiclient import MultiApiClientMixin

import pytest

def test_profile_from_string():
    profile_from_string = KnownProfiles.from_name("2017-03-09-profile")
    assert profile_from_string is KnownProfiles.v2017_03_09_profile

    with pytest.raises(ValueError):
        KnownProfiles.from_name("blablabla")

def test_default_profile():
    with pytest.raises(ValueError):
        KnownProfiles.default.use("This is not a profile")

def test_multiapi_client():

    class SDKClient(object):
        # Mock msrest.SDKClient to not import it
        def __init__(self, creds, config):
            assert creds == "creds"
            assert config == "config"

    class TestClient(MultiApiClientMixin, SDKClient):
        DEFAULT_API_VERSION = "2216-08-09"
        _PROFILE_TAG = "azure.mgmt.compute.ComputeManagementClient"
        LATEST_PROFILE = ProfileDefinition({
            _PROFILE_TAG: {
                None: DEFAULT_API_VERSION
            }},
            _PROFILE_TAG + " latest"
        )

        def __init__(self, creds="creds", config="config", api_version=None, profile=KnownProfiles.default):
            super(TestClient, self).__init__(
                creds,
                config,
                api_version=api_version,
                profile=profile
            )

        def operations(self):
            return self._get_api_version("operations")

    # By default, use latest
    client = TestClient()
    assert client.operations() == TestClient.DEFAULT_API_VERSION

    # Dynamically change to a new profile
    KnownProfiles.default.use(KnownProfiles.v2017_03_09_profile)
    assert client.operations() == "2016-03-30"

    # I ask explicitly latest, where the default is not that
    client = TestClient(profile=KnownProfiles.latest)
    assert client.operations() == TestClient.DEFAULT_API_VERSION

    # Bring back default to latest for next tests
    KnownProfiles.default.use(KnownProfiles.latest)

    # I asked explicily a specific profile, must not be latest
    client = TestClient(profile=KnownProfiles.v2017_03_09_profile)
    assert client.operations() == "2016-03-30"

    # I refuse api_version and profile at the same time
    # https://github.com/Azure/azure-sdk-for-python/issues/1864
    with pytest.raises(ValueError):
        TestClient(api_version="something", profile=KnownProfiles.latest)

    # If I provide only api_version, this creates a profile with just that
    client = TestClient(api_version="2666-05-15")
    assert client.operations() == "2666-05-15"

    # I can specify old profile syntax with dict
    client = TestClient(profile={
        "operations": "1789-07-14"
    })
    assert client.operations() == "1789-07-14"

    # If I give a profile definition with no default api-version
    # and I call a method not define in the profile, this fails
    client = TestClient(profile={
        "operations2": "1789-07-14"
    })
    with pytest.raises(ValueError):
        client.operations() == "1789-07-14"

def test_multiapi_client_legacy():
    """The messed-up way old Profile was.
    Note that this was only released on RC packages, so as soon as the
    CLI does not use RC packages anymore, I have no trouble to
    remove that legacy.
    """

    class TestClient(MultiApiClientMixin):
        DEFAULT_API_VERSION = "2216-08-09"
        _PROFILE_TAG = "azure.mgmt.compute.ComputeManagementClient"
        LATEST_PROFILE = ProfileDefinition({
            _PROFILE_TAG: {
                None: DEFAULT_API_VERSION
            }},
            _PROFILE_TAG + " latest"
        )

        def __init__(self, creds="creds", config="config", api_version=None, profile=KnownProfiles.default):
            super(TestClient, self).__init__(
                credentials="credentials",
                subscription_id="subscription_id",
                api_version=api_version,
                base_url="base_url",
                profile=profile
            )

        def operations(self):
            return self._get_api_version("operations")

    # Creating a client that does not raise with:
    # TypeError: object.__init__() takes no parameters
    # is enough to show the legacy work
    TestClient()
