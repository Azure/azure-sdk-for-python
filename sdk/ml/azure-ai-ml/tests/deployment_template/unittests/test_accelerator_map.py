# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import tempfile
from pathlib import Path

import pytest

from azure.ai.ml.entities._deployment.accelerator_map import AcceleratorMap
from azure.ai.ml.entities._deployment.deployment_template import DeploymentTemplate


class TestAcceleratorMap:
    """Tests for the AcceleratorMap entity."""

    def test_basic_init(self):
        """Test basic AcceleratorMap initialization with required fields."""
        am = AcceleratorMap(
            accelerator_type="H100_80GB",
            number_of_accelerators_per_model_instance=4,
        )

        assert am.accelerator_type == "H100_80GB"
        assert am.number_of_accelerators_per_model_instance == 4
        assert am.default is None

    def test_full_init(self):
        """Test AcceleratorMap initialization with all fields."""
        am = AcceleratorMap(
            accelerator_type="H200_141GB",
            number_of_accelerators_per_model_instance=2,
            default=True,
        )

        assert am.accelerator_type == "H200_141GB"
        assert am.number_of_accelerators_per_model_instance == 2
        assert am.default is True

    def test_default_false(self):
        """Test AcceleratorMap with default=False."""
        am = AcceleratorMap(
            accelerator_type="A100_80GB",
            number_of_accelerators_per_model_instance=8,
            default=False,
        )

        assert am.default is False

    def test_to_rest_dict(self):
        """Test conversion to REST API dictionary."""
        am = AcceleratorMap(
            accelerator_type="H100_80GB",
            number_of_accelerators_per_model_instance=4,
            default=True,
        )

        rest_dict = am._to_rest_dict()

        assert rest_dict["acceleratorType"] == "H100_80GB"
        assert rest_dict["numberOfAcceleratorsPerModelInstance"] == 4
        assert rest_dict["default"] is True

    def test_to_rest_dict_without_default(self):
        """Test conversion to REST API dictionary without default field."""
        am = AcceleratorMap(
            accelerator_type="H100_80GB",
            number_of_accelerators_per_model_instance=4,
        )

        rest_dict = am._to_rest_dict()

        assert rest_dict["acceleratorType"] == "H100_80GB"
        assert rest_dict["numberOfAcceleratorsPerModelInstance"] == 4
        assert "default" not in rest_dict

    def test_from_rest_dict(self):
        """Test creation from REST API dictionary."""
        rest_dict = {
            "acceleratorType": "H200_141GB",
            "numberOfAcceleratorsPerModelInstance": 2,
            "default": True,
        }

        am = AcceleratorMap._from_rest_dict(rest_dict)

        assert am.accelerator_type == "H200_141GB"
        assert am.number_of_accelerators_per_model_instance == 2
        assert am.default is True

    def test_from_rest_dict_without_default(self):
        """Test creation from REST API dictionary without default."""
        rest_dict = {
            "acceleratorType": "A100_80GB",
            "numberOfAcceleratorsPerModelInstance": 8,
        }

        am = AcceleratorMap._from_rest_dict(rest_dict)

        assert am.accelerator_type == "A100_80GB"
        assert am.number_of_accelerators_per_model_instance == 8
        assert am.default is None

    def test_round_trip(self):
        """Test round-trip: entity -> REST dict -> entity."""
        original = AcceleratorMap(
            accelerator_type="H100_80GB",
            number_of_accelerators_per_model_instance=4,
            default=True,
        )

        rest_dict = original._to_rest_dict()
        restored = AcceleratorMap._from_rest_dict(rest_dict)

        assert original == restored

    def test_equality(self):
        """Test equality comparison."""
        am1 = AcceleratorMap(accelerator_type="H100_80GB", number_of_accelerators_per_model_instance=4, default=True)
        am2 = AcceleratorMap(accelerator_type="H100_80GB", number_of_accelerators_per_model_instance=4, default=True)
        am3 = AcceleratorMap(accelerator_type="H200_141GB", number_of_accelerators_per_model_instance=2)

        assert am1 == am2
        assert am1 != am3

    def test_inequality_with_other_types(self):
        """Test inequality with non-AcceleratorMap objects."""
        am = AcceleratorMap(accelerator_type="H100_80GB", number_of_accelerators_per_model_instance=4)

        assert am != "not an accelerator map"
        assert am != 42
        assert am != None  # noqa: E711

    def test_repr(self):
        """Test string representation."""
        am = AcceleratorMap(
            accelerator_type="H100_80GB",
            number_of_accelerators_per_model_instance=4,
            default=True,
        )

        repr_str = repr(am)
        assert "H100_80GB" in repr_str
        assert "4" in repr_str
        assert "True" in repr_str


class TestDeploymentTemplateWithAcceleratorMaps:
    """Tests for accelerator_maps integration in DeploymentTemplate."""

    def test_init_with_accelerator_maps(self):
        """Test DeploymentTemplate with accelerator_maps field."""
        maps = [
            AcceleratorMap(accelerator_type="H100_80GB", number_of_accelerators_per_model_instance=4, default=True),
            AcceleratorMap(accelerator_type="H200_141GB", number_of_accelerators_per_model_instance=2),
        ]

        template = DeploymentTemplate(
            name="dt-with-accelerators",
            version="1",
            accelerator_maps=maps,
        )

        assert template.accelerator_maps is not None
        assert len(template.accelerator_maps) == 2
        assert template.accelerator_maps[0].accelerator_type == "H100_80GB"
        assert template.accelerator_maps[0].default is True
        assert template.accelerator_maps[1].accelerator_type == "H200_141GB"

    def test_init_without_accelerator_maps(self):
        """Test DeploymentTemplate without accelerator_maps defaults to None."""
        template = DeploymentTemplate(name="dt-no-accelerators", version="1")

        assert template.accelerator_maps is None

    def test_to_rest_object_with_accelerator_maps(self):
        """Test _to_rest_object includes acceleratorMaps."""
        maps = [
            AcceleratorMap(accelerator_type="H100_80GB", number_of_accelerators_per_model_instance=4, default=True),
            AcceleratorMap(accelerator_type="H200_141GB", number_of_accelerators_per_model_instance=2),
        ]

        template = DeploymentTemplate(
            name="dt1",
            version="1",
            environment="azureml://registries/reg1/environments/env1/versions/1",
            allowed_instance_types="Standard_ND96isr_H100_v5 Standard_ND96isr_H200_v5",
            accelerator_maps=maps,
        )

        rest_obj = template._to_rest_object()

        assert "acceleratorMaps" in rest_obj
        assert len(rest_obj["acceleratorMaps"]) == 2
        assert rest_obj["acceleratorMaps"][0]["acceleratorType"] == "H100_80GB"
        assert rest_obj["acceleratorMaps"][0]["numberOfAcceleratorsPerModelInstance"] == 4
        assert rest_obj["acceleratorMaps"][0]["default"] is True
        assert rest_obj["acceleratorMaps"][1]["acceleratorType"] == "H200_141GB"
        assert rest_obj["acceleratorMaps"][1]["numberOfAcceleratorsPerModelInstance"] == 2
        assert "default" not in rest_obj["acceleratorMaps"][1]

    def test_to_rest_object_without_accelerator_maps(self):
        """Test _to_rest_object omits acceleratorMaps when None."""
        template = DeploymentTemplate(name="dt1", version="1")

        rest_obj = template._to_rest_object()

        assert "acceleratorMaps" not in rest_obj

    def test_from_rest_object_with_accelerator_maps(self):
        """Test _from_rest_object deserializes acceleratorMaps."""
        rest_obj = {
            "properties": {
                "name": "dt1",
                "version": "1",
                "deploymentTemplateType": "ModelDeployment",
                "environmentId": "azureml://registries/reg1/environments/env1/versions/1",
                "allowedInstanceTypes": ["Standard_ND96isr_H100_v5"],
                "defaultInstanceType": "Standard_ND96isr_H100_v5",
                "instanceCount": 1,
                "acceleratorMaps": [
                    {
                        "acceleratorType": "H100_80GB",
                        "numberOfAcceleratorsPerModelInstance": 4,
                        "default": True,
                    },
                    {
                        "acceleratorType": "H200_141GB",
                        "numberOfAcceleratorsPerModelInstance": 2,
                    },
                ],
            },
        }

        template = DeploymentTemplate._from_rest_object(rest_obj)

        assert template.accelerator_maps is not None
        assert len(template.accelerator_maps) == 2
        assert template.accelerator_maps[0].accelerator_type == "H100_80GB"
        assert template.accelerator_maps[0].number_of_accelerators_per_model_instance == 4
        assert template.accelerator_maps[0].default is True
        assert template.accelerator_maps[1].accelerator_type == "H200_141GB"
        assert template.accelerator_maps[1].number_of_accelerators_per_model_instance == 2
        assert template.accelerator_maps[1].default is None

    def test_from_rest_object_without_accelerator_maps(self):
        """Test _from_rest_object handles missing acceleratorMaps."""
        rest_obj = {
            "properties": {
                "name": "dt1",
                "version": "1",
                "deploymentTemplateType": "ModelDeployment",
                "environmentId": "env1",
                "allowedInstanceTypes": ["Standard_DS3_v2"],
                "defaultInstanceType": "Standard_DS3_v2",
                "instanceCount": 1,
            },
        }

        template = DeploymentTemplate._from_rest_object(rest_obj)

        assert template.accelerator_maps is None

    def test_dump_with_accelerator_maps(self):
        """Test dump() includes accelerator_maps."""
        maps = [
            AcceleratorMap(accelerator_type="H100_80GB", number_of_accelerators_per_model_instance=4, default=True),
            AcceleratorMap(accelerator_type="H200_141GB", number_of_accelerators_per_model_instance=2),
        ]

        template = DeploymentTemplate(
            name="dt1",
            version="1",
            accelerator_maps=maps,
        )

        dumped = template.dump()

        assert "accelerator_maps" in dumped
        assert len(dumped["accelerator_maps"]) == 2
        assert dumped["accelerator_maps"][0]["accelerator_type"] == "H100_80GB"
        assert dumped["accelerator_maps"][0]["number_of_accelerators_per_model_instance"] == 4
        assert dumped["accelerator_maps"][0]["default"] is True
        assert dumped["accelerator_maps"][1]["accelerator_type"] == "H200_141GB"
        assert dumped["accelerator_maps"][1]["number_of_accelerators_per_model_instance"] == 2
        assert "default" not in dumped["accelerator_maps"][1]

    def test_to_dict_with_accelerator_maps(self):
        """Test _to_dict() includes acceleratorMaps."""
        maps = [
            AcceleratorMap(accelerator_type="H100_80GB", number_of_accelerators_per_model_instance=4, default=True),
        ]

        template = DeploymentTemplate(name="dt1", version="1", accelerator_maps=maps)

        result = template._to_dict()

        assert "acceleratorMaps" in result
        assert len(result["acceleratorMaps"]) == 1
        assert result["acceleratorMaps"][0]["acceleratorType"] == "H100_80GB"

    def test_round_trip_rest_object(self):
        """Test full round-trip: entity -> REST -> entity."""
        original_maps = [
            AcceleratorMap(accelerator_type="H100_80GB", number_of_accelerators_per_model_instance=4, default=True),
            AcceleratorMap(accelerator_type="H200_141GB", number_of_accelerators_per_model_instance=2),
        ]

        original = DeploymentTemplate(
            name="dt1",
            version="1",
            description="Test template with accelerator maps",
            accelerator_maps=original_maps,
        )

        rest_obj = {"properties": original._to_rest_object()}
        restored = DeploymentTemplate._from_rest_object(rest_obj)

        assert restored.name == original.name
        assert restored.version == original.version
        assert restored.accelerator_maps is not None
        assert len(restored.accelerator_maps) == 2
        assert restored.accelerator_maps[0] == original_maps[0]
        assert restored.accelerator_maps[1] == original_maps[1]

    def test_str_with_accelerator_maps(self):
        """Test __str__ includes accelerator maps."""
        maps = [
            AcceleratorMap(accelerator_type="H100_80GB", number_of_accelerators_per_model_instance=4),
        ]

        template = DeploymentTemplate(name="dt1", version="1", accelerator_maps=maps)

        str_repr = str(template)
        assert "acceleratorMaps" in str_repr
        assert "H100_80GB" in str_repr


class TestAcceleratorMapSchema:
    """Tests for the AcceleratorMap marshmallow schema."""

    @pytest.fixture
    def dt_schema(self):
        """Create a DeploymentTemplateSchema instance."""
        from azure.ai.ml._schema._deployment.template.deployment_template import DeploymentTemplateSchema
        from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY

        temp_dir = tempfile.mkdtemp()
        context = {BASE_PATH_CONTEXT_KEY: Path(temp_dir)}
        schema = DeploymentTemplateSchema(context=context)
        return schema

    def test_load_with_accelerator_maps(self, dt_schema):
        """Test loading DeploymentTemplate data with accelerator_maps via schema."""
        data = {
            "name": "dt-with-maps",
            "version": "1",
            "accelerator_maps": [
                {
                    "accelerator_type": "H100_80GB",
                    "number_of_accelerators_per_model_instance": 4,
                    "default": True,
                },
                {
                    "accelerator_type": "H200_141GB",
                    "number_of_accelerators_per_model_instance": 2,
                },
            ],
        }

        result = dt_schema.load(data)

        assert isinstance(result, DeploymentTemplate)
        assert result.accelerator_maps is not None
        assert len(result.accelerator_maps) == 2
        assert isinstance(result.accelerator_maps[0], AcceleratorMap)
        assert result.accelerator_maps[0].accelerator_type == "H100_80GB"
        assert result.accelerator_maps[0].number_of_accelerators_per_model_instance == 4
        assert result.accelerator_maps[0].default is True
        assert result.accelerator_maps[1].accelerator_type == "H200_141GB"
        assert result.accelerator_maps[1].number_of_accelerators_per_model_instance == 2
        assert result.accelerator_maps[1].default is None

    def test_load_without_accelerator_maps(self, dt_schema):
        """Test loading DeploymentTemplate data without accelerator_maps."""
        data = {
            "name": "dt-no-maps",
            "version": "1",
        }

        result = dt_schema.load(data)

        assert isinstance(result, DeploymentTemplate)
        assert result.accelerator_maps is None

    def test_load_with_empty_accelerator_maps(self, dt_schema):
        """Test loading DeploymentTemplate data with empty accelerator_maps list."""
        data = {
            "name": "dt-empty-maps",
            "version": "1",
            "accelerator_maps": [],
        }

        result = dt_schema.load(data)

        assert isinstance(result, DeploymentTemplate)
        assert result.accelerator_maps == []
