# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest
from azure.iot.modelsrepository import (
    ModelsRepositoryClient,
    DEFAULT_LOCATION,
)


@pytest.mark.describe("ModelsRepositoryClient.__init__()")
class ModelRepositoryClientTest(object):
    def test_remote_repository_client_init(self):
        client = ModelsRepositoryClient()
        assert client.repository_uri == DEFAULT_LOCATION
        client.close()

        sample_uri = "https://dtmi.com"
        client = ModelsRepositoryClient(sample_uri)
        assert client.repository_uri == sample_uri
        client.close()

    def test_local_repository_client_init(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        local_repo = os.path.join(test_dir, "local_repository")
        client = ModelsRepositoryClient(local_repo)
        assert client.repository_uri == local_repo
        client.close()
