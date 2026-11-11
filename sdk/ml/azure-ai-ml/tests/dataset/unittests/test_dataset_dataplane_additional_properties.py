import pytest

from azure.ai.ml._restclient.dataset_dataplane.models import DataVersionEntity


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestDataVersionEntityAdditionalProperties:
    """Regression guard for the ``mltable`` local data-asset resolution path.

    ``mltable.load("azureml://.../data/<name>/versions/<version>")`` fetches a ``DataVersionEntity``
    via ``MLClient.jobs._dataset_dataplane_operations._operation.get`` and reads
    ``data_version.additional_properties['isV2' | 'legacyDataflow']``. The TypeSpec (hybrid) model
    dropped the msrest ``additional_properties`` attribute; the ``models/_patch.py`` shim restores it.
    """

    def _wire(self):
        return {
            "dataVersion": {"dataUri": "azureml://datastores/x/paths/y", "dataType": "mltable"},
            "entityMetadata": {"etag": "abc"},
            "isV2": True,
            "legacyDataflow": "some-legacy-dataflow-yaml",
        }

    def test_additional_properties_exposes_unmodeled_wire_keys(self):
        entity = DataVersionEntity._deserialize(self._wire(), [])

        # mltable reads these exact keys off ``additional_properties``.
        assert entity.additional_properties["isV2"] is True
        assert entity.additional_properties["legacyDataflow"] == "some-legacy-dataflow-yaml"

    def test_additional_properties_excludes_modeled_fields(self):
        entity = DataVersionEntity._deserialize(self._wire(), [])

        # Declared fields must not leak into ``additional_properties`` (msrest parity).
        assert "dataVersion" not in entity.additional_properties
        assert "entityMetadata" not in entity.additional_properties

        # Declared fields remain accessible via their model attributes.
        assert entity.data_version.data_uri == "azureml://datastores/x/paths/y"
        assert entity.data_version.data_type == "mltable"

    def test_additional_properties_empty_when_no_extra_keys(self):
        entity = DataVersionEntity._deserialize(
            {"dataVersion": {"dataUri": "azureml://x", "dataType": "uri_folder"}}, []
        )

        assert entity.additional_properties == {}

    def test_missing_key_raises_key_error(self):
        # mltable relies on ``KeyError`` (caught) when ``legacyDataflow`` is absent.
        entity = DataVersionEntity._deserialize(
            {"dataVersion": {"dataUri": "azureml://x", "dataType": "mltable"}, "isV2": False}, []
        )

        with pytest.raises(KeyError):
            _ = entity.additional_properties["legacyDataflow"]
