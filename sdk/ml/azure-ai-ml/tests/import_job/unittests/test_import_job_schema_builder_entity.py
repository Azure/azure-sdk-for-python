from os import environ

import pytest
from marshmallow.exceptions import ValidationError

from azure.ai.ml import load_component, load_job
from azure.ai.ml.constants import ImportSourceType
from azure.ai.ml.constants._common import AZUREML_PRIVATE_FEATURES_ENV_VAR, AssetTypes
from azure.ai.ml.entities._builders.import_node import Import
from azure.ai.ml.entities._component.import_component import ImportComponent
from azure.ai.ml.entities._inputs_outputs import Output
from azure.ai.ml.entities._job.import_job import DatabaseImportSource, FileImportSource, ImportJob, ImportSource


@pytest.mark.unittest
class TestImportJob:
    environ[AZUREML_PRIVATE_FEATURES_ENV_VAR] = "True"

    @pytest.mark.parametrize(
        "yaml_file,expected_import_source,expected_import_source_type",
        [
            ("import_job_test.yml", DatabaseImportSource, ImportSourceType.AZURESQLDB),
            ("import_job_test_azuresynapseanalytics.yml", DatabaseImportSource, ImportSourceType.AZURESYNAPSEANALYTICS),
            ("import_job_test_snowflake.yml", DatabaseImportSource, ImportSourceType.SNOWFLAKE),
            ("import_job_test_s3.yml", FileImportSource, ImportSourceType.S3),
        ],
    )
    def test_import_job(self, yaml_file: str, expected_import_source: ImportSource, expected_import_source_type: str):
        import_job = load_job(
            source="./tests/test_configs/import_job/" + yaml_file,
        )

        source = (
            DatabaseImportSource(
                type=expected_import_source_type,
                connection="azureml:my_username_password",
                query="select * from REGION",
            )
            if expected_import_source is DatabaseImportSource
            else FileImportSource(
                type=expected_import_source_type, connection="azureml:my_username_password", path="test1/*"
            )
        )
        output_type = AssetTypes.MLTABLE if expected_import_source is DatabaseImportSource else AssetTypes.URI_FOLDER

        import_job2 = ImportJob(
            description="test_description",
            display_name="test_display_name",
            source=source,
            output=Output(type=output_type, path="azureml://datastores/workspaceblobstore/paths/output_dir/"),
        )

        assert import_job.description == import_job2.description
        assert import_job.display_name == import_job2.display_name

        assert import_job.output.type == import_job2.output.type
        assert import_job.output.path == import_job2.output.path

        assert isinstance(import_job, ImportJob)
        assert isinstance(import_job.source, expected_import_source)
        assert import_job.source.type == import_job2.source.type
        assert import_job.source.connection == import_job2.source.connection

    @pytest.mark.parametrize(
        "yaml_file,expected_exception_messages",
        [
            (
                "import_job_test_missing_keys.yml",
                ["source: [Missing data for required field.]", "output: [Missing data for required field.]"],
            ),
            (
                "import_job_test_missing_fields.yml",
                ["connection: [Missing data for required field.]", "query: [Missing data for required field.]"],
            ),
            (
                "import_job_test_unknown_keys.yml",
                ["compute: [Unknown field.]", "inputs: [Unknown field.]", "outputs: [Unknown field.]"],
            ),
            (
                "import_job_test_unknown_fields.yml",
                ["query: [Missing data for required field.]", "path: [Unknown field.]"],
            ),
        ],
    )
    def test_import_job_missing_unknown_fields(self, yaml_file: str, expected_exception_messages: list):
        with pytest.raises(ValidationError) as exception_raised:
            load_job("./tests/test_configs/import_job/" + yaml_file)

        assert exception_raised.value.messages is not None and len(exception_raised.value.messages) > 0
        assert "Validation for ImportJobSchema failed" in exception_raised.value.messages[0]

        exception_message = exception_raised.value.messages[0].replace("\n", "").replace('"', "").replace("  ", "")

        for expected_exception_message in expected_exception_messages:
            assert expected_exception_message in exception_message

    def test_import_component(self):
        import_func = load_component("./tests/test_configs/import_job/import_component_test.yml")
        import_node: Import = import_func(
            type="azuresqldb", connection="azureml:my_username_password", query="select * from REGION"
        )
        import_job: ImportJob = import_node._to_job()

        assert isinstance(import_node, Import)
        assert isinstance(import_node.component, ImportComponent)
        assert isinstance(import_job.source, DatabaseImportSource)

        assert import_node.component.description == "This is the basic import component"
        assert import_node.component.display_name == "ImportComponentBasic"

        assert import_job.source.type == "azuresqldb"
        assert import_job.source.connection == "azureml:my_username_password"
        assert import_job.source.query == "select * from REGION"

        assert import_node.inputs.get("type")._data == import_job.source.type
        assert import_node.inputs.get("connection")._data == import_job.source.connection
        assert import_node.inputs.get("query")._data == import_job.source.query
        assert import_node.outputs.get("output").type == AssetTypes.MLTABLE

    @pytest.mark.parametrize(
        "yaml_file,expected_exception_messages",
        [
            (
                "import_component_test_missing_keys.yml",
                {"source": "Missing data for required field.", "output": "Missing data for required field."},
            ),
        ],
    )
    def test_import_component_missing_unknown_fields(self, yaml_file: str, expected_exception_messages: dict):
        with pytest.raises(ValidationError) as exception_raised:
            load_component(source="./tests/test_configs/import_job/" + yaml_file)

        assert exception_raised.value.messages is not None and len(exception_raised.value.messages) > 0
        assert exception_raised.typename == "ValidationError"

        for key in expected_exception_messages:
            assert any(key in msg for msg in exception_raised.value.messages)
            # assert expected_exception_messages[key] in exception_raised.value.messages[key]
