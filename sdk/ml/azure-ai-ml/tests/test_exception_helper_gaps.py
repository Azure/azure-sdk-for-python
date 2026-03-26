import sys
import types

import pytest
from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml import _exception_helper as exception_helper
from azure.ai.ml.constants._common import YAML_CREATION_ERROR_DESCRIPTION
from azure.ai.ml.exceptions import ErrorTarget, MlException, ValidationErrorType, ValidationException

module_definitions = {
    "azure.ai.ml._schema._datastore": [
        "AzureBlobSchema",
        "AzureDataLakeGen1Schema",
        "AzureDataLakeGen2Schema",
        "AzureFileSchema",
    ],
    "azure.ai.ml._schema._sweep": ["SweepJobSchema"],
    "azure.ai.ml._schema.assets.data": ["DataSchema"],
    "azure.ai.ml._schema.assets.environment": ["EnvironmentSchema"],
    "azure.ai.ml._schema.assets.model": ["ModelSchema"],
    "azure.ai.ml._schema.job": ["CommandJobSchema"],
}

for module_name, class_names in module_definitions.items():
    module = types.ModuleType(module_name)
    for class_name in class_names:
        setattr(module, class_name, type(class_name, (), {}))
    sys.modules[module_name] = module

REF_DOC_ERROR_MESSAGE_MAP = {}
util_module = types.ModuleType("azure.ai.ml.entities._util")
util_module.REF_DOC_ERROR_MESSAGE_MAP = REF_DOC_ERROR_MESSAGE_MAP
sys.modules["azure.ai.ml.entities._util"] = util_module

azure_datastore_module = sys.modules["azure.ai.ml._schema._datastore"]
assets_module = sys.modules["azure.ai.ml._schema.assets.data"]
environment_assets_module = sys.modules["azure.ai.ml._schema.assets.environment"]
model_assets_module = sys.modules["azure.ai.ml._schema.assets.model"]
sweep_module = sys.modules["azure.ai.ml._schema._sweep"]
job_module = sys.modules["azure.ai.ml._schema.job"]

REF_DOC_ERROR_MESSAGE_MAP.update(
    {
        model_assets_module.ModelSchema: "Model schema guidance",
        assets_module.DataSchema: "Data schema guidance",
        job_module.CommandJobSchema: "Command job schema guidance",
        sweep_module.SweepJobSchema: "Sweep schema guidance",
        azure_datastore_module.AzureBlobSchema: "Datastore guidance",
        azure_datastore_module.AzureDataLakeGen1Schema: "Gen1 datastore guidance",
        azure_datastore_module.AzureDataLakeGen2Schema: "Gen2 datastore guidance",
        azure_datastore_module.AzureFileSchema: "File datastore guidance",
        environment_assets_module.EnvironmentSchema: "Environment schema guidance",
        "": "Default guidance",
    }
)

ENTITY_EXPECTATIONS = [
    (ErrorTarget.MODEL, "Model schema guidance"),
    (ErrorTarget.DATA, "Data schema guidance"),
    (ErrorTarget.COMMAND_JOB, "Command job schema guidance"),
    (ErrorTarget.SWEEP_JOB, "Sweep schema guidance"),
    (ErrorTarget.BLOB_DATASTORE, "Datastore guidance"),
    (ErrorTarget.DATASTORE, "Datastore guidance"),
    (ErrorTarget.GEN1_DATASTORE, "Gen1 datastore guidance"),
    (ErrorTarget.GEN2_DATASTORE, "Gen2 datastore guidance"),
    (ErrorTarget.FILE_DATASTORE, "File datastore guidance"),
    (ErrorTarget.ENVIRONMENT, "Environment schema guidance"),
    (ErrorTarget.CODE, "Default guidance"),
]

@pytest.mark.parametrize("entity_type,expected_doc", ENTITY_EXPECTATIONS)
def test_format_create_validation_error_yaml_operation_appends_ref_doc_entries(
    monkeypatch, entity_type, expected_doc
):
    monkeypatch.setattr(exception_helper, "get_entity_type", lambda error: (entity_type, "details"))
    monkeypatch.setattr(
        exception_helper, "format_details_section", lambda error, details, entity_type: ({}, "formatted details")
    )
    monkeypatch.setattr(
        exception_helper,
        "format_errors_and_resolutions_sections",
        lambda entity_type, error_types, cli: ("errors", "base resolutions"),
    )

    formatted = exception_helper.format_create_validation_error("ignored", yaml_operation=True)

    assert expected_doc in formatted


def test_log_and_raise_error_wraps_schema_validation_error_and_respects_yaml_flag(monkeypatch):
    traced = {}

    def fake_format(arg, yaml_operation=False, cli=False, raw_error=None):
        traced["args"] = (arg, yaml_operation, cli, raw_error)
        return "formatted schema failure"

    monkeypatch.setattr(exception_helper, "format_create_validation_error", fake_format)

    schema_error = SchemaValidationError([{"field": ["error"]}])
    with pytest.raises(MlException) as excinfo:
        exception_helper.log_and_raise_error(schema_error, yaml_operation=True)

    assert "formatted schema failure" in str(excinfo.value)
    assert traced["args"][0] == schema_error.messages[0]
    assert traced["args"][1] is True


def test_log_and_raise_error_schema_validation_error_falls_back_on_not_implemented(monkeypatch):
    def fake_format(*args, **kwargs):
        raise NotImplementedError

    monkeypatch.setattr(exception_helper, "format_create_validation_error", fake_format)

    schema_error = SchemaValidationError([{"fallback": ["missing"]}])
    with pytest.raises(MlException) as excinfo:
        exception_helper.log_and_raise_error(schema_error)

    assert "fallback" in str(excinfo.value)


class _GenericValidationException(ValidationException):
    def __init__(self):
        self.error_type = ValidationErrorType.GENERIC
        self.target = ErrorTarget.MODEL
        self.message = "generic validation failure"
        self.exc_msg = "GenericValidationException"


def test_log_and_raise_error_generic_validation_exception_preserves_original(monkeypatch):
    monkeypatch.setattr(
        exception_helper,
        "format_create_validation_error",
        lambda *args, **kwargs: pytest.fail("Should not be invoked for generic errors"),
    )

    error = _GenericValidationException()
    with pytest.raises(MlException) as excinfo:
        exception_helper.log_and_raise_error(error)

    assert excinfo.value.no_personal_data_message is error
    assert excinfo.value.no_personal_data_message.message == "generic validation failure"


class _NonGenericValidationException(ValidationException):
    def __init__(self):
        self.error_type = ValidationErrorType.MISSING_FIELD
        self.target = ErrorTarget.MODEL
        self.message = "non generic validation failure"
        self.exc_msg = "NonGenericValidationException"


def test_log_and_raise_error_non_generic_validation_exception_uses_formatting(monkeypatch):
    recorded = {}

    def fake_format(error_arg, yaml_operation=False, cli=False, raw_error=None):
        recorded["error"] = error_arg
        return "formatted validation failure"

    monkeypatch.setattr(exception_helper, "format_create_validation_error", fake_format)

    error = _NonGenericValidationException()
    with pytest.raises(MlException) as excinfo:
        exception_helper.log_and_raise_error(error)

    assert "formatted validation failure" in str(excinfo.value)
    assert recorded["error"] is error


def test_log_and_raise_error_propagates_other_exceptions():
    with pytest.raises(ValueError):
        exception_helper.log_and_raise_error(ValueError("boom"))


class _ModelSchema:
    pass

class _DataSchema:
    pass

class _CommandJobSchema:
    pass

class _SweepJobSchema:
    pass

class _AzureBlobSchema:
    pass

class _AzureDataLakeGen1Schema:
    pass

class _AzureDataLakeGen2Schema:
    pass

class _AzureFileSchema:
    pass

class _EnvironmentSchema:
    pass

MODEL_SCHEMA = _ModelSchema
DATA_SCHEMA = _DataSchema
COMMAND_JOB_SCHEMA = _CommandJobSchema
SWEEP_JOB_SCHEMA = _SweepJobSchema
AZURE_BLOB_SCHEMA = _AzureBlobSchema
AZURE_GEN1_SCHEMA = _AzureDataLakeGen1Schema
AZURE_GEN2_SCHEMA = _AzureDataLakeGen2Schema
AZURE_FILE_SCHEMA = _AzureFileSchema
ENVIRONMENT_SCHEMA = _EnvironmentSchema


def _install_schema_stubs(monkeypatch, ref_doc_map):
    datastore_module = types.ModuleType('azure.ai.ml._schema._datastore')
    datastore_module.AzureBlobSchema = AZURE_BLOB_SCHEMA
    datastore_module.AzureDataLakeGen1Schema = AZURE_GEN1_SCHEMA
    datastore_module.AzureDataLakeGen2Schema = AZURE_GEN2_SCHEMA
    datastore_module.AzureFileSchema = AZURE_FILE_SCHEMA
    monkeypatch.setitem(sys.modules, 'azure.ai.ml._schema._datastore', datastore_module)

    sweep_module = types.ModuleType('azure.ai.ml._schema._sweep')
    sweep_module.SweepJobSchema = SWEEP_JOB_SCHEMA
    monkeypatch.setitem(sys.modules, 'azure.ai.ml._schema._sweep', sweep_module)

    data_module = types.ModuleType('azure.ai.ml._schema.assets.data')
    data_module.DataSchema = DATA_SCHEMA
    monkeypatch.setitem(sys.modules, 'azure.ai.ml._schema.assets.data', data_module)

    environment_module = types.ModuleType('azure.ai.ml._schema.assets.environment')
    environment_module.EnvironmentSchema = ENVIRONMENT_SCHEMA
    monkeypatch.setitem(sys.modules, 'azure.ai.ml._schema.assets.environment', environment_module)

    model_module = types.ModuleType('azure.ai.ml._schema.assets.model')
    model_module.ModelSchema = MODEL_SCHEMA
    monkeypatch.setitem(sys.modules, 'azure.ai.ml._schema.assets.model', model_module)

    job_module = types.ModuleType('azure.ai.ml._schema.job')
    job_module.CommandJobSchema = COMMAND_JOB_SCHEMA
    monkeypatch.setitem(sys.modules, 'azure.ai.ml._schema.job', job_module)

    entities_module = types.ModuleType('azure.ai.ml.entities._util')
    entities_module.REF_DOC_ERROR_MESSAGE_MAP = ref_doc_map
    monkeypatch.setitem(sys.modules, 'azure.ai.ml.entities._util', entities_module)


class _MapRecorder(dict):
    def __init__(self):
        super().__init__()
        self.last_key = None

    def get(self, key, default=None):
        self.last_key = key
        return default or ''

REF_DOC_GUIDANCE = {
    MODEL_SCHEMA: 'model guidance',
    DATA_SCHEMA: 'data guidance',
    COMMAND_JOB_SCHEMA: 'command guidance',
    SWEEP_JOB_SCHEMA: 'sweep guidance',
    AZURE_BLOB_SCHEMA: 'blob guidance',
    AZURE_GEN1_SCHEMA: 'gen1 guidance',
    AZURE_GEN2_SCHEMA: 'gen2 guidance',
    AZURE_FILE_SCHEMA: 'file guidance',
    ENVIRONMENT_SCHEMA: 'env guidance',
}

ENTITY_GUIDANCE_CASES = [
    (ErrorTarget.MODEL, 'model guidance'),
    (ErrorTarget.DATA, 'data guidance'),
    (ErrorTarget.COMMAND_JOB, 'command guidance'),
    (ErrorTarget.SWEEP_JOB, 'sweep guidance'),
    (ErrorTarget.BLOB_DATASTORE, 'blob guidance'),
    (ErrorTarget.DATASTORE, 'blob guidance'),
    (ErrorTarget.GEN1_DATASTORE, 'gen1 guidance'),
    (ErrorTarget.GEN2_DATASTORE, 'gen2 guidance'),
    (ErrorTarget.FILE_DATASTORE, 'file guidance'),
    (ErrorTarget.ENVIRONMENT, 'env guidance'),
]

@pytest.mark.parametrize('entity_type, expected_guidance', ENTITY_GUIDANCE_CASES)
def test_format_create_validation_error_appends_ref_doc_for_yaml_entity_types(monkeypatch, entity_type, expected_guidance):
    _install_schema_stubs(monkeypatch, ref_doc_map=REF_DOC_GUIDANCE)
    monkeypatch.setattr(exception_helper, 'get_entity_type', lambda _: (entity_type, 'details'))
    monkeypatch.setattr(exception_helper, 'format_details_section', lambda *args, **kwargs: ({}, 'details'))
    monkeypatch.setattr(
        exception_helper,
        'format_errors_and_resolutions_sections',
        lambda *args, **kwargs: ('errors', 'resolutions'),
    )
    result = exception_helper.format_create_validation_error('ignored', yaml_operation=True)
    assert expected_guidance in result


def test_format_create_validation_error_uses_empty_schema_type_for_unmatched_entity(monkeypatch):
    recorder = _MapRecorder()
    _install_schema_stubs(monkeypatch, ref_doc_map=recorder)
    monkeypatch.setattr(exception_helper, 'get_entity_type', lambda _: (ErrorTarget.JOB, 'details'))
    monkeypatch.setattr(exception_helper, 'format_details_section', lambda *args, **kwargs: ({}, 'details'))
    monkeypatch.setattr(
        exception_helper,
        'format_errors_and_resolutions_sections',
        lambda *args, **kwargs: ('errors', 'resolutions'),
    )
    exception_helper.format_create_validation_error('ignored', yaml_operation=True)
    assert recorder.last_key == ''


def test_format_create_validation_error_without_yaml_description(monkeypatch):
    monkeypatch.setattr(exception_helper, 'get_entity_type', lambda _: (ErrorTarget.MODEL, 'details'))
    monkeypatch.setattr(exception_helper, 'format_details_section', lambda *args, **kwargs: ({}, 'details'))
    monkeypatch.setattr(
        exception_helper,
        'format_errors_and_resolutions_sections',
        lambda *args, **kwargs: ('errors', 'resolutions'),
    )
    result = exception_helper.format_create_validation_error('ignored', yaml_operation=False)
    unexpected_description = YAML_CREATION_ERROR_DESCRIPTION.format(entity_type=ErrorTarget.MODEL)
    assert unexpected_description not in result


class _DummyValidationException:
    def __init__(self, error_type):
        self.error_type = error_type


def test_log_and_raise_with_schema_validation_error_uses_formatter_and_debug(monkeypatch):
    error = SchemaValidationError('issue')
    error.messages = ['payload']
    monkeypatch.setattr(exception_helper.module_logger, 'error', lambda *args, **kwargs: None)
    monkeypatch.setattr(exception_helper.module_logger, 'debug', lambda *args, **kwargs: None)
    monkeypatch.setattr(exception_helper, 'format_create_validation_error', lambda *args, **kwargs: 'formatted')
    with pytest.raises(MlException) as excinfo:
        exception_helper.log_and_raise_error(error, debug=True)
    assert excinfo.value.message == 'formatted'


def test_log_and_raise_with_schema_validation_error_handles_not_implemented(monkeypatch):
    error = SchemaValidationError('issue')
    error.messages = ['payload']

    def _raise_not_implemented(*args, **kwargs):
        raise NotImplementedError

    monkeypatch.setattr(exception_helper.module_logger, 'debug', lambda *args, **kwargs: None)
    monkeypatch.setattr(exception_helper, 'format_create_validation_error', _raise_not_implemented)
    with pytest.raises(MlException) as excinfo:
        exception_helper.log_and_raise_error(error)
    assert excinfo.value.message == 'issue'
    assert excinfo.value.no_personal_data_message is error


def test_log_and_raise_with_validation_exception_generic_skips_formatter(monkeypatch):
    monkeypatch.setattr(exception_helper, 'ValidationException', _DummyValidationException)
    monkeypatch.setattr(exception_helper.module_logger, 'debug', lambda *args, **kwargs: None)

    def _fail_if_called(*args, **kwargs):
        raise AssertionError('formatter should not be invoked')

    monkeypatch.setattr(exception_helper, 'format_create_validation_error', _fail_if_called)
    generic_error = _DummyValidationException(ValidationErrorType.GENERIC)
    with pytest.raises(MlException) as excinfo:
        exception_helper.log_and_raise_error(generic_error)
    assert excinfo.value.no_personal_data_message is generic_error


def test_log_and_raise_with_validation_exception_uses_formatter(monkeypatch):
    monkeypatch.setattr(exception_helper, 'ValidationException', _DummyValidationException)
    monkeypatch.setattr(exception_helper.module_logger, 'debug', lambda *args, **kwargs: None)
    monkeypatch.setattr(exception_helper, 'format_create_validation_error', lambda *args, **kwargs: 'validation formatted')
    error = _DummyValidationException(ValidationErrorType.INVALID_VALUE)
    with pytest.raises(MlException) as excinfo:
        exception_helper.log_and_raise_error(error)
    assert excinfo.value.message == 'validation formatted'


def test_log_and_raise_with_validation_exception_handles_not_implemented(monkeypatch):
    monkeypatch.setattr(exception_helper, 'ValidationException', _DummyValidationException)
    monkeypatch.setattr(exception_helper.module_logger, 'debug', lambda *args, **kwargs: None)

    def _raise_not_implemented(*args, **kwargs):
        raise NotImplementedError

    monkeypatch.setattr(exception_helper, 'format_create_validation_error', _raise_not_implemented)
    error = _DummyValidationException(ValidationErrorType.INVALID_VALUE)
    with pytest.raises(MlException) as excinfo:
        exception_helper.log_and_raise_error(error)
    assert excinfo.value.message == str(error)


def test_log_and_raise_error_propagates_other_exceptions():
    with pytest.raises(ValueError):
        exception_helper.log_and_raise_error(ValueError('boom'))
