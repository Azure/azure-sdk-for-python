# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest
from azure.iot.modelsrepository._model_query import (
    ModelQuery
)

_model_template = '{{\
{0}\
"@type": "Interface",\
"displayName": "Phone",\
{1}\
{2}\
"@context": "dtmi:dtdl:context;2"\
}}'

@pytest.mark.describe("ModelQuery")
class ModelQueryTests(object):
    @pytest.mark.it("ModelQuery.parse_model() returns Model with correct id")
    @pytest.mark.parametrize(
        "input_id", "expected_id",
        [
            pytest.param("\"@id\": \"dtmi:com:example:thermostat;1\",", "dtmi:com:example:thermostat;1", id="Realistic DTMI @id"),
            pytest.param("\"@id\": \"\",", "", id="Model with empty @id"),
            pytest.param("", "", id="Model with no @id"),
        ],
    )
    def test_parse_root_dtmi(self, input_id, expected_id):
        model_content = _model_template.format(input_id, "", "")
        model = ModelQuery(model_content).parse_model()
        assert model.id == expected_id

    @pytest.mark.it("ModelQuery.parse_model() returns Model with correct components from contents")
    @pytest.mark.parametrize(
        "input_component", "expected_component",
        [
            pytest.param(
                '"contents":\
                [{\
                    "@type": "Component",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                }],',
                ["dtmi:com:example:Camera;3"],
                id="Model with one component in contents"
            ),
            pytest.param(
                '"contents":\
                [{\
                    "@type": "Component",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                },\
                {\
                    "@type": "Component",\
                    "name": "backCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                },\
                {\
                    "@type": "Component",\
                    "name": "deviceInfo",\
                    "schema": "dtmi:azure:DeviceManagement:DeviceInformation;1"\
                }],',
                [
                    "dtmi:com:example:Camera;3",
                    "dtmi:azure:DeviceManagement:DeviceInformation;1"
                ],
                id="Model with multiple components in contents"
            ),
            pytest.param(
                '"contents":\
                [{\
                    "@type": "Property",\
                    "name": "capacity",\
                    "schema": "integer"\
                },\
                {\
                    "@type": "Component",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                },\
                {\
                    "@type": "Component",\
                    "name": "backCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                },\
                {\
                    "@type": "Component",\
                    "name": "deviceInfo",\
                    "schema": "dtmi:azure:DeviceManagement:DeviceInformation;1"\
                }],',
                [
                    "dtmi:com:example:Camera;3",
                    "dtmi:azure:DeviceManagement:DeviceInformation;1"
                ],
                id="Model with multiple components and non-components in contents"
            ),
            pytest.param(
                '"contents":\
                [{\
                    "@type": "Property",\
                    "name": "capacity",\
                    "schema": "integer"\
                }],',
                [],
                id="Model with no components in contents"
            ),
            pytest.param(
                '"contents":["dtmi:azure:DeviceManagement:DeviceInformation;1"],',
                ["dtmi:azure:DeviceManagement:DeviceInformation;1"],
                id="Model with string component in contents"
            ),
            pytest.param(
                '"contents":["dtmi:azure:DeviceManagement:DeviceInformation;1", "dtmi:com:example:Camera;3"],',
                ["dtmi:azure:DeviceManagement:DeviceInformation;1", "dtmi:com:example:Camera;3"],
                id="Model with multiple string components in contents"
            ),
            pytest.param(
                '"contents":[],',
                [],
                id="Model with empty contents"
            ),
            pytest.param("", [], id="Model with no contents"),
        ],
    )
    def test_parse_components(self, input_component, expected_component):
        model_content = _model_template.format("", "", input_component)
        model = ModelQuery(model_content).parse_model()
        assert model.components == expected_component
        assert model.dependencies == expected_component

    @pytest.mark.it("ModelQuery.parse_model() returns Model with correct interfaces from extends")
    @pytest.mark.parametrize(
        "input_extends", "expected_extends",
        [
            pytest.param(
                '"extends":\
                [{\
                    "@type": "Interface",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                }],',
                ["dtmi:com:example:Camera;3"],
                id="Model with one interfaces in extends"
            ),
            pytest.param(
                '"extends":\
                [{\
                    "@type": "Interface",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                },\
                {\
                    "@type": "Interface",\
                    "name": "backCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                },\
                {\
                    "@type": "Interface",\
                    "name": "deviceInfo",\
                    "schema": "dtmi:azure:DeviceManagement:DeviceInformation;1"\
                }],',
                [
                    "dtmi:com:example:Camera;3",
                    "dtmi:azure:DeviceManagement:DeviceInformation;1"
                ],
                id="Model with multiple interfaces in extends"
            ),
            pytest.param(
                '"extends":\
                [{\
                    "@type": "Property",\
                    "name": "capacity",\
                    "schema": "integer"\
                },\
                {\
                    "@type": "Interface",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                },\
                {\
                    "@type": "Interface",\
                    "name": "backCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                },\
                {\
                    "@type": "Interface",\
                    "name": "deviceInfo",\
                    "schema": "dtmi:azure:DeviceManagement:DeviceInformation;1"\
                }],',
                ["dtmi:com:example:Camera;3",
                "dtmi:azure:DeviceManagement:DeviceInformation;1"],
                id="Model with multiple interfaces and non-interfaces in extends"
            ),
            pytest.param(
                '"extends":\
                [{\
                    "@type": "Property",\
                    "name": "capacity",\
                    "schema": "integer"\
                }],',
                [],
                id="Model with no interfacess in extends"
            ),
            pytest.param(
                '"extends":["dtmi:azure:DeviceManagement:DeviceInformation;1"],',
                ["dtmi:azure:DeviceManagement:DeviceInformation;1"],
                id="Model with string interfaces in extends"
            ),
            pytest.param(
                '"extends":["dtmi:azure:DeviceManagement:DeviceInformation;1", "dtmi:com:example:Camera;3"],',
                ["dtmi:azure:DeviceManagement:DeviceInformation;1", "dtmi:com:example:Camera;3"],
                id="Model with multiple string interfacess in extends"
            ),
            pytest.param(
                '"extends":\
                ["dtmi:com:example:Camera;3", {\
                    "@type": "Interface",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                }],',
                [
                    "dtmi:com:example:Camera;3",
                    "dtmi:azure:DeviceManagement:DeviceInformation;1"
                ],
                id="Model with dict and string interfaces in extends"
            ),
            pytest.param(
                '"extends":[],',
                [],
                id="Model with empty extends"
            ),
            pytest.param("", [], id="Model with no extends"),
        ],
    )
    def test_parse_expends(self, input_extends, expected_extends):
        model_content = _model_template.format("", input_extends,"")
        model = ModelQuery(model_content).parse_model()
        assert model.extends == expected_extends
        assert model.dependencies == expected_extends

    @pytest.mark.it(
        "ModelQuery.parse_model() returns Model with correct components and interfaces in dependencies"
    )
    @pytest.mark.parametrize(
        "input_extends, input_components, expected_extends, expected_components",
        [
            pytest.param(
                '"extends":\
                [{\
                    "@type": "Interface",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;2"\
                }],',
                '"contents":\
                [{\
                    "@type": "Component",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                }],',
                ["dtmi:com:example:Camera;2",],
                ["dtmi:com:example:Camera;3",],
                id="Model with one interfaces in extends, one component in contents"
            ),
            pytest.param(
                '"extends":\
                [{\
                    "@type": "Interface",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                },\
                {\
                    "@type": "Interface",\
                    "name": "backCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                },\
                {\
                    "@type": "Interface",\
                    "name": "deviceInfo",\
                    "schema": "dtmi:azure:DeviceManagement:DeviceInformation;1"\
                }],',
                '"contents":\
                [{\
                    "@type": "Component",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;4"\
                },\
                {\
                    "@type": "Component",\
                    "name": "backCamera",\
                    "schema": "dtmi:com:example:Camera;4"\
                },\
                {\
                    "@type": "Component",\
                    "name": "deviceInfo",\
                    "schema": "dtmi:azure:DeviceManagement:DeviceInformation;2"\
                }],',
                [
                    "dtmi:com:example:Camera;3",
                    "dtmi:azure:DeviceManagement:DeviceInformation;1"
                ],
                [
                    "dtmi:com:example:Camera;4",
                    "dtmi:azure:DeviceManagement:DeviceInformation;2"
                ],
                id="Model with multiple interfaces in extends, multiple components in "
                   "contents"
            ),
            pytest.param(
                '"extends":\
                [{\
                    "@type": "Interface",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                }],',
                '"contents":\
                [{\
                    "@type": "Component",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                }],',
                ["dtmi:com:example:Camera;3"],
                ["dtmi:com:example:Camera;3"],
                id="Model with same interface in extend and same component in contents"
            ),
            pytest.param(
                '"extends":\
                [{\
                    "@type": "Property",\
                    "name": "capacity",\
                    "schema": "integer"\
                },\
                {\
                    "@type": "Interface",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                },\
                {\
                    "@type": "Interface",\
                    "name": "backCamera",\
                    "schema": "dtmi:com:example:Camera;3"\
                },\
                {\
                    "@type": "Interface",\
                    "name": "deviceInfo",\
                    "schema": "dtmi:azure:DeviceManagement:DeviceInformation;1"\
                }],',
                '"contents":\
                [{\
                    "@type": "Command",\
                    "name": "capacity",\
                    "schema": "integer"\
                },\
                {\
                    "@type": "Component",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;4"\
                },\
                {\
                    "@type": "Component",\
                    "name": "backCamera",\
                    "schema": "dtmi:com:example:Camera;4"\
                },\
                {\
                    "@type": "Component",\
                    "name": "deviceInfo",\
                    "schema": "dtmi:azure:DeviceManagement:DeviceInformation;1"\
                }],',
                [
                    "dtmi:com:example:Camera;3",
                    "dtmi:azure:DeviceManagement:DeviceInformation;1"
                ],
                [
                    "dtmi:com:example:Camera;4",
                    "dtmi:azure:DeviceManagement:DeviceInformation;1"
                ],
                id="Model with multiple interfaces and non-interfaces in extends,"
                   " components and non-components in contents"
            ),
            pytest.param(
                '"extends":\
                [{\
                    "@type": "Property",\
                    "name": "capacity",\
                    "schema": "integer"\
                }],',
                [],
                id="Model with no interfaces in extends and no components in contents"
            ),
            pytest.param(
                '"extends":["dtmi:azure:DeviceManagement:DeviceInformation;1"],',
                '"contents":\
                [{\
                    "@type": "Component",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;2"\
                }],',
                ["dtmi:azure:DeviceManagement:DeviceInformation;1"],
                ["dtmi:com:example:Camera;2",],
                id="Model with string interface in extends, one component in contents"
            ),
            pytest.param(
                '"extends":[\
                    "dtmi:azure:DeviceManagement:DeviceInformation;1", \
                    "dtmi:com:example:Camera;3"\
                ],',
                '"contents":\
                [{\
                    "@type": "Component",\
                    "name": "frontCamera",\
                    "schema": "dtmi:com:example:Camera;4"\
                },\
                {\
                    "@type": "Component",\
                    "name": "backCamera",\
                    "schema": "dtmi:com:example:Camera;4"\
                },\
                {\
                    "@type": "Component",\
                    "name": "deviceInfo",\
                    "schema": "dtmi:azure:DeviceManagement:DeviceInformation;2"\
                }],',
                ["dtmi:azure:DeviceManagement:DeviceInformation;1", "dtmi:com:example:Camera;3"],
                ["dtmi:azure:DeviceManagement:DeviceInformation;2", "dtmi:com:example:Camera;4"],
                id="Model with multiple string interfaces in extends, multiple components"
                " in contents"
            ),
        ],
    )
    def test_parse_dependencies(self, input_extends, input_components, expected_extends, expected_components):
        model_content = _model_template.format("", input_extends, input_components)
        model = ModelQuery(model_content).parse_model()
        assert model.components == expected_components
        assert model.extends == expected_extends
        assert model.dependencies == list(set(expected_extends).update(set(expected_components)))
