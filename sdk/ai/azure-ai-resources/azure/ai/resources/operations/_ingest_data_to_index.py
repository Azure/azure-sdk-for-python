# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml import MLClient

from azure.ai.resources.operations import IndexDataSource, ACSOutputConfig
from ._index_config import IndexConfig


def ingest_data_to_index(
    *,
    client: MLClient,
    index_config: IndexConfig,
    source_config: IndexDataSource,
    acs_config: ACSOutputConfig = None,  # todo better name?
):  # pylint: disable=too-many-function-args
    # create index creation pipeline from loaded yml component
    # presumably relying heavily upon code from here:
    # https://github.com/Azure/azureml_run_specification/blob/d74e8aac81203206976203fd4936f33d3b30e6e0/specs/simplified-sdk/mlindex_creation_job.md

    pipeline = source_config._createComponent(index_config=index_config, acs_config=acs_config)
    pipeline.settings = {"default_compute": "serverless"}
    client.jobs.create_or_update(pipeline)