# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
import functools
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from azure.core.exceptions import ResourceNotFoundError
from azure.iot.modelsrepository import (
    ModelsRepositoryClient,
    DEPENDENCY_MODE_ENABLED,
    DEPENDENCY_MODE_DISABLED,
    DEPENDENCY_MODE_TRY_FROM_EXPANDED,
    ModelError,
)
from azure.iot.modelsrepository._resolver import HttpFetcher

pytestmark = pytest.mark.usefixtures("recorded_test")

LOCAL_REPO = "Local Repository"
REMOTE_REPO = "Remote Repository"


@pytest.fixture(params=[REMOTE_REPO, LOCAL_REPO], autouse=True)
def client_type(request):
    return request.param


@pytest.fixture
def client(client_type):
    if client_type == REMOTE_REPO:
        client = ModelsRepositoryClient()
    elif client_type == LOCAL_REPO:
        test_dir = os.path.dirname(os.path.abspath(__file__))
        local_repo = os.path.join(test_dir, "local_repository")
        client = ModelsRepositoryClient(repository_location=local_repo)
    else:
        raise Exception("Bad fixture")
    yield client
    client.close()


def skip_remote(test_fn):
    """This decorator can be added to a test function to skip it for remote clients if
    insufficent data exists on the remote test repository"""
    @functools.wraps(test_fn)
    def wrapper(*args, **kwargs):
        # A bit of a hack - since we can't easily access the client_type fixture here,
        # instead check the type of the client's fetcher. HttpFetcher means remote.
        client = kwargs["client"]
        if type(client.fetcher) is HttpFetcher:
            return pytest.skip("Insufficient test data")
        else:
            return test_fn(*args, **kwargs)
    return wrapper


@pytest.mark.describe(".get_models() - Dependency Mode: Enabled")
class TestGetModelsDependencyModeEnabled(AzureRecordedTestCase):
    @pytest.mark.parametrize("dtmi", [
        pytest.param("dtmi:com:example:Thermostat:1", id="No semicolon"),
        pytest.param("dtmi:com:example::Thermostat;1", id="Double colon"),
        pytest.param("com:example:Thermostat;1", id="No DTMI prefix"),
    ])
    def test_invalid_dtmi_format(self, client, dtmi):
        with pytest.raises(ValueError):
            client.get_models(dtmi, dependency_resolution=DEPENDENCY_MODE_ENABLED)

    def test_dtmi_mismatch_casing(self, client):
        dtmi = "dtmi:com:example:thermostat;1"
        with pytest.raises(ModelError):
            client.get_models(dtmi, dependency_resolution=DEPENDENCY_MODE_ENABLED)

    def test_nonexistant_dtdl_doc(self, client):
        dtmi = "dtmi:com:example:thermojax;999"
        with pytest.raises(ResourceNotFoundError):
            client.get_models(dtmi)

    def test_nonexistent_dependency_dtdl_doc(self, client):
        dtmi = "dtmi:com:example:invalidmodel;1"
        with pytest.raises(ResourceNotFoundError):
            client.get_models(dtmi)

    def test_single_dtmi_no_components_no_extends(self, client):
        dtmi = "dtmi:com:example:Thermostat;1"
        model_map = client.get_models(dtmi, dependency_resolution=DEPENDENCY_MODE_ENABLED)

        assert len(model_map) == 1
        assert dtmi in model_map.keys()
        model = model_map[dtmi]
        assert model["@id"] == dtmi

    def test_multiple_dtmis_no_components_no_extends(self, client):
        dtmi1 = "dtmi:com:example:Thermostat;1"
        dtmi2 = "dtmi:azure:DeviceManagement:DeviceInformation;1"
        model_map = client.get_models(
            [dtmi1, dtmi2], dependency_resolution=DEPENDENCY_MODE_ENABLED
        )

        assert len(model_map) == 2
        assert dtmi1 in model_map.keys()
        assert dtmi2 in model_map.keys()
        model1 = model_map[dtmi1]
        model2 = model_map[dtmi2]
        assert model1["@id"] == dtmi1
        assert model2["@id"] == dtmi2

    def test_single_dtmi_with_component_deps(self, client):
        root_dtmi = "dtmi:com:example:TemperatureController;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
        ]
        expected_dtmis = [root_dtmi] + expected_deps
        model_map = client.get_models(root_dtmi, dependency_resolution=DEPENDENCY_MODE_ENABLED)

        assert len(model_map) == len(expected_dtmis)
        for dtmi in expected_dtmis:
            assert dtmi in model_map.keys()
            model = model_map[dtmi]
            assert model["@id"] == dtmi

    @skip_remote
    def test_multiple_dtmis_with_component_deps(self, client):
        root_dtmi1 = "dtmi:com:example:Phone;2"
        root_dtmi2 = "dtmi:com:example:TemperatureController;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;2",
            "dtmi:com:example:Camera;3",
        ]
        expected_dtmis = [root_dtmi1, root_dtmi2] + expected_deps
        model_map = client.get_models(
            [root_dtmi1, root_dtmi2], dependency_resolution=DEPENDENCY_MODE_ENABLED
        )

        assert len(model_map) == len(expected_dtmis)
        for dtmi in expected_dtmis:
            assert dtmi in model_map.keys()
            model = model_map[dtmi]
            assert model["@id"] == dtmi

    @skip_remote
    def test_multiple_dtmis_with_extends_deps_single_dtmi(self, client, client_type):
        root_dtmi1 = "dtmi:com:example:TemperatureController;1"
        root_dtmi2 = "dtmi:com:example:ConferenceRoom;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
            "dtmi:com:example:Room;1",
        ]
        expected_dtmis = [root_dtmi1, root_dtmi2] + expected_deps
        model_map = client.get_models(
            [root_dtmi1, root_dtmi2], dependency_resolution=DEPENDENCY_MODE_ENABLED
        )

        assert len(model_map) == len(expected_dtmis)
        for dtmi in expected_dtmis:
            assert dtmi in model_map.keys()
            model = model_map[dtmi]
            assert model["@id"] == dtmi

    @skip_remote
    def test_multiple_dtmis_with_extends_deps_multiple_dtmi(self, client):
        root_dtmi1 = "dtmi:com:example:TemperatureController;1"
        root_dtmi2 = "dtmi:com:example:ColdStorage;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
            "dtmi:com:example:Room;1",
            "dtmi:com:example:Freezer;1",
        ]
        expected_dtmis = [root_dtmi1, root_dtmi2] + expected_deps
        model_map = client.get_models(
            [root_dtmi1, root_dtmi2], dependency_resolution=DEPENDENCY_MODE_ENABLED
        )

        assert len(model_map) == len(expected_dtmis)
        for dtmi in expected_dtmis:
            assert dtmi in model_map.keys()
            model = model_map[dtmi]
            assert model["@id"] == dtmi

    @skip_remote
    def test_single_dtmi_with_extends_single_model_inline(self, client, client_type):
        dtmi = "dtmi:com:example:base;1"
        model_map = client.get_models(dtmi, dependency_resolution=DEPENDENCY_MODE_ENABLED)

        assert len(model_map) == 1
        assert dtmi in model_map.keys()
        model = model_map[dtmi]
        assert model["@id"] == dtmi

    @skip_remote
    def test_single_dtmi_with_extends_mixed_inline_and_dtmi(self, client, client_type):
        root_dtmi = "dtmi:com:example:base;2"
        expected_deps = ["dtmi:com:example:Freezer;1", "dtmi:com:example:Thermostat;1"]
        expected_dtmis = [root_dtmi] + expected_deps
        model_map = client.get_models(root_dtmi, dependency_resolution=DEPENDENCY_MODE_ENABLED)

        assert len(model_map) == len(expected_dtmis)
        for dtmi in expected_dtmis:
            assert dtmi in model_map.keys()
            model = model_map[dtmi]
            assert model["@id"] == dtmi

    @recorded_by_proxy
    def test_duplicate_dtmi(self, client):
        dtmi1 = "dtmi:azure:DeviceManagement:DeviceInformation;1"
        dtmi2 = "dtmi:azure:DeviceManagement:DeviceInformation;1"
        model_map = client.get_models(
            [dtmi1, dtmi1], dependency_resolution=DEPENDENCY_MODE_ENABLED
        )

        assert len(model_map) == 1
        assert dtmi1 in model_map.keys()
        assert dtmi2 in model_map.keys()
        model = model_map[dtmi1]
        assert model["@id"] == dtmi1 == dtmi2


@pytest.mark.describe(".get_models() - Dependency Mode: Disabled")
class TestGetModelsDependencyModeDisabled(AzureRecordedTestCase):
    @pytest.mark.parametrize("dtmi", [
        pytest.param("dtmi:com:example:Thermostat:1", id="No semicolon"),
        pytest.param("dtmi:com:example::Thermostat;1", id="Double colon"),
        pytest.param("com:example:Thermostat;1", id="No DTMI prefix"),
    ])
    def test_invalid_dtmi_format(self, client, dtmi):
        with pytest.raises(ValueError):
            client.get_models(dtmi, dependency_resolution=DEPENDENCY_MODE_DISABLED)

    def test_dtmi_mismatch_casing(self, client):
        dtmi = "dtmi:com:example:thermostat;1"
        with pytest.raises(ModelError):
            client.get_models(dtmi, dependency_resolution=DEPENDENCY_MODE_DISABLED)

    def test_nonexistant_dtdl_doc(self, client):
        dtmi = "dtmi:com:example:thermojax;999"
        with pytest.raises(ResourceNotFoundError):
            client.get_models(dtmi)

    def test_nonexistent_dependency_dtdl_doc(self, client):
        dtmi = "dtmi:com:example:invalidmodel;1"
        with pytest.raises(ResourceNotFoundError):
            client.get_models(dtmi)

    def test_single_dtmi_no_components_no_extends(self, client):
        dtmi = "dtmi:com:example:Thermostat;1"
        model_map = client.get_models(dtmi, dependency_resolution=DEPENDENCY_MODE_DISABLED)

        assert len(model_map) == 1
        assert dtmi in model_map.keys()
        model = model_map[dtmi]
        assert model["@id"] == dtmi

    def test_multiple_dtmis_no_components_no_extends(self, client):
        dtmi1 = "dtmi:com:example:Thermostat;1"
        dtmi2 = "dtmi:azure:DeviceManagement:DeviceInformation;1"
        model_map = client.get_models(
            [dtmi1, dtmi2], dependency_resolution=DEPENDENCY_MODE_DISABLED
        )

        assert len(model_map) == 2
        assert dtmi1 in model_map.keys()
        assert dtmi2 in model_map.keys()
        model1 = model_map[dtmi1]
        model2 = model_map[dtmi2]
        assert model1["@id"] == dtmi1
        assert model2["@id"] == dtmi2

    def test_single_dtmi_with_component_deps(self, client):
        dtmi = "dtmi:com:example:TemperatureController;1"
        model_map = client.get_models(dtmi, dependency_resolution=DEPENDENCY_MODE_DISABLED)

        assert len(model_map) == 1
        assert dtmi in model_map.keys()
        model = model_map[dtmi]
        assert model["@id"] == dtmi

    @skip_remote
    def test_multiple_dtmis_with_component_deps(self, client):
        dtmi1 = "dtmi:com:example:Phone;2"
        dtmi2 = "dtmi:com:example:TemperatureController;1"
        model_map = client.get_models(
            [dtmi1, dtmi2], dependency_resolution=DEPENDENCY_MODE_DISABLED
        )

        assert len(model_map) == 2
        assert dtmi1 in model_map.keys()
        assert dtmi2 in model_map.keys()
        model1 = model_map[dtmi1]
        model2 = model_map[dtmi2]
        assert model1["@id"] == dtmi1
        assert model2["@id"] == dtmi2

    @skip_remote
    def test_multiple_dtmis_with_extends_deps_single_dtmi(self, client):
        dtmi1 = "dtmi:com:example:TemperatureController;1"
        dtmi2 = "dtmi:com:example:ConferenceRoom;1"
        model_map = client.get_models(
            [dtmi1, dtmi2], dependency_resolution=DEPENDENCY_MODE_DISABLED
        )

        assert len(model_map) == 2
        assert dtmi1 in model_map.keys()
        assert dtmi2 in model_map.keys()
        model1 = model_map[dtmi1]
        model2 = model_map[dtmi2]
        assert model1["@id"] == dtmi1
        assert model2["@id"] == dtmi2

    @skip_remote
    def test_multiple_dtmis_with_extends_deps_multiple_dtmi(self, client):
        dtmi1 = "dtmi:com:example:TemperatureController;1"
        dtmi2 = "dtmi:com:example:ColdStorage;1"
        model_map = client.get_models(
            [dtmi1, dtmi2], dependency_resolution=DEPENDENCY_MODE_DISABLED
        )

        assert len(model_map) == 2
        assert dtmi1 in model_map.keys()
        assert dtmi2 in model_map.keys()
        model1 = model_map[dtmi1]
        model2 = model_map[dtmi2]
        assert model1["@id"] == dtmi1
        assert model2["@id"] == dtmi2

    @skip_remote
    def test_single_dtmi_with_extends_single_model_inline(self, client):
        dtmi = "dtmi:com:example:base;1"
        model_map = client.get_models(dtmi, dependency_resolution=DEPENDENCY_MODE_DISABLED)

        assert len(model_map) == 1
        assert dtmi in model_map.keys()
        model = model_map[dtmi]
        assert model["@id"] == dtmi

    @skip_remote
    def test_single_dtmi_with_extends_mixed_inline_and_dtmi(self, client):
        dtmi = "dtmi:com:example:base;2"
        model_map = client.get_models(dtmi, dependency_resolution=DEPENDENCY_MODE_DISABLED)

        assert len(model_map) == 1
        assert dtmi in model_map.keys()
        model = model_map[dtmi]
        assert model["@id"] == dtmi

    def test_duplicate_dtmi(self, client):
        dtmi1 = "dtmi:azure:DeviceManagement:DeviceInformation;1"
        dtmi2 = "dtmi:azure:DeviceManagement:DeviceInformation;1"
        model_map = client.get_models(
            [dtmi1, dtmi1], dependency_resolution=DEPENDENCY_MODE_DISABLED
        )

        assert len(model_map) == 1
        assert dtmi1 in model_map.keys()
        assert dtmi2 in model_map.keys()
        model = model_map[dtmi1]
        assert model["@id"] == dtmi1 == dtmi2


@pytest.mark.describe(".get_models() - Dependency Mode: Try From Expanded")
class TestGetModelsDependencyModeTryFromExpanded(AzureRecordedTestCase):
    @pytest.mark.parametrize("dtmi", [
        pytest.param("dtmi:com:example:Thermostat:1", id="No semicolon"),
        pytest.param("dtmi:com:example::Thermostat;1", id="Double colon"),
        pytest.param("com:example:Thermostat;1", id="No DTMI prefix"),
    ])
    def test_invalid_dtmi_format(self, dtmi, client):
        with pytest.raises(ValueError):
            client.get_models(dtmi, dependency_resolution=DEPENDENCY_MODE_TRY_FROM_EXPANDED)

    def test_dtmi_mismatch_casing(self, client):
        dtmi = "dtmi:com:example:thermostat;1"
        with pytest.raises(ModelError):
            client.get_models(dtmi, dependency_resolution=DEPENDENCY_MODE_TRY_FROM_EXPANDED)

    def test_nonexistant_dtdl_doc(self, client):
        dtmi = "dtmi:com:example:thermojax;999"
        with pytest.raises(ResourceNotFoundError):
            client.get_models(dtmi)

    def test_single_dtmi_with_component_deps_expanded_json(self, client):
        root_dtmi = "dtmi:com:example:TemperatureController;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
        ]
        expected_dtmis = [root_dtmi] + expected_deps
        model_map = client.get_models(
            root_dtmi, dependency_resolution=DEPENDENCY_MODE_TRY_FROM_EXPANDED
        )

        assert len(model_map) == len(expected_dtmis)
        for dtmi in expected_dtmis:
            assert dtmi in model_map.keys()
            model = model_map[dtmi]
            assert model["@id"] == dtmi

    @skip_remote
    def test_single_dtmi_with_component_deps_no_expanded_json(self, client):
        # this tests the fallback procedure when no expanded doc exists
        root_dtmi = "dtmi:com:example:Phone;2"
        expected_deps = [
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;2",
            "dtmi:com:example:Camera;3",
        ]
        expected_dtmis = [root_dtmi] + expected_deps
        model_map = client.get_models(
            root_dtmi, dependency_resolution=DEPENDENCY_MODE_TRY_FROM_EXPANDED
        )

        assert len(model_map) == len(expected_dtmis)
        for dtmi in expected_dtmis:
            assert dtmi in model_map.keys()
            model = model_map[dtmi]
            assert model["@id"] == dtmi

    @skip_remote
    def test_multiple_dtmis_with_component_deps_no_expanded_json(self, client):
        # this tests the fallback procedure when no expanded doc exists
        root_dtmi1 = "dtmi:com:example:Phone;2"
        root_dtmi2 = "dtmi:com:example:Freezer;1"
        expected_deps = [
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;2",
            "dtmi:com:example:Camera;3",
            "dtmi:com:example:Thermostat;1",
        ]
        expected_dtmis = [root_dtmi1, root_dtmi2] + expected_deps
        model_map = client.get_models(
            [root_dtmi1, root_dtmi2], dependency_resolution=DEPENDENCY_MODE_TRY_FROM_EXPANDED
        )

        assert len(model_map) == len(expected_dtmis)
        for dtmi in expected_dtmis:
            assert dtmi in model_map.keys()
            model = model_map[dtmi]
            assert model["@id"] == dtmi

    @skip_remote
    def test_multiple_dtmis_with_component_deps_extends_deps_mixed_expanded_json(self, client):
        root_dtmi1 = "dtmi:com:example:ColdStorage;1"  # no expanded doc
        root_dtmi2 = "dtmi:com:example:TemperatureController;1"  # has expanded doc
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
            "dtmi:com:example:Room;1",
            "dtmi:com:example:Freezer;1",
        ]
        expected_dtmis = [root_dtmi1, root_dtmi2] + expected_deps
        model_map = client.get_models(
            [root_dtmi1, root_dtmi2], dependency_resolution=DEPENDENCY_MODE_TRY_FROM_EXPANDED
        )

        assert len(model_map) == len(expected_dtmis)
        for dtmi in expected_dtmis:
            assert dtmi in model_map.keys()
            model = model_map[dtmi]
            assert model["@id"] == dtmi

    @skip_remote
    def test_dangling_expanded(self, client):
        root_dtmi = "dtmi:com:example:DanglingExpanded;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
        ]
        expected_dtmis = [root_dtmi] + expected_deps
        model_map = client.get_models(
            root_dtmi, dependency_resolution=DEPENDENCY_MODE_TRY_FROM_EXPANDED
        )

        assert len(model_map) == len(expected_dtmis)
        for dtmi in expected_dtmis:
            assert dtmi in model_map.keys()
            model = model_map[dtmi]
            assert model["@id"] == dtmi
