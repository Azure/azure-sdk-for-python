# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
import unittest
from azure.ai.projects._model_base import _deserialize
from azure.ai.projects.models import _models


class Test(unittest.TestCase):

    def testName(self):
        val = {
            "id": "vs_OQpX6y9YM368EBZ5GmF45kRO",
            "object": "vector_store",
            "name": "TV Support FAQ",
            "status": "completed",
            "usage_bytes": 0,
            "created_at": 1729730726,
            "file_counts": {"in_progress": 0, "completed": 0, "failed": 0, "cancelled": 0, "total": 0},
            "metadata": {"source": "Assistant API Tests"},
            "expires_after": None,
            "expires_at": None,
            "last_active_at": 1729730726,
            "configuration": {
                "data_sources": [
                    {
                        "type": "uri_asset",
                        "uri": "azureml://subscriptions/10e1de13-9717-4242-acf5-3e241940d326/resourcegroups/rg-sawidderai/workspaces/sawidder-0278/datastores/workspaceblobstore/paths/UI/2024-10-01_001042_UTC/unit-test.txt",
                    }
                ]
            },
            "configuration1": {},
        }
        # json_val = json.dumps(val)
        vct = _deserialize(_models.VectorStore, val)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
