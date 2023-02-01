
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase


class QuestionAnsweringTestCase(AzureRecordedTestCase):

    @property
    def kwargs_for_polling(self):
        if self.is_playback:
            return {"polling_interval": 0}
        return {}
