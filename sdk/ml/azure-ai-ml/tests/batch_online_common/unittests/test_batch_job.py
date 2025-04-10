# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest

from azure.ai.ml.entities import BatchJob
from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import BatchJobResource, BatchJob as BatchJobRest


@pytest.mark.unittest
class TestBatchJob:
    def test_batch_job_to_dict(self):
        batch_job = BatchJob(
            id="id",
            name="name",
            type="type",
            status="status",
        )
        batch_job_dict = batch_job._to_dict()
        assert batch_job_dict == {
            "id": "id",
            "name": "name",
            "type": "type",
            "status": "status",
        }

    def test_batch_job_to_rest(self):
        batch_jon_rest = BatchJobResource.deserialize(
            {"id": "id", "name": "name", "type": "type", "properties": {"status": "status"}}
        )
        batch_job = BatchJob._from_rest_object(batch_jon_rest)
        assert batch_job.id == "id"
        assert batch_job.name == "name"
        assert batch_job.type == "type"
        assert batch_job.status == "status"
