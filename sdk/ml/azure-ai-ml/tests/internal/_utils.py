from azure.ai.ml import Input
from azure.ai.ml.constants import AssetTypes

PARAMETERS_TO_TEST = [
    (
        "./tests/test_configs/internal/ls_command_component.yaml",
        {},
        {
            # "resources.priority": 5,  # to be review
            "compute": "cpu-cluster",
            "limits.timeout": 300,
        },
    ),  # Command
    # TODO 1892661: enable all pipeline job e2e tests
    # ("./tests/test_configs/internal/hemera-component/component.yaml", True),  # Hemera
    # ("./tests/test_configs/internal/hdi-component/component_spec.yaml", True),  # HDInsight
    # (
    #     "./tests/test_configs/internal/batch_inference/batch_score.yaml",  # Parallel
    #     False,  # Parallel component doesn't have code
    # ),
    # (
    #     "./tests/test_configs/internal/scope-component/component_spec.yaml",
    #     {
    #         "TextData": Input(type=AssetTypes.MLTABLE, path="azureml:scope_tsv:1"),
    #         "ExtractionClause": "column1:string, column2:int",
    #     },
    #     {
    #         "adla_account_name": "adla_account_name",
    #         "scope_param": "-tokens 50",
    #         "custom_job_name_suffix": "component_sdk_test",
    #     },
    # ),  # Scope
    # ("./tests/test_configs/internal/data-transfer-component/component_spec.yaml", True),  # Data Transfer
    # ("./tests/test_configs/internal/starlite-component/component_spec.yaml", True),  # Starlite
]


def set_run_settings(node, runsettings_dict):
    for dot_key, value in runsettings_dict.items():
        keys = dot_key.split(".")
        last_key = keys.pop()

        current_obj = node
        for key in keys:
            current_obj = getattr(current_obj, key)
        setattr(current_obj, last_key, value)
