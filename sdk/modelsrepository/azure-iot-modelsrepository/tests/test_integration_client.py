# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from parameterized import parameterized
from devtools_testutils import AzureTestCase
from azure.core.exceptions import ResourceNotFoundError
from azure.iot.modelsrepository import (
    DependencyModeType,
    ModelError,
    ModelsRepositoryClient
)
from .client_helper import (
    ClientType,
    determine_repo
)


###########################
# Test Case Mixin Classes #
###########################


class TestIntegrationGetModels(AzureTestCase):
    @parameterized.expand(
        [
            ("Remote Client", ClientType.remote.value),
            ("Local Client", ClientType.local.value)
        ]
    )
    def test_dtmi_mismatch_casing(self, _, client_type):
        lower_case_dtmi = "dtmi:com:example:thermostat;1"

        repo = determine_repo(client_type=client_type)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            with self.assertRaises(ModelError):
                client.get_models(lower_case_dtmi)

    @parameterized.expand(
        [
            ("No semicolon", "dtmi:com:example:Thermostat:1"),
            ("Double colon", "dtmi:com:example::Thermostat;1"),
            ("No DTMI prefix", "com:example:Thermostat;1"),
        ]
    )
    def test_invalid_dtmi_format(self, _, dtmi):
        repo = determine_repo(client_type=ClientType.local.value)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            with self.assertRaises(ValueError):
                client.get_models(dtmi)

    @parameterized.expand(
        [
            ("Remote Client", ClientType.remote.value),
            ("Local Client", ClientType.local.value)
        ]
    )
    def test_nonexistant_dtdl_doc(self, _, client_type):
        dtmi = "dtmi:com:example:thermojax;999"

        repo = determine_repo(client_type=client_type)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            with self.assertRaises(ResourceNotFoundError):
                client.get_models(dtmi)

    def test_nonexistent_dependency_dtdl_doc(self):
        dtmi = "dtmi:com:example:invalidmodel;1"

        repo = determine_repo(client_type=ClientType.local.value)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            with self.assertRaises(ResourceNotFoundError):
                client.get_models(dtmi)

    @parameterized.expand(
        [
            ("Remote Client with metadata", ClientType.remote.value, True),
            ("Remote Client without metadata", ClientType.remote.value, False),
            ("Local Client with metadata", ClientType.local.value, True),
            ("Local Client without metadata", ClientType.local.value, False),
        ]
    )
    def test_single_dtmi_no_components_no_extends(self, _, client_type, has_metadata):
        dtmi = "dtmi:com:example:Thermostat;1"

        repo = determine_repo(client_type=client_type, has_metadata=has_metadata)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            model_map = client.get_models(dtmi)

        self.assertTrue(len(model_map) == 1)
        self.assertTrue(dtmi in model_map.keys())
        model = model_map[dtmi]
        self.assertTrue(model["@id"] == dtmi)

    @parameterized.expand(
        [
            ("Remote Client with metadata", ClientType.remote.value, True),
            ("Remote Client without metadata", ClientType.remote.value, False),
            ("Local Client with metadata", ClientType.local.value, True),
            ("Local Client without metadata", ClientType.local.value, False),
        ]
    )
    def test_multiple_dtmis_no_components_no_extends(self, _, client_type, has_metadata):
        dtmi1 = "dtmi:com:example:Thermostat;1"
        dtmi2 = "dtmi:azure:DeviceManagement:DeviceInformation;1"

        repo = determine_repo(client_type=client_type, has_metadata=has_metadata)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            model_map = client.get_models(
                [dtmi1, dtmi2]
            )

        self.assertTrue(len(model_map) == 2)
        self.assertTrue(dtmi1 in model_map.keys())
        self.assertTrue(dtmi2 in model_map.keys())
        model1 = model_map[dtmi1]
        model2 = model_map[dtmi2]
        self.assertTrue(model1["@id"] == dtmi1)
        self.assertTrue(model2["@id"] == dtmi2)

    @parameterized.expand(
        [
            ("Remote Client with metadata", ClientType.remote.value, True),
            ("Remote Client without metadata", ClientType.remote.value, False),
            ("Local Client with metadata", ClientType.local.value, True),
            ("Local Client without metadata", ClientType.local.value, False),
        ]
    )
    def test_single_dtmi_with_component_deps(self, _, client_type, has_metadata):
        root_dtmi = "dtmi:com:example:TemperatureController;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
        ]
        expected_dtmis = [root_dtmi] + expected_deps

        repo = determine_repo(client_type=client_type, has_metadata=has_metadata)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            model_map = client.get_models(root_dtmi)

        self.assertTrue(len(model_map) == len(expected_dtmis))
        for dtmi in expected_dtmis:
            self.assertTrue(dtmi in model_map.keys())
            model = model_map[dtmi]
            self.assertTrue(model["@id"] == dtmi)

    def test_multiple_dtmis_with_component_deps(self):
        root_dtmi1 = "dtmi:com:example:Phone;2"
        root_dtmi2 = "dtmi:com:example:TemperatureController;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;2",
            "dtmi:com:example:Camera;3",
        ]
        expected_dtmis = [root_dtmi1, root_dtmi2] + expected_deps

        repo = determine_repo(client_type=ClientType.local.value)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            model_map = client.get_models(
                [root_dtmi1, root_dtmi2]
            )

        self.assertTrue(len(model_map) == len(expected_dtmis))
        for dtmi in expected_dtmis:
            self.assertTrue(dtmi in model_map.keys())
            model = model_map[dtmi]
            self.assertTrue(model["@id"] == dtmi)

    def test_multiple_dtmis_with_extends_deps_single_dtmi(self):
        root_dtmi1 = "dtmi:com:example:TemperatureController;1"
        root_dtmi2 = "dtmi:com:example:ConferenceRoom;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
            "dtmi:com:example:Room;1",
        ]
        expected_dtmis = [root_dtmi1, root_dtmi2] + expected_deps

        repo = determine_repo(client_type=ClientType.local.value)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            model_map = client.get_models(
                [root_dtmi1, root_dtmi2]
            )

        self.assertTrue(len(model_map) == len(expected_dtmis))
        for dtmi in expected_dtmis:
            self.assertTrue(dtmi in model_map.keys())
            model = model_map[dtmi]
            self.assertTrue(model["@id"] == dtmi)

    def test_multiple_dtmis_with_extends_deps_multiple_dtmi(self):
        root_dtmi1 = "dtmi:com:example:TemperatureController;1"
        root_dtmi2 = "dtmi:com:example:ColdStorage;1"
        expected_deps = [
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1",
            "dtmi:com:example:Room;1",
            "dtmi:com:example:Freezer;1",
        ]
        expected_dtmis = [root_dtmi1, root_dtmi2] + expected_deps

        repo = determine_repo(client_type=ClientType.local.value)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            model_map = client.get_models(
            [root_dtmi1, root_dtmi2]
        )

        self.assertTrue(len(model_map) == len(expected_dtmis))
        for dtmi in expected_dtmis:
            self.assertTrue(dtmi in model_map.keys())
            model = model_map[dtmi]
            self.assertTrue(model["@id"] == dtmi)

    def test_single_dtmi_with_extends_single_model_inline(self):
        dtmi = "dtmi:com:example:base;1"

        repo = determine_repo(client_type=ClientType.local.value)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            model_map = client.get_models(dtmi)

        self.assertTrue(len(model_map) == 1)
        self.assertTrue(dtmi in model_map.keys())
        model = model_map[dtmi]
        self.assertTrue(model["@id"] == dtmi)

    def test_single_dtmi_with_extends_mixed_inline_and_dtmi(self):
        root_dtmi = "dtmi:com:example:base;2"
        expected_deps = ["dtmi:com:example:Freezer;1", "dtmi:com:example:Thermostat;1"]
        expected_dtmis = [root_dtmi] + expected_deps

        repo = determine_repo(client_type=ClientType.local.value)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            model_map = client.get_models(root_dtmi)

        self.assertTrue(len(model_map) == len(expected_dtmis))
        for dtmi in expected_dtmis:
            self.assertTrue(dtmi in model_map.keys())
            model = model_map[dtmi]
            self.assertTrue(model["@id"] == dtmi)

    @parameterized.expand(
        [
            ("Remote Client", ClientType.remote.value),
            ("Local Client", ClientType.local.value)
        ]
    )
    def test_duplicate_dtmi(self, _, client_type):
        dtmi1 = "dtmi:azure:DeviceManagement:DeviceInformation;1"
        dtmi2 = "dtmi:azure:DeviceManagement:DeviceInformation;1"

        repo = determine_repo(client_type=client_type)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            model_map = client.get_models(
                [dtmi1, dtmi1]
            )

        self.assertTrue(len(model_map) == 1)
        self.assertTrue(dtmi1 in model_map.keys())
        self.assertTrue(dtmi2 in model_map.keys())
        model = model_map[dtmi1]
        self.assertTrue(model["@id"] == dtmi1 == dtmi2)

    @parameterized.expand(
        [
            ("Remote Client", ClientType.remote.value),
            ("Local Client", ClientType.local.value)
        ]
    )
    def test_single_dtmi_with_dependencies_disabled_dependency_resolution(self, _, client_type):
        dtmi = "dtmi:com:example:TemperatureController;1"

        repo = determine_repo(client_type=client_type)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            model_map = client.get_models(dtmi, dependency_resolution=DependencyModeType.disabled.value)

        self.assertTrue(len(model_map) == 1)
        self.assertTrue(dtmi in model_map.keys())
        model = model_map[dtmi]
        self.assertTrue(model["@id"] == dtmi)

    def test_single_dtmi_with_depdendencies_use_metadata_enabled_dependency_resolution(self):
        dtmi = "dtmi:com:example:DanglingExpanded;1"
        expected_dtmis = [
            dtmi,
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1"
        ]

        repo = determine_repo(client_type=ClientType.local.value, has_metadata=True)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            model_map = client.get_models(dtmi, dependency_resolution=DependencyModeType.enabled.value)

        self.assertTrue(len(model_map) == len(expected_dtmis))
        for dtmi in expected_dtmis:
            self.assertTrue(dtmi in model_map.keys())
            model = model_map[dtmi]
            self.assertTrue(model["@id"] == dtmi)

    @parameterized.expand(
        [
            ("Has metadata", True),
            ("Has no metadata", False)
        ]
    )
    def test_multiple_dtmis_with_partial_dependencies_enabled_dependency_resolution(self, _, has_metadata):
        # Expanded models available
        dtmis_expanded = [
            "dtmi:com:example:TemperatureController;1",
            "dtmi:com:example:Thermostat;1",
            "dtmi:azure:DeviceManagement:DeviceInformation;1"
        ]

        # Expanded models not available, must use model query
        dtmis_non_expanded = [
            "dtmi:com:example:ColdStorage;1",
            "dtmi:com:example:Room;1",
            "dtmi:com:example:Freezer;1"
        ]

        total_dtmis = dtmis_expanded + dtmis_non_expanded

        repo = determine_repo(client_type=ClientType.local.value, has_metadata=has_metadata)
        client = ModelsRepositoryClient(repository_location=repo)

        with client:
            model_map = client.get_models([dtmis_expanded[0], dtmis_non_expanded[0]])

        self.assertTrue(len(model_map) == len(total_dtmis))
        for dtmi in total_dtmis:
            self.assertTrue(dtmi in model_map.keys())
            model = model_map[dtmi]
            self.assertTrue(model["@id"] == dtmi)
