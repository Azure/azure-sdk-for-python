# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import logging
from azure.iot.modelsrepository import ModelsRepositoryClient

logging.basicConfig(level=logging.DEBUG)


@pytest.mark.describe("ModelsRepositoryClient - .get_models() [INTEGRATION]")
class TestModelsRepositoryClientGetModels(object):
    @pytest.mark.it("test recordings")
    def test_simple(self):
        c = ModelsRepositoryClient()
        c.get_models(["dtmi:com:example:TemperatureController;1"])
