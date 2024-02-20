from pathlib import Path

from azure.ai.ml.exceptions import JobException
from azure.core.exceptions import HttpResponseError

_PIPELINE_JOB_TIMEOUT_SECOND = 20 * 60  # timeout for pipeline job's tests, unit in second.
_PIPELINE_JOB_LONG_RUNNING_TIMEOUT_SECOND = 40 * 60  # timeout for pipeline job's long-running tests, unit in second.

DATABINDING_EXPRESSION_TEST_CASES = [
    (
        "./tests/test_configs/dsl_pipeline/data_binding_expression/input_basic.yml",
        None,
    ),
    (
        "./tests/test_configs/dsl_pipeline/data_binding_expression/input_literal_cross_type.yml",
        None,
    ),
    (
        "./tests/test_configs/dsl_pipeline/data_binding_expression/input_literal_meta.yml",
        HttpResponseError(),
    ),
    (
        "./tests/test_configs/dsl_pipeline/data_binding_expression/input_path.yml",
        None,
    ),
    (
        "./tests/test_configs/dsl_pipeline/data_binding_expression/input_path_concatenate.yml",
        HttpResponseError(),
    ),
    (
        "./tests/test_configs/dsl_pipeline/data_binding_expression/input_reason_expression.yml",
        HttpResponseError(),
    ),
    (
        "./tests/test_configs/dsl_pipeline/data_binding_expression/input_string_concatenate.yml",
        None,
    ),
    (
        "./tests/test_configs/dsl_pipeline/data_binding_expression/run_settings_compute.yml",
        JobException("", no_personal_data_message=""),
    ),
    (
        "./tests/test_configs/dsl_pipeline/data_binding_expression/run_settings_literal.yml",
        None,
    ),
    ("./tests/test_configs/dsl_pipeline/data_binding_expression/run_settings_sweep_literal.yml", None),
    (
        "./tests/test_configs/dsl_pipeline/data_binding_expression/run_settings_sweep_choice.yml",
        JobException("", no_personal_data_message=""),
    ),
    ("./tests/test_configs/dsl_pipeline/data_binding_expression/run_settings_sweep_limits.yml", None),
]

# this is to shorten the test name
DATABINDING_EXPRESSION_TEST_CASE_ENUMERATE = list(
    enumerate(
        map(
            lambda params: Path(params[0]).name,
            DATABINDING_EXPRESSION_TEST_CASES,
        )
    )
)
