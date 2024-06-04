# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_input_output_configurations.py
DESCRIPTION:
    These samples configures for input and output of a component.
USAGE:
    python ml_samples_input_output_configurations.py

"""


class InputOutputConfigurationOptions(object):
    def ml_input_output_config(self):
        # [START configure_database]
        from azure.ai.ml.entities._inputs_outputs import Database

        # For querying a database table
        source_database = Database(query="SELECT * FROM my_table", connection="azureml:my_azuresql_connection")

        # For invoking a stored procedure with parameters
        stored_procedure_params = [
            {"name": "job", "value": "Engineer", "type": "String"},
            {"name": "department", "value": "Engineering", "type": "String"},
        ]
        source_database = Database(
            stored_procedure="SelectEmployeeByJobAndDepartment",
            stored_procedure_params=stored_procedure_params,
            connection="azureml:my_azuresql_connection",
        )

        # [END configure_database]


if __name__ == "__main__":
    sample = InputOutputConfigurationOptions()
    sample.ml_input_output_config()
