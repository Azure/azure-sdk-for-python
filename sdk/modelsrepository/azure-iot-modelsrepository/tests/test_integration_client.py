# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from parameterized import parameterized
from devtools_testutils import AzureTestCase
from azure.core.exceptions import ResourceNotFoundError
from azure.iot.modelsrepository import (
    ModelsRepositoryClient,
    DependencyModeType,
    ModelError,
)

LOCAL_REPO = "local repo"
REMOTE_REPO = "remote_repo"


################################
# Client Fixture Mixin Classes #
################################


class RemoteRepositoryMixin(object):
    def setUp(self):
        self.client = ModelsRepositoryClient()
        self.client_type = REMOTE_REPO
        super(RemoteRepositoryMixin, self).setUp()

    def tearDown(self):
        self.client.close()
        super(RemoteRepositoryMixin, self).tearDown()


class LocalRepositoryMixin(object):
    def setUp(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        local_repo = os.path.join(test_dir, "local_repository")
        self.client = ModelsRepositoryClient(repository_location=local_repo)
        self.client_type = LOCAL_REPO
        super(LocalRepositoryMixin, self).setUp()

    def tearDown(self):
        self.client.close()
        super(LocalRepositoryMixin, self).tearDown()


###########################
# Test Case Mixin Classes #
###########################


class GetModelsDependencyModeEnabledIntegrationTestCaseMixin(object):
    @parameterized.expand(
        [
            ("All lower case", "dtmi:com:example:thermostat;1"),
            ("Non-starting upper case", "dtmi:com:example:thermoStat;1"),
        ]
    )
    def test_dtmi_mismatch_casing(self, _, dtmi):
        with self.assertRaises(ModelError):
            self.client.get_models(dtmi, dependency_resolution=DependencyModeType.enabled.value)

    @parameterized.expand(
        [
            ("No semicolon", "dtmi:com:example:Thermostat:1"),
            ("Double colon", "dtmi:com:example::Thermostat;1"),
            ("No DTMI prefix", "com:example:Thermostat;1"),
        ]
    )
    def test_invalid_dtmi_format(self, _, dtmi):
        with self.assertRaises(ValueError):
            self.client.get_models(dtmi, dependency_resolution=DependencyModeType.enabled.value)

    def test_nonexistant_dtdl_doc(self):
        dtmi = "dtmi:com:example:thermojax;999"
        with self.assertRaises(ResourceNotFoundError):
            self.client.get_models(dtmi)

    def test_nonexistent_dependency_dtdl_doc(self):
        dtmi = "dtmi:com:example:invalidmodel;1"
        with self.assertRaises(ResourceNotFoundError):
            self.client.get_models(dtmi)

    def test_single_dtmi_no_components_no_extends(self):
        dtmi = "dtmi:com:example:Thermostat;1"
        model_map = self.client.get_models(dtmi, dependency_resolution=DependencyModeType.enabled.value)

        self.assertTrue(len(model_map) == 1)
        self.assertTrue(dtmi in model_map.keys())
        model = model_map[dtmi]
        self.assertTrue(model["@id"] == dtmi)

    def test_multiple_dtmis_no_components_no_extends(self):
        dtmi1 = "dtmi:com:example:Thermostat;1"
        dtmi2 = "dtmi:azure:DeviceManagement:DeviceInformation;1"
        model_map = self.client.get_models(
            [dtmi1, dtmi2], dependency_resolution=DependencyModeType.enabled.value
        )

        self.assertTrue(len(model_map) == 2)
        self.assertTrue(dtmi1 in model_map.keys())
        self.assertTrue(dtmi2 in model_map.keys())
        model1 = model_map[dtmi1]
        model2 = model_map[dtmi2]
        self.assertTrue(model1["@id"] == dtmi1)
        self.assertTrue(model2["@id"] == dtmi2)

    def test_single_dtmi_with_component_deps(self):
        root_dtmi = "dtmi:com:example:TemperatureController;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
        ]
        expected_dtmis = [root_dtmi] + expected_deps
        model_map = self.client.get_models(root_dtmi, dependency_resolution=DependencyModeType.enabled.value)

        self.assertTrue(len(model_map) == len(expected_dtmis))
        for dtmi in expected_dtmis:
            self.assertTrue(dtmi in model_map.keys())
            model = model_map[dtmi]
            self.assertTrue(model["@id"] == dtmi)

    def test_multiple_dtmis_with_component_deps(self):
        if self.client_type == REMOTE_REPO:
            self.skipTest("Insufficient data")
        root_dtmi1 = "dtmi:com:example:Phone;2"
        root_dtmi2 = "dtmi:com:example:TemperatureController;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;2",
            "dtmi:com:example:Camera;3",
        ]
        expected_dtmis = [root_dtmi1, root_dtmi2] + expected_deps
        model_map = self.client.get_models(
            [root_dtmi1, root_dtmi2], dependency_resolution=DependencyModeType.enabled.value
        )

        self.assertTrue(len(model_map) == len(expected_dtmis))
        for dtmi in expected_dtmis:
            self.assertTrue(dtmi in model_map.keys())
            model = model_map[dtmi]
            self.assertTrue(model["@id"] == dtmi)

    def test_multiple_dtmis_with_extends_deps_single_dtmi(self):
        if self.client_type == REMOTE_REPO:
            self.skipTest("Insufficient data")
        root_dtmi1 = "dtmi:com:example:TemperatureController;1"
        root_dtmi2 = "dtmi:com:example:ConferenceRoom;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
            "dtmi:com:example:Room;1",
        ]
        expected_dtmis = [root_dtmi1, root_dtmi2] + expected_deps
        model_map = self.client.get_models(
            [root_dtmi1, root_dtmi2], dependency_resolution=DependencyModeType.enabled.value
        )

        self.assertTrue(len(model_map) == len(expected_dtmis))
        for dtmi in expected_dtmis:
            self.assertTrue(dtmi in model_map.keys())
            model = model_map[dtmi]
            self.assertTrue(model["@id"] == dtmi)

    def test_multiple_dtmis_with_extends_deps_multiple_dtmi(self):
        if self.client_type == REMOTE_REPO:
            self.skipTest("Insufficient data")
        root_dtmi1 = "dtmi:com:example:TemperatureController;1"
        root_dtmi2 = "dtmi:com:example:ColdStorage;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
            "dtmi:com:example:Room;1",
            "dtmi:com:example:Freezer;1",
        ]
        expected_dtmis = [root_dtmi1, root_dtmi2] + expected_deps
        model_map = self.client.get_models(
            [root_dtmi1, root_dtmi2], dependency_resolution=DependencyModeType.enabled.value
        )

        self.assertTrue(len(model_map) == len(expected_dtmis))
        for dtmi in expected_dtmis:
            self.assertTrue(dtmi in model_map.keys())
            model = model_map[dtmi]
            self.assertTrue(model["@id"] == dtmi)

    def test_single_dtmi_with_extends_single_model_inline(self):
        if self.client_type == REMOTE_REPO:
            self.skipTest("Insufficient data")
        dtmi = "dtmi:com:example:base;1"
        model_map = self.client.get_models(dtmi, dependency_resolution=DependencyModeType.enabled.value)

        self.assertTrue(len(model_map) == 1)
        self.assertTrue(dtmi in model_map.keys())
        model = model_map[dtmi]
        self.assertTrue(model["@id"] == dtmi)

    def test_single_dtmi_with_extends_mixed_inline_and_dtmi(self):
        if self.client_type == REMOTE_REPO:
            self.skipTest("Insufficient data")
        root_dtmi = "dtmi:com:example:base;2"
        expected_deps = ["dtmi:com:example:Freezer;1", "dtmi:com:example:Thermostat;1"]
        expected_dtmis = [root_dtmi] + expected_deps
        model_map = self.client.get_models(root_dtmi, dependency_resolution=DependencyModeType.enabled.value)

        self.assertTrue(len(model_map) == len(expected_dtmis))
        for dtmi in expected_dtmis:
            self.assertTrue(dtmi in model_map.keys())
            model = model_map[dtmi]
            self.assertTrue(model["@id"] == dtmi)

    def test_duplicate_dtmi(self):
        dtmi1 = "dtmi:azure:DeviceManagement:DeviceInformation;1"
        dtmi2 = "dtmi:azure:DeviceManagement:DeviceInformation;1"
        model_map = self.client.get_models(
            [dtmi1, dtmi1], dependency_resolution=DependencyModeType.enabled.value
        )

        self.assertTrue(len(model_map) == 1)
        self.assertTrue(dtmi1 in model_map.keys())
        self.assertTrue(dtmi2 in model_map.keys())
        model = model_map[dtmi1]
        self.assertTrue(model["@id"] == dtmi1 == dtmi2)


class GetModelsDependencyModeDisabledIntegrationTestCaseMixin(object):
    def test_dtmi_mismatch_casing(self):
        dtmi = "dtmi:com:example:thermostat;1"
        with self.assertRaises(ModelError):
            self.client.get_models(dtmi, dependency_resolution=DependencyModeType.disabled.value)

    @parameterized.expand(
        [
            ("No semicolon", "dtmi:com:example:Thermostat:1"),
            ("Double colon", "dtmi:com:example::Thermostat;1"),
            ("No DTMI prefix", "com:example:Thermostat;1"),
        ]
    )
    def test_invalid_dtmi_format(self, _, dtmi):
        with self.assertRaises(ValueError):
            self.client.get_models(dtmi, dependency_resolution=DependencyModeType.disabled.value)

    def test_nonexistant_dtdl_doc(self):
        dtmi = "dtmi:com:example:thermojax;999"
        with self.assertRaises(ResourceNotFoundError):
            self.client.get_models(dtmi)

    def test_nonexistent_dependency_dtdl_doc(self):
        dtmi = "dtmi:com:example:invalidmodel;1"
        with self.assertRaises(ResourceNotFoundError):
            self.client.get_models(dtmi)

    def test_single_dtmi_no_components_no_extends(self):
        dtmi = "dtmi:com:example:Thermostat;1"
        model_map = self.client.get_models(dtmi, dependency_resolution=DependencyModeType.disabled.value)

        self.assertTrue(len(model_map) == 1)
        self.assertTrue(dtmi in model_map.keys())
        model = model_map[dtmi]
        self.assertTrue(model["@id"] == dtmi)

    def test_multiple_dtmis_no_components_no_extends(self):
        dtmi1 = "dtmi:com:example:Thermostat;1"
        dtmi2 = "dtmi:azure:DeviceManagement:DeviceInformation;1"
        model_map = self.client.get_models(
            [dtmi1, dtmi2], dependency_resolution=DependencyModeType.disabled.value
        )

        self.assertTrue(len(model_map) == 2)
        self.assertTrue(dtmi1 in model_map.keys())
        self.assertTrue(dtmi2 in model_map.keys())
        model1 = model_map[dtmi1]
        model2 = model_map[dtmi2]
        self.assertTrue(model1["@id"] == dtmi1)
        self.assertTrue(model2["@id"] == dtmi2)

    def test_single_dtmi_with_component_deps(self):
        dtmi = "dtmi:com:example:TemperatureController;1"
        model_map = self.client.get_models(dtmi, dependency_resolution=DependencyModeType.disabled.value)

        self.assertTrue(len(model_map) == 1)
        self.assertTrue(dtmi in model_map.keys())
        model = model_map[dtmi]
        self.assertTrue(model["@id"] == dtmi)

    def test_multiple_dtmis_with_component_deps(self):
        if self.client_type == REMOTE_REPO:
            self.skipTest("Insufficient data")
        dtmi1 = "dtmi:com:example:Phone;2"
        dtmi2 = "dtmi:com:example:TemperatureController;1"
        model_map = self.client.get_models(
            [dtmi1, dtmi2], dependency_resolution=DependencyModeType.disabled.value
        )

        self.assertTrue(len(model_map) == 2)
        self.assertTrue(dtmi1 in model_map.keys())
        self.assertTrue(dtmi2 in model_map.keys())
        model1 = model_map[dtmi1]
        model2 = model_map[dtmi2]
        self.assertTrue(model1["@id"] == dtmi1)
        self.assertTrue(model2["@id"] == dtmi2)

    def test_multiple_dtmis_with_extends_deps_single_dtmi(self):
        if self.client_type == REMOTE_REPO:
            self.skipTest("Insufficient data")
        dtmi1 = "dtmi:com:example:TemperatureController;1"
        dtmi2 = "dtmi:com:example:ConferenceRoom;1"
        model_map = self.client.get_models(
            [dtmi1, dtmi2], dependency_resolution=DependencyModeType.disabled.value
        )

        self.assertTrue(len(model_map) == 2)
        self.assertTrue(dtmi1 in model_map.keys())
        self.assertTrue(dtmi2 in model_map.keys())
        model1 = model_map[dtmi1]
        model2 = model_map[dtmi2]
        self.assertTrue(model1["@id"] == dtmi1)
        self.assertTrue(model2["@id"] == dtmi2)

    def test_multiple_dtmis_with_extends_deps_multiple_dtmi(self):
        if self.client_type == REMOTE_REPO:
            self.skipTest("Insufficient data")
        dtmi1 = "dtmi:com:example:TemperatureController;1"
        dtmi2 = "dtmi:com:example:ColdStorage;1"
        model_map = self.client.get_models(
            [dtmi1, dtmi2], dependency_resolution=DependencyModeType.disabled.value
        )

        self.assertTrue(len(model_map) == 2)
        self.assertTrue(dtmi1 in model_map.keys())
        self.assertTrue(dtmi2 in model_map.keys())
        model1 = model_map[dtmi1]
        model2 = model_map[dtmi2]
        self.assertTrue(model1["@id"] == dtmi1)
        self.assertTrue(model2["@id"] == dtmi2)

    def test_single_dtmi_with_extends_single_model_inline(self):
        if self.client_type == REMOTE_REPO:
            self.skipTest("Insufficient data")
        dtmi = "dtmi:com:example:base;1"
        model_map = self.client.get_models(dtmi, dependency_resolution=DependencyModeType.disabled.value)

        self.assertTrue(len(model_map) == 1)
        self.assertTrue(dtmi in model_map.keys())
        model = model_map[dtmi]
        self.assertTrue(model["@id"] == dtmi)

    def test_single_dtmi_with_extends_mixed_inline_and_dtmi(self):
        if self.client_type == REMOTE_REPO:
            self.skipTest("Insufficient data")
        dtmi = "dtmi:com:example:base;2"
        model_map = self.client.get_models(dtmi, dependency_resolution=DependencyModeType.disabled.value)

        self.assertTrue(len(model_map) == 1)
        self.assertTrue(dtmi in model_map.keys())
        model = model_map[dtmi]
        self.assertTrue(model["@id"] == dtmi)

    def test_duplicate_dtmi(self):
        dtmi1 = "dtmi:azure:DeviceManagement:DeviceInformation;1"
        dtmi2 = "dtmi:azure:DeviceManagement:DeviceInformation;1"
        model_map = self.client.get_models(
            [dtmi1, dtmi1], dependency_resolution=DependencyModeType.disabled.value
        )

        self.assertTrue(len(model_map) == 1)
        self.assertTrue(dtmi1 in model_map.keys())
        self.assertTrue(dtmi2 in model_map.keys())
        model = model_map[dtmi1]
        self.assertTrue(model["@id"] == dtmi1 == dtmi2)


#######################
# Actual Test Classes #
#######################


class TestIntegrationGetModelsDependencyModeEnabledLocalRepository(
    GetModelsDependencyModeEnabledIntegrationTestCaseMixin, LocalRepositoryMixin, AzureTestCase
):
    pass


class TestIntegrationGetModelsDependencyModeDisabledLocalRepository(
    GetModelsDependencyModeDisabledIntegrationTestCaseMixin, LocalRepositoryMixin, AzureTestCase
):
    pass


class TestIntegrationGetModelsDependencyModeEnabledRemoteRepository(
    GetModelsDependencyModeEnabledIntegrationTestCaseMixin, RemoteRepositoryMixin, AzureTestCase
):
    pass


class TestIntegrationGetModelsDependencyModeDisabledRemoteRepository(
    GetModelsDependencyModeDisabledIntegrationTestCaseMixin, RemoteRepositoryMixin, AzureTestCase
):
    pass
