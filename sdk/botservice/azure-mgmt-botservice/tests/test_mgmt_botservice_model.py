# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


from azure.mgmt.botservice.models import Site


class TestMgmtBotServiceModel:

    def test_model_site(self):
        # the model shall not raise error
        Site(
            is_v1_enabled=True,
            is_v3_enabled=True,
            site_name="xxx",
            is_enabled=True,
            is_webchat_preview_enabled=True,
            is_secure_site_enabled=True
        )
